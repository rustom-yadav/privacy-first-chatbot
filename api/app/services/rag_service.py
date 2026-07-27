import logging
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.config import settings

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

        self.bm25_retriever = None
        self._init_bm25()

    def _init_bm25(self):
        """
        Loads all existing documents from ChromaDB and initializes the BM25 index.
        """
        try:
            data = self.vector_store.get()
            if data and data.get("documents"):
                from langchain_core.documents import Document
                from langchain_community.retrievers import BM25Retriever

                docs = [
                    Document(page_content=text, metadata=meta)
                    for text, meta in zip(data["documents"], data["metadatas"])
                ]
                self.bm25_retriever = BM25Retriever.from_documents(docs)
                logger.info(f"Initialized BM25 Retriever with {len(docs)} documents.")
            else:
                self.bm25_retriever = None
        except Exception as e:
            logger.error(f"Error initializing BM25: {e}")
            self.bm25_retriever = None

    def _delete_existing_chunks(self, filename: str) -> None:
        """
        Deletes all existing chunks for a given filename from ChromaDB.
        Prevents duplicate entries when a file is re-uploaded.
        """
        try:
            self.vector_store._collection.delete(where={"filename": filename})
            logger.info(f"Cleared old vectors for: {filename}")
        except Exception as e:
            # Non-fatal: log and continue. First-time ingestion won't have old chunks.
            logger.warning(f"Could not clear old vectors for {filename}: {e}")

    def ingest_document(self, file_path: Path) -> bool:
        """
        Loads a PDF, normalizes path + metadata, deduplicates old chunks,
        splits into chunks, and stores embeddings in ChromaDB.
        """

        try:
            # Normalize to absolute path — works for both API calls and direct/test calls
            resolved_path = file_path.resolve()
            logger.info(f"Starting ingestion for: {resolved_path}")

            # 1. Load the document
            loader = PyPDFLoader(str(resolved_path))
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {resolved_path.name}")

            if not documents:
                logger.warning(f"No text extracted from {resolved_path.name}")
                return False

            for doc in documents:
                doc.metadata["source"] = str(resolved_path)
                doc.metadata["filename"] = resolved_path.name

            self._delete_existing_chunks(resolved_path.name)

            # 4. Split the document into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")

            # 5. Embed and persist to ChromaDB
            self.vector_store.add_documents(chunks)
            logger.info(
                f"Successfully ingested {resolved_path.name} ({len(chunks)} chunks)"
            )
            
            # Rebuild BM25 index with new documents
            self._init_bm25()

            return True
        except Exception as e:
            logger.error(f"Error during document ingestion: {e}")
            raise e

    def get_similarity_retriever(self, k: int = None):
        """
        Returns a retriever that uses pure cosine-similarity search.
        Best for finding the most semantically relevant chunks.
        """
        k = k or settings.RETRIEVER_K
        return self.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": k}
        )

    def get_mmr_retriever(self, k: int = None, fetch_k: int = None, lambda_mult: float = 0.5):
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

    def get_retriever(self, search_type: str = "similarity", search_kwargs: dict = None):
        """
        Generic retriever factory — kept for backward compatibility.
        Prefer get_similarity_retriever() or get_mmr_retriever() for clarity.
        """
        if search_kwargs is None:
            search_kwargs = {"k": settings.RETRIEVER_K}
        return self.vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )


# Singleton instance to be used across the app
rag_service = RAGService()
