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

            return True
        except Exception as e:
            logger.error(f"Error during document ingestion: {e}")
            raise e

    def get_retriever(self, search_type: str = "mmr", search_kwargs: dict = None):
        """
        Returns a retriever for the vector store.
        Defaults to MMR (Maximal Marginal Relevance) — fetches k=5 diverse chunks
        from a candidate pool of fetch_k=12, avoiding redundant/duplicate content.
        """
        if search_kwargs is None:
            search_kwargs = {"k": 5, "fetch_k": 12}
        return self.vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )


# Singleton instance to be used across the app
rag_service = RAGService()
