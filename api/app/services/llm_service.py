import logging
from pathlib import Path

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate

from app.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        # Initialize Local LLM using Ollama
        # This keeps data completely local and private
        try:
            self.llm = Ollama(
                base_url=settings.OLLAMA_HOST,
                model=settings.LLM_MODEL,
                temperature=0.1
            )
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM: {e}")
            raise e

        # Create a prompt template instructing the LLM to strictly use the context
        self.prompt = ChatPromptTemplate.from_template("""
        You are a helpful, privacy-first AI assistant. Use the following pieces of retrieved context to answer the user's question. 
        If you don't know the answer or if the answer is not contained within the context, just say that you don't know. Do not try to make up an answer.
        Keep the answer concise, accurate, and strictly based on the provided context.

        Context: {context}
        
        Question: {input}
        
        Answer:
        """)

    def generate_response(self, query: str) -> str:
        """
        1. Checks ChromaDB has documents.
        2. Retrieves top-k diverse chunks via MMR.
        3. Formats each chunk with [File | Page] header.
        4. Passes formatted context to LLM prompt and returns the answer.
        """
        try:
            # Guard: don't call LLM if no documents are indexed yet
            stats = rag_service.get_collection_stats()
            if stats.get("total_chunks", 0) == 0:
                return (
                    "No documents are currently indexed. "
                    "Please upload a PDF first and wait for ingestion to complete."
                )

            # Retrieve diverse chunks using MMR
            retriever = rag_service.get_retriever(
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 12}
            )
            docs = retriever.invoke(query)

            if not docs:
                return "No relevant content found in the uploaded documents for your question."

            # Format each chunk with clear source attribution
            formatted_chunks = []
            for doc in docs:
                src_path = doc.metadata.get("source", "")
                filename = doc.metadata.get("filename") or Path(src_path).name or "Document"
                # PyPDFLoader uses 0-based page index; convert to 1-based for display
                page_raw = doc.metadata.get("page", 0)
                page = (page_raw + 1) if isinstance(page_raw, int) else page_raw
                content = doc.page_content.strip()
                formatted_chunks.append(f"[File: {filename} | Page {page}]\n{content}")

            formatted_context = "\n\n---\n\n".join(formatted_chunks)

            # Run the prompt | LLM chain
            chain = self.prompt | self.llm
            response = chain.invoke({"context": formatted_context, "input": query})
            return str(response).strip() if response else "Could not generate an answer."

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return (
                "There was an error generating the response. "
                "Please ensure Ollama is running and at least one document is ingested."
            )


# Singleton instance to be used by the chat endpoint
llm_service = LLMService()
