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
        # Initialize Embeddings
        # We use HuggingFace local embeddings to ensure privacy
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        
        # Initialize Chroma Vector Store
        self.vector_store = Chroma(
            collection_name="privacy_chat_docs",
            embedding_function=self.embeddings,
            persist_directory=str(settings.CHROMA_DB_DIR)
        )
        
        # Initialize Text Splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def ingest_document(self, file_path: Path) -> bool:
        """
        Loads a PDF, splits it into chunks, and stores the embeddings in ChromaDB.
        """
        try:
            logger.info(f"Starting ingestion for: {file_path}")
            
            # 1. Load the document
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path.name}")
            
            # 2. Split the document into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # 3. Add chunks to the vector store
            # Chroma will automatically calculate embeddings and persist to disk
            self.vector_store.add_documents(chunks)
            logger.info(f"Successfully ingested {file_path.name} into ChromaDB")
            
            return True
        except Exception as e:
            logger.error(f"Error during document ingestion: {e}")
            raise e

    def get_retriever(self, search_kwargs={"k": 4}):
        """
        Returns a retriever interface for the vector store.
        """
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

# Singleton instance to be used across the app
rag_service = RAGService()
