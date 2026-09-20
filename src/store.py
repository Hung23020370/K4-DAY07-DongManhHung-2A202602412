from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Always uses an in-memory store for predictable test outcomes.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Build a normalized stored record for one document.
        Copies metadata safely and ensures doc_id key is present.
        """
        meta = dict(doc.metadata) if doc.metadata else {}
        
        # doc_id trỏ về id tài liệu gốc (phục vụ delete_document)
        if "doc_id" not in meta:
            meta["doc_id"] = doc.id.split("#")[0] if "#" in doc.id else doc.id

        embedding = self._embedding_fn(doc.content)

        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": meta,
            "embedding": embedding,
        }

    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        """
        Run in-memory similarity search over provided records.
        Removes heavy embedding vectors from returned dicts.
        """
        if not records or top_k <= 0:
            return []

        query_vec = self._embedding_fn(query)
        scored: list[tuple[float, dict[str, Any]]] = []

        for r in records:
            score = _dot(query_vec, r["embedding"])
            scored.append((score, r))

        # Sắp xếp theo độ tương đồng giảm dần
        scored.sort(key=lambda item: item[0], reverse=True)
        selected = scored[:top_k]

        results = []
        for score, r in selected:
            # Tạo bản sao output loại bỏ embedding vector
            record_copy = {
                "id": r["id"],
                "content": r["content"],
                "metadata": dict(r["metadata"]),
                "score": score,
            }
            results.append(record_copy)

        return results

    def add_documents(self, docs: list[Document]) -> None:
        """Embed each document's content and store it in-memory."""
        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Find the top_k most similar documents to query."""
        return self._search_records(query, self._store, top_k=top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(
        self, query: str, top_k: int = 3, metadata_filter: dict | None = None
    ) -> list[dict[str, Any]]:
        """
        Search with pre-filtering:
        Filters candidate pool first before selecting top-k.
        """
        if not metadata_filter:
            return self._search_records(query, self._store, top_k=top_k)

        # Lọc trước (Pre-filtering)
        candidates = []
        for record in self._store:
            record_meta = record.get("metadata", {})
            matches = True
            for k, v in metadata_filter.items():
                if record_meta.get(k) != v:
                    matches = False
                    break
            if matches:
                candidates.append(record)

        return self._search_records(query, candidates, top_k=top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.
        Returns True if any chunks were removed, False otherwise.
        """
        initial_len = len(self._store)
        self._store = [
            r for r in self._store if r.get("metadata", {}).get("doc_id") != doc_id
        ]
        return len(self._store) < initial_len