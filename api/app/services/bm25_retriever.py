"""
Custom BM25 retriever using the rank_bm25 library.

Replaces the deprecated langchain-community BM25Retriever with a direct
implementation that wraps rank_bm25.BM25Okapi in the LangChain BaseRetriever
interface, so it plugs directly into EnsembleRetriever.

BM25 (Best Matching 25) is a keyword-based ranking function that scores
documents based on term frequency, inverse document frequency, and document
length normalization. It excels at exact keyword matching where embedding-based
semantic search might miss specific terms.
"""

import logging
from typing import Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Retriever(BaseRetriever):
    """
    LangChain-compatible retriever that uses BM25Okapi for keyword-based search.

    Usage:
        retriever = BM25Retriever.from_documents(docs, k=20)
        results = retriever.invoke("search query")
    """

    documents: list[Document] = Field(default_factory=list)
    bm25_index: Any = Field(default=None, exclude=True)
    k: int = Field(default=20, description="Number of documents to retrieve")

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_documents(cls, documents: list[Document], k: int = 20) -> "BM25Retriever":
        """
        Creates a BM25Retriever from a list of LangChain Document objects.
        Tokenizes each document's page_content for BM25 indexing.
        """
        if not documents:
            logger.warning("BM25Retriever initialized with zero documents.")
            return cls(documents=[], bm25_index=None, k=k)

        # Tokenize: lowercase + whitespace split (simple but effective)
        tokenized_corpus = [doc.page_content.lower().split() for doc in documents]

        bm25_index = BM25Okapi(tokenized_corpus)
        logger.info(f"BM25 index built with {len(documents)} documents.")

        return cls(documents=documents, bm25_index=bm25_index, k=k)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """
        Retrieves top-k documents matching the query using BM25 scoring.
        Returns only documents with a positive BM25 score (non-zero relevance).
        """
        if self.bm25_index is None or not self.documents:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)

        # Get indices sorted by score (highest first), take top-k
        top_indices = scores.argsort()[::-1][: self.k]

        # Filter out zero-score documents (no keyword match at all)
        results = [
            self.documents[i] for i in top_indices if scores[i] > 0
        ]

        return results
