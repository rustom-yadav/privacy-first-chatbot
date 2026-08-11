"""
RAG (Retrieval-Augmented Generation) Service.

Manages the document ingestion pipeline and vector store operations:
- PDF loading, chunking, and embedding into ChromaDB
- BM25 keyword index (using rank_bm25 via custom retriever)
- Similarity and MMR retriever factories for the ensemble pipeline
- Document listing and deletion for management endpoints

A version counter (_docs_version) is incremented on every ingestion/deletion
so that LLMService can cache and invalidate its EnsembleRetriever efficiently.
"""

import logging
from pathlib import Path

import pypdf
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.exceptions import DocumentIngestionError, DocumentNotFoundError
from app.services.bm25_retriever import BM25Retriever

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

        self.vector_store = Chroma(
            collection_name="privacy_chat_docs",
            embedding_function=self.embeddings,
            persist_directory=str(settings.CHROMA_DB_DIR),
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )

        self.bm25_retriever: BM25Retriever | None = None
        self._docs_version: int = 0  # Incremented on ingest/delete for cache invalidation
        self._init_bm25()

    # ── BM25 Index Management ────────────────────────────────────────

    def _init_bm25(self) -> None:
        """
        Loads all existing documents from ChromaDB and builds the BM25 index.
        Called on startup and after every ingestion/deletion.
        """
        try:
            data = self.vector_store.get()
            if data and data.get("documents"):
                docs = [
                    Document(page_content=text, metadata=meta)
                    for text, meta in zip(data["documents"], data["metadatas"])
                ]
                self.bm25_retriever = BM25Retriever.from_documents(
                    docs, k=settings.RETRIEVER_K
                )
                logger.info(f"BM25 index built with {len(docs)} chunks.")
            else:
                self.bm25_retriever = None
                logger.info("BM25 index: no documents found.")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error initializing BM25: {e}")
            self.bm25_retriever = None

    # ── Document Ingestion ───────────────────────────────────────────

    def _delete_existing_chunks(self, filename: str) -> None:
        """
        Deletes all existing chunks for a given filename from ChromaDB.
        Prevents duplicate entries when a file is re-uploaded.
        """
        try:
            self.vector_store._collection.delete(where={"filename": filename})
            logger.info(f"Cleared old vectors for: {filename}")
        except Exception as e:  # noqa: BLE001
            # Non-fatal: log and continue. First-time ingestion won't have old chunks.
            logger.warning(f"Could not clear old vectors for {filename}: {e}")

    def ingest_document(self, file_path: Path) -> int:
        """
        Loads a PDF, normalizes path + metadata, deduplicates old chunks,
        splits into chunks, and stores embeddings in ChromaDB.

        Returns:
            Number of chunks created.

        Raises:
            DocumentIngestionError: If ingestion fails at any step.
        """
        try:
            # Normalize to absolute path
            resolved_path = file_path.resolve()
            logger.info(f"Starting ingestion for: {resolved_path}")

            # 1. Load the document using pypdf directly
            reader = pypdf.PdfReader(resolved_path)
            documents = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": str(resolved_path),
                                "filename": resolved_path.name,
                                "page": page_num,
                            },
                        )
                    )

            logger.info(f"Loaded {len(documents)} pages from {resolved_path.name}")

            if not documents:
                raise DocumentIngestionError(
                    f"No text could be extracted from {resolved_path.name}"
                )

            # 2. Remove old chunks (prevents duplicates on re-upload)
            self._delete_existing_chunks(resolved_path.name)

            # 4. Split the document into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")

            # 5. Embed and persist to ChromaDB
            self.vector_store.add_documents(chunks)
            logger.info(
                f"Successfully ingested {resolved_path.name} ({len(chunks)} chunks)"
            )

            # 6. Rebuild BM25 index and bump version
            self._init_bm25()
            self._docs_version += 1

            return len(chunks)

        except DocumentIngestionError:
            raise
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error during document ingestion: {e}")
            raise DocumentIngestionError(
                f"Failed to ingest {file_path.name}: {e!s}"
            )

    # ── Document Management ──────────────────────────────────────────

    def list_documents(self) -> list[dict]:
        """
        Returns a list of all ingested documents with their chunk counts.
        Queries ChromaDB metadata to aggregate by filename.
        """
        try:
            data = self.vector_store.get()
            if not data or not data.get("metadatas"):
                return []

            # Aggregate chunk counts by filename
            file_counts: dict[str, int] = {}
            for meta in data["metadatas"]:
                filename = meta.get("filename", "Unknown")
                file_counts[filename] = file_counts.get(filename, 0) + 1

            return [
                {"filename": name, "chunk_count": count}
                for name, count in sorted(file_counts.items())
            ]
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error listing documents: {e}")
            return []

    def delete_document(self, filename: str) -> bool:
        """
        Deletes all chunks for a document from ChromaDB and removes the file from disk.

        Raises:
            DocumentNotFoundError: If no chunks exist for the filename.
        """
        # Check if document exists in ChromaDB
        data = self.vector_store.get(where={"filename": filename})
        if not data or not data.get("documents"):
            raise DocumentNotFoundError(f"No document found with name: {filename}")

        # Delete vectors from ChromaDB
        self._delete_existing_chunks(filename)

        # Delete file from disk (if it exists)
        file_path = settings.UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file from disk: {filename}")

        # Rebuild BM25 and bump version
        self._init_bm25()
        self._docs_version += 1

        logger.info(f"Document fully deleted: {filename}")
        return True

    # ── Retriever Factories ──────────────────────────────────────────

    def get_similarity_retriever(self, k: int | None = None):
        """
        Returns a retriever that uses pure cosine-similarity search.
        Best for finding the most semantically relevant chunks.
        """
        k = k or settings.RETRIEVER_K
        return self.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": k}
        )

    def get_mmr_retriever(
        self,
        k: int | None = None,
        fetch_k: int | None = None,
        lambda_mult: float = 0.5,
    ):
        """
        Returns a retriever that uses Maximal Marginal Relevance (MMR).
        Balances relevance with diversity — avoids returning near-duplicate chunks.

        Args:
            k: Number of final chunks to return.
            fetch_k: Number of candidates to fetch before MMR re-ranking (should be > k).
            lambda_mult: Diversity factor (0 = max diversity, 1 = max relevance).
        """
        k = k or settings.RETRIEVER_K
        fetch_k = fetch_k or (k * 2)
        return self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult},
        )


# Singleton instance to be used across the app
rag_service = RAGService()
