from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """Retrieve chunks, build prompt with numbered citations, and call llm_fn."""
        # 1. Kiểm tra kho rỗng
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy thông tin trong cơ sở dữ liệu."

        # 2. Truy xuất top-k chunks
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu."

        # 3. Dựng ngữ cảnh kèm đánh số [1], [2], [3] (Source Traceability)
        context_blocks = []
        for i, doc in enumerate(results, 1):
            source_id = doc.get("metadata", {}).get("doc_id", doc.get("id", "unknown"))
            context_blocks.append(f"[{i}] (Nguồn: {source_id}):\n{doc.get('content', '')}")

        context_str = "\n\n".join(context_blocks)

        # 4. Tạo prompt chặt chẽ chống bịa đặt
        prompt = (
            "Bạn là một trợ lý giải đáp chính sách. Hãy trả lời câu hỏi dưới đây CHỈ DỰA TRÊN "
            "ngữ cảnh được cung cấp. Luôn trích dẫn nguồn dạng [1], [2] ở các câu khẳng định. "
            "Nếu thông tin không xuất hiện trong ngữ cảnh, hãy nói rõ là không tìm thấy.\n\n"
            f"--- NGỮ CẢNH ---\n{context_str}\n\n"
            f"--- CÂU HỎI ---\n{question}\n\n"
            "--- TRẢ LỜI ---"
        )

        # 5. Gọi LLM
        return self.llm_fn(prompt)