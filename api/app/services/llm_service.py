import logging
from langchain_community.llms import Ollama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
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
        """)

    def generate_response(self, query: str) -> str:
        """
        Takes a user query, retrieves relevant context from Chroma, and generates a response using Ollama.
        """
        try:
            # Get the retriever from rag_service (configured to fetch top 3 most relevant chunks)
            retriever = rag_service.get_retriever(search_kwargs={"k": 5})
            
            # Create a chain that takes a list of documents and formats them into a prompt
            document_chain = create_stuff_documents_chain(self.llm, self.prompt)
            
            # Create the final retrieval chain that combines retriever and document_chain
            retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            # Run the query
            response = retrieval_chain.invoke({"input": query})
            
            # Extract and return just the answer text
            return response.get('answer', "Sorry, I couldn't generate an answer.")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "There was an error generating the response. Please ensure Ollama is running and documents are successfully ingested."

# Singleton instance to be used by the chat endpoint
llm_service = LLMService()
