import logging
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_classic.retrievers import EnsembleRetriever

from app.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class LLMService:
    """
    Privacy-first LLM service with hybrid retrieval pipeline.

    Retrieval Architecture:
        1. Similarity Search  — pure cosine-distance semantic matching
        2. MMR Search         — semantic relevance + diversity (avoids near-duplicate chunks)
        3. BM25 Search        — exact keyword/term matching (catches what embeddings miss)
        4. EnsembleRetriever  — fuses all 3 via Reciprocal Rank Fusion (RRF) with configurable weights

    History Management:
        - Capped at MAX_HISTORY_TURNS (default 10 turns = 20 messages)
        - Auto-trims oldest messages when limit is exceeded
        - clear_history() resets conversation state
    """

    # Ensemble weights: [Similarity, MMR, BM25]
    # Slightly lower BM25 weight since it doesn't understand semantic meaning
    ENSEMBLE_WEIGHTS = [0.35, 0.35, 0.30]

    def __init__(self):
        try:
            self.llm = ChatOllama(
                base_url=settings.OLLAMA_HOST,
                model=settings.LLM_MODEL,
                temperature=0.1,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM: {e}")
            raise

        self.history: list = []

        self.system_instruction = (
            "You are a helpful, privacy-first AI assistant.\n"
            "Use the following pieces of retrieved context to answer the user's question.\n"
            "If you don't know the answer or if the answer is not contained within the context, "
            "just say that you don't know.\n"
            "Do not try to make up an answer.\n"
            "Keep the answer concise, accurate, and strictly based on the provided context."
        )

    # ── Retrieval Pipeline ────────────────────────────────────────────

    def _build_ensemble_retriever(self) -> EnsembleRetriever | None:
        """
        Builds an EnsembleRetriever combining Similarity, MMR, and BM25 retrievers.
        Uses LangChain's built-in Reciprocal Rank Fusion (RRF) for merging results.

        Returns None if no documents are ingested yet.
        """
        k = settings.RETRIEVER_K

        # 1. Similarity Retriever — pure semantic relevance
        similarity_retriever = rag_service.get_similarity_retriever(k=k)

        # 2. MMR Retriever — semantic relevance + diversity
        mmr_retriever = rag_service.get_mmr_retriever(k=k, fetch_k=k * 2, lambda_mult=0.5)

        # 3. BM25 Retriever — keyword/term matching
        bm25_retriever = rag_service.bm25_retriever

        # Build ensemble based on available retrievers
        retrievers = [similarity_retriever, mmr_retriever]
        weights = [self.ENSEMBLE_WEIGHTS[0], self.ENSEMBLE_WEIGHTS[1]]

        if bm25_retriever:
            bm25_retriever.k = k
            retrievers.append(bm25_retriever)
            weights.append(self.ENSEMBLE_WEIGHTS[2])

            # Re-normalize weights to sum to 1.0
            total = sum(weights)
            weights = [w / total for w in weights]

            logger.info(
                f"Ensemble built: Similarity + MMR + BM25 "
                f"(weights: {[round(w, 2) for w in weights]}, k={k})"
            )
        else:
            # No BM25 available — only Similarity + MMR
            total = sum(weights)
            weights = [w / total for w in weights]

            logger.info(
                f"Ensemble built: Similarity + MMR only "
                f"(BM25 unavailable — no documents ingested yet?)"
            )

        return EnsembleRetriever(retrievers=retrievers, weights=weights)

    def _retrieve_context(self, query: str) -> list:
        """
        Retrieves and fuses documents from all retrievers using the ensemble pipeline.

        Returns:
            List of top-N fused Document objects, or empty list if nothing found.
        """
        ensemble = self._build_ensemble_retriever()
        if ensemble is None:
            return []

        try:
            docs = ensemble.invoke(query)

            # Take only top-N results from the fused output
            top_n = settings.ENSEMBLE_TOP_N
            docs = docs[:top_n]

            logger.info(f"Retrieved {len(docs)} chunks after ensemble fusion (top_n={top_n})")
            return docs
        except Exception as e:
            logger.error(f"Error during ensemble retrieval: {e}")
            return []

    @staticmethod
    def _format_chunks(docs: list) -> str:
        """
        Formats retrieved document chunks with clear source attribution.
        Each chunk gets a [File | Page] header for traceability.
        """
        formatted_chunks = []
        for doc in docs:
            src_path = doc.metadata.get("source", "")
            filename = doc.metadata.get("filename") or Path(src_path).name or "Document"
            page_raw = doc.metadata.get("page", 0)
            page = (page_raw + 1) if isinstance(page_raw, int) else page_raw
            content = doc.page_content.strip()
            formatted_chunks.append(f"[File: {filename} | Page {page}]\n{content}")

        return "\n\n---\n\n".join(formatted_chunks)

    # ── History Management ────────────────────────────────────────────

    def _trim_history(self) -> None:
        """
        Keeps history within MAX_HISTORY_TURNS limit.
        Each turn = 1 HumanMessage + 1 AIMessage = 2 messages.
        Trims from the front (oldest messages removed first).
        """
        max_messages = settings.MAX_HISTORY_TURNS * 2
        if len(self.history) > max_messages:
            trimmed_count = len(self.history) - max_messages
            self.history = self.history[-max_messages:]
            logger.info(
                f"History trimmed: removed {trimmed_count} oldest messages, "
                f"keeping last {settings.MAX_HISTORY_TURNS} turns"
            )

    def clear_history(self) -> None:
        """Resets conversation history to empty state."""
        self.history.clear()
        logger.info("Conversation history cleared")

    # ── Main Response Generation ──────────────────────────────────────

    def generate_response(self, query: str) -> str:
        """
        Full RAG pipeline:
            1. Retrieves chunks via EnsembleRetriever (Similarity + MMR + BM25 → RRF fusion)
            2. Formats chunks with source attribution
            3. Builds prompt with system instruction + context + history + query
            4. Invokes local LLM (ChatOllama)
            5. Appends to history and trims if needed
        """
        try:
            # Stage 1: Retrieve context via ensemble pipeline
            docs = self._retrieve_context(query)

            if not docs:
                return "No relevant content found in the uploaded documents for your question."

            # Stage 2: Format chunks with source headers
            formatted_context = self._format_chunks(docs)

            # Stage 3: Build message chain
            messages = [
                SystemMessage(
                    content=f"{self.system_instruction}\n\nContext:\n{formatted_context}"
                )
            ]

            # Add conversation history (already trimmed)
            messages.extend(self.history)

            # Add current user query
            human_msg = HumanMessage(content=query)
            messages.append(human_msg)

            # Stage 4: Invoke LLM
            response = self.llm.invoke(messages)

            # Stage 5: Update history and trim
            self.history.append(human_msg)
            self.history.append(response)
            self._trim_history()

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
