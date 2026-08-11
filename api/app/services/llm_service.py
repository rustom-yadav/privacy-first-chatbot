"""
LLM Service — Core RAG response generation engine.

Responsibilities:
    1. Builds and caches the EnsembleRetriever (Similarity + MMR + BM25)
    2. Retrieves and formats context chunks with source attribution
    3. Manages per-session history via SessionService (SQLite)
    4. Invokes the local LLM (ChatOllama) and returns answer + sources

The ensemble retriever is cached and only rebuilt when documents change
(tracked via rag_service._docs_version).
"""

import logging
from pathlib import Path

from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.config import settings
from app.exceptions import LLMConnectionError, RetrievalError
from app.services.rag_service import rag_service
from app.services.session_service import session_service

logger = logging.getLogger(__name__)


class LLMService:
    """
    Privacy-first LLM service with hybrid retrieval pipeline.

    Retrieval Architecture:
        1. Similarity Search  — pure cosine-distance semantic matching
        2. MMR Search         — semantic relevance + diversity (avoids near-duplicate chunks)
        3. BM25 Search        — exact keyword/term matching (catches what embeddings miss)
        4. EnsembleRetriever  — fuses all 3 via Reciprocal Rank Fusion (RRF)

    Session Management:
        - Per-session history stored in SQLite (survives server restarts)
        - Capped at MAX_HISTORY_TURNS per session
        - No login required — anonymous session IDs
    """

    # Ensemble weights: [Similarity, MMR, BM25]
    # Slightly lower BM25 weight since it doesn't understand semantic meaning
    ENSEMBLE_WEIGHTS = (0.35, 0.35, 0.30)

    def __init__(self):
        try:
            self.llm = ChatOllama(
                base_url=settings.OLLAMA_HOST,
                model=settings.LLM_MODEL,
                temperature=0.1,
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to initialize Ollama LLM: {e}")
            raise LLMConnectionError(f"Could not connect to Ollama: {e}")

        self.system_instruction = (
            "You are a helpful, privacy-first AI assistant.\n"
            "Use the following pieces of retrieved context to answer the user's question.\n"
            "If you don't know the answer or if the answer is not contained within the context, "
            "just say that you don't know.\n"
            "Do not try to make up an answer.\n"
            "Keep the answer concise, accurate, and strictly based on the provided context."
        )

        # Ensemble cache — rebuilt only when documents change
        self._cached_ensemble: EnsembleRetriever | None = None
        self._cached_docs_version: int = -1

    # ── Retrieval Pipeline ────────────────────────────────────────────

    def _get_ensemble_retriever(self) -> EnsembleRetriever:
        """
        Returns a cached EnsembleRetriever, rebuilding only when documents change.
        Uses rag_service._docs_version to detect changes.
        """
        current_version = rag_service._docs_version

        if current_version != self._cached_docs_version or self._cached_ensemble is None:
            self._cached_ensemble = self._build_ensemble_retriever()
            self._cached_docs_version = current_version
            logger.info(f"Ensemble retriever rebuilt (docs_version={current_version})")

        return self._cached_ensemble

    def _build_ensemble_retriever(self) -> EnsembleRetriever:
        """
        Builds an EnsembleRetriever combining Similarity, MMR, and BM25 retrievers.
        Uses LangChain's built-in Reciprocal Rank Fusion (RRF) for merging results.
        """
        k = settings.RETRIEVER_K

        # 1. Similarity Retriever — pure semantic relevance
        similarity_retriever = rag_service.get_similarity_retriever(k=k)

        # 2. MMR Retriever — semantic relevance + diversity
        mmr_retriever = rag_service.get_mmr_retriever(
            k=k, fetch_k=k * 2, lambda_mult=0.5
        )

        # 3. BM25 Retriever — keyword/term matching
        bm25_retriever = rag_service.bm25_retriever

        # Build ensemble based on available retrievers
        retrievers = [similarity_retriever, mmr_retriever]
        weights = [self.ENSEMBLE_WEIGHTS[0], self.ENSEMBLE_WEIGHTS[1]]

        if bm25_retriever:
            bm25_retriever.k = k
            retrievers.append(bm25_retriever)
            weights.append(self.ENSEMBLE_WEIGHTS[2])

        # Normalize weights to sum to 1.0
        total = sum(weights)
        weights = [w / total for w in weights]

        retriever_names = "Similarity + MMR" + (" + BM25" if bm25_retriever else "")
        logger.info(
            f"Ensemble: {retriever_names} "
            f"(weights={[round(w, 2) for w in weights]}, k={k})"
        )

        return EnsembleRetriever(retrievers=retrievers, weights=weights)

    def _retrieve_context(self, query: str) -> list:
        """
        Retrieves and fuses documents from all retrievers.

        Returns:
            List of top-N fused Document objects, or empty list if nothing found.

        Raises:
            RetrievalError: If the retrieval pipeline fails.
        """
        try:
            ensemble = self._get_ensemble_retriever()
            docs = ensemble.invoke(query)

            # Take only top-N from fused results
            top_n = settings.ENSEMBLE_TOP_N
            docs = docs[:top_n]

            logger.info(f"Retrieved {len(docs)} chunks (top_n={top_n})")
            return docs

        except Exception as e:  # noqa: BLE001
            logger.error(f"Retrieval pipeline error: {e}")
            raise RetrievalError(f"Failed to retrieve context: {e}")

    @staticmethod
    def _format_chunks(docs: list) -> str:
        """
        Formats retrieved document chunks with clear source attribution.
        Each chunk gets a [File | Page] header for traceability.
        """
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

        return "\n\n---\n\n".join(formatted_chunks)

    @staticmethod
    def _extract_sources(docs: list) -> list[dict]:
        """
        Extracts unique source references from retrieved documents.
        Returns a deduplicated list of {filename, page} dicts.
        """
        sources = []
        seen: set[tuple[str, int]] = set()

        for doc in docs:
            src_path = doc.metadata.get("source", "")
            filename = (
                doc.metadata.get("filename") or Path(src_path).name or "Document"
            )
            page_raw = doc.metadata.get("page", 0)
            page = (page_raw + 1) if isinstance(page_raw, int) else page_raw

            key = (filename, page)
            if key not in seen:
                sources.append({"filename": filename, "page": page})
                seen.add(key)

        return sources

    # ── Main Response Generation ──────────────────────────────────────

    def generate_response(
        self, query: str, session_id: str
    ) -> tuple[str, list[dict]]:
        """
        Full RAG pipeline:
            1. Retrieves chunks via EnsembleRetriever (Similarity + MMR + BM25 → RRF)
            2. Formats chunks with source attribution
            3. Loads session history from SQLite
            4. Builds prompt with system instruction + context + history + query
            5. Invokes local LLM (ChatOllama)
            6. Saves the turn to session history
            7. Returns (answer, sources)

        Args:
            query: The user's question.
            session_id: Anonymous session identifier.

        Returns:
            Tuple of (answer_text, sources_list).

        Raises:
            RetrievalError: If context retrieval fails.
            LLMConnectionError: If the LLM call fails.
        """
        # Stage 1: Retrieve context via ensemble pipeline
        docs = self._retrieve_context(query)

        if not docs:
            return (
                "No relevant content found in the uploaded documents for your question.",
                [],
            )

        # Stage 2: Format chunks + extract source references
        formatted_context = self._format_chunks(docs)
        sources = self._extract_sources(docs)

        # Stage 3: Load session history from SQLite
        history = session_service.get_history(session_id)

        # Stage 4: Build message chain
        messages = [
            SystemMessage(
                content=f"{self.system_instruction}\n\nContext:\n{formatted_context}"
            )
        ]
        messages.extend(history)
        messages.append(HumanMessage(content=query))

        # Stage 5: Invoke LLM
        try:
            response = self.llm.invoke(messages)
        except Exception as e:  # noqa: BLE001
            logger.error(f"LLM invocation failed: {e}")
            raise LLMConnectionError(
                "Failed to get response from Ollama. Is it running?"
            )

        answer = (
            response.content.strip()
            if response.content
            else "Could not generate an answer."
        )

        # Stage 6: Save to session history (SQLite)
        session_service.append_to_history(session_id, query, answer)

        return answer, sources


# Singleton instance
llm_service = LLMService()
