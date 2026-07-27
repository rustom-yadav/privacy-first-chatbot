import logging
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        try:
            self.llm = ChatOllama(
                base_url=settings.OLLAMA_HOST, model=settings.LLM_MODEL, temperature=0.1
            )
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM: {e}")
            raise e

        self.history = []
        self.system_instruction = (
            "You are a helpful, privacy-first AI assistant.\n"
            "Use the following pieces of retrieved context to answer the user's question.\n"
            "If you don't know the answer or if the answer is not contained within the context, "
            "just say that you don't know.\n"
            "Do not try to make up an answer.\n"
            "Keep the answer concise, accurate, and strictly based on the provided context."
        )

    def generate_response(self, query: str) -> str:
        """
        1. Checks ChromaDB has documents.
        2. Retrieves top-k diverse chunks via MMR.
        3. Formats each chunk with [File | Page] header.
        4. Passes formatted context to LLM prompt and returns the answer.
        """
        try:
            # Retrieve diverse chunks using MMR
            retriever = rag_service.get_retriever(
                search_type="mmr", search_kwargs={"k": 5, "fetch_k": 12}
            )
            docs = retriever.invoke(query)

            if not docs:
                return "No relevant content found in the uploaded documents for your question."

            # Format each chunk with clear source attribution
            formatted_chunks = []
            for doc in docs:
                src_path = doc.metadata.get("source", "")
                filename = (
                    doc.metadata.get("filename") or Path(src_path).name or "Document"
                )
                page_raw = doc.metadata.get("page", 0)
                page = (page_raw + 1) if isinstance(page_raw, int) else page_raw
                content = doc.page_content.strip()
                formatted_chunks.append(f"[File: {filename} | Page {page}]\n{content}")

            formatted_context = "\n\n---\n\n".join(formatted_chunks)

            messages = [
                SystemMessage(
                    content=f"{self.system_instruction}\n\nContext:\n{formatted_context}"
                )
            ]

            messages.extend(self.history)
            human_msg = HumanMessage(content=query)
            messages.append(human_msg)

            response = self.llm.invoke(messages)

            self.history.append(human_msg)
            self.history.append(response)

            return (
                response.content.strip()
                if response.content
                else "Could not generate an answer."
            )

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return (
                "There was an error generating the response. "
                "Please ensure Ollama is running and at least one document is ingested."
            )


# Singleton instance
llm_service = LLMService()
