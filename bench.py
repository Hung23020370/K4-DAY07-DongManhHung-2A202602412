import csv
import re
from pathlib import Path
from src.models import Document
from src.store import EmbeddingStore
from src.chunking import (
    FixedSizeChunker,
    SentenceChunker,
    RecursiveChunker,
    HeadingChunker,
)

# ==========================================
# 1. CẤU HÌNH CHIẾN LƯỢC CỦA BẠN TẠI ĐÂY
# ==========================================
# chunker = FixedSizeChunker(chunk_size=400, overlap=50)
# chunker = SentenceChunker(max_sentences_per_chunk=3)
# chunker = RecursiveChunker(chunk_size=400)
chunker = HeadingChunker(chunk_size=400)

DATA_DIR = Path("data/tra-hang-hoan-tien")
OUTPUT_FILE = Path("ket_qua_benchmark.txt")

# ==========================================
# 2. DANH SÁCH BENCHMARK QUERIES MỚI
# ==========================================
QUERIES = [
    {
        "id": "Q1",
        "question": "Người mua có bao lâu để yêu cầu trả hàng/hoàn tiền sau khi đơn giao thành công?",
        "filter": {"audience": "buyer"},
        "gold_answer": "Thông thường trong vòng 15 ngày; với thực phẩm tươi sống và đông lạnh là 24 giờ.",
        "gold_doc_ids": ["shopee-buyer-chinh-sach-tra-hang", "shopee-buyer-quy-dinh-chung-tra-hang", "tiktok-chinh-sach-huy-tra-hoan-tien"],
        "gold_keywords": ["15 ngày", "24 giờ", "mười lăm ngày"],
        "test_ab": True,
    },
    {
        "id": "Q2",
        "question": "Người mua cần làm gì để gửi yêu cầu trả hàng hoặc hoàn tiền trên Shopee?",
        "filter": {"audience": "buyer"},
        "gold_answer": "Gửi yêu cầu trong ứng dụng Shopee, chọn đơn/lý do, cung cấp bằng chứng theo hướng dẫn và gửi yêu cầu.",
        "gold_doc_ids": ["shopee-buyer-chinh-sach-tra-hang", "shopee-buyer-quy-dinh-chung-tra-hang"],
        "gold_keywords": ["ứng dụng shopee", "chọn đơn", "bằng chứng", "gửi yêu cầu"],
        "test_ab": False,
    },
    {
        "id": "Q3",
        "question": "Trong trường hợp được hoàn tiền ngay, cần làm gì nếu không đồng ý với quyết định?",
        "filter": {"audience": "seller"},
        "gold_answer": "Người bán cần khiếu nại kèm bằng chứng trong vòng 2 ngày kể từ thông báo hoàn tiền ngay.",
        "gold_doc_ids": ["tiktok-seller-quy-trinh-xet-duyet-tra-hang", "tiktok-seller-khieu-nai-khang-cao"],
        "gold_keywords": ["khiếu nại", "2 ngày", "bằng chứng", "hoàn tiền ngay"],
        "test_ab": False,
    },
    {
        "id": "Q4",
        "question": "Chính sách nào áp dụng cho sản phẩm thuộc Shopee Mall khi yêu cầu trả hàng/hoàn tiền?",
        "filter": {"audience": "buyer"},
        "gold_answer": "Sản phẩm Shopee Mall được áp dụng quy định trả hàng/hoàn tiền dành riêng cho Shopee Mall theo Điều khoản Dịch vụ Shopee Mall.",
        "evidence": "Chính Sách Trả Hàng và Hoàn Tiền cho sản phẩm thuộc Shopee Mall được quy định tại Điều Khoản Dịch Vụ Shopee Mall.",
        "gold_doc_ids": ["shopee-buyer-chinh-sach-tra-hang", "shopee-buyer-quy-dinh-chung-tra-hang"],
        "gold_keywords": ["shopee mall", "điều khoản dịch vụ shopee mall"],
        "test_ab": False,
    },
    {
        "id": "Q5",
        "question": "Điều kiện nào cần đáp ứng để sản phẩm được bảo hành miễn phí?",
        "filter": {"audience": "buyer"},
        "gold_answer": "Sản phẩm bị lỗi kỹ thuật do nhà sản xuất, còn trong thời hạn bảo hành, có hóa đơn điện tử khi yêu cầu hoặc mã đơn hàng; với đồ điện gia dụng, tem/phiếu bảo hành và tem niêm phong cần nguyên vẹn theo yêu cầu hãng.",
        "evidence": "Sản phẩm bị lỗi kỹ thuật do nhà sản xuất",
        "gold_doc_ids": ["tiki-buyer-chinh-sach-doi-tra", "shopee-buyer-chinh-sach-tra-hang"],
        "gold_keywords": ["lỗi kỹ thuật do nhà sản xuất", "thời hạn bảo hành", "tem niêm phong"],
        "test_ab": False,
    },
]

def load_documents_and_chunk(data_dir: Path, selected_chunker) -> list[Document]:
    documents = []
    for md_file in sorted(data_dir.glob("*.md")):
        raw_text = md_file.read_text(encoding="utf-8")
        parts = raw_text.split("---", 2)
        if len(parts) >= 3:
            fm_text, body_text = parts[1], parts[2]
            meta = dict(re.findall(r"^(\w+):\s*(.+)$", fm_text, re.M))
            meta = {k: v.strip("\"' ") for k, v in meta.items()}
        else:
            meta = {}
            body_text = raw_text

        meta["doc_id"] = md_file.stem
        chunks = selected_chunker.chunk(body_text)
        for i, ch in enumerate(chunks):
            documents.append(Document(
                id=f"{md_file.stem}#{i}",
                content=ch,
                metadata=dict(meta)
            ))
    return documents

def evaluate_retrieval(hits: list[dict], gold_docs: list[str], gold_keywords: list[str]):
    for rank, h in enumerate(hits, 1):
        doc_id = h.get("metadata", {}).get("doc_id", "")
        content = h.get("content", "").lower()

        is_gold_doc = doc_id in gold_docs
        has_gold_kw = any(kw.lower() in content for kw in gold_keywords)

        if is_gold_doc and has_gold_kw:
            return (2 if rank == 1 else 1), rank, doc_id, True

    for rank, h in enumerate(hits, 1):
        doc_id = h.get("metadata", {}).get("doc_id", "")
        if doc_id in gold_docs:
            return 0, rank, doc_id, False

    return 0, -1, "None", False

def main():
    lines = []
    strategy_name = chunker.__class__.__name__
    lines.append("============================================================")
    lines.append(f"BENCHMARK REPORT - STRATEGY: {strategy_name}")
    lines.append("============================================================\n")

    docs = load_documents_and_chunk(DATA_DIR, chunker)
    store = EmbeddingStore()
    store.add_documents(docs)

    chunk_lengths = [len(d.content) for d in docs]
    avg_len = round(sum(chunk_lengths) / len(chunk_lengths), 2) if chunk_lengths else 0
    lines.append(f"Tong so chunks nap: {len(docs)}")
    lines.append(f"Do dai trung binh: {avg_len} ky tu\n")

    total_score = 0

    lines.append("--- 1. DANH GIA 5 BENCHMARK QUERIES ---")
    for q_item in QUERIES:
        query_text = q_item["question"]
        meta_filter = q_item.get("filter")
        
        hits = store.search_with_filter(
            query=query_text,
            top_k=3,
            metadata_filter=meta_filter
        )

        score, rank, hit_doc, has_content = evaluate_retrieval(
            hits, q_item.get("gold_doc_ids", []), q_item.get("gold_keywords", [])
        )
        total_score += score

        lines.append(f"\n[{q_item['id']}] {query_text}")
        lines.append(f"  Filter: {meta_filter} | Score dat duoc: {score}/2")
        lines.append(f"  Ket luan: Gold Doc o rank {rank} ({hit_doc}) | Dung noi dung chuoi: {has_content}")
        for r, h in enumerate(hits, 1):
            d_id = h.get("metadata", {}).get("doc_id", "N/A")
            c_id = h.get("id")
            s = round(h.get("score", 0.0), 4)
            preview = h.get("content", "").replace("\n", " ")[:80]
            lines.append(f"    Top {r}: [{s}] {c_id} (doc: {d_id}) -> \"{preview}...\"")

    lines.append(f"\n=> TONG DIEM RETRIEVAL: {total_score}/10\n")

    lines.append("--- 2. KET QUA A/B TEST (METADATA FILTERING TREN Q1) ---")
    q1 = QUERIES[0]

    hits_with_filter = store.search_with_filter(q1["question"], top_k=3, metadata_filter=q1["filter"])
    hits_no_filter = store.search_with_filter(q1["question"], top_k=3, metadata_filter=None)

    lines.append(f"Query: \"{q1['question']}\"")
    lines.append("\n[Lan A - CO FILTER (audience: buyer)]:")
    for r, h in enumerate(hits_with_filter, 1):
        lines.append(f"  Top {r}: {h.get('id')} (audience: {h.get('metadata', {}).get('audience')})")

    lines.append("\n[Lan B - KHONG FILTER]:")
    for r, h in enumerate(hits_no_filter, 1):
        lines.append(f"  Top {r}: {h.get('id')} (audience: {h.get('metadata', {}).get('audience')})")

    report_text = "\n".join(lines)
    print(report_text)
    OUTPUT_FILE.write_text(report_text, encoding="utf-8")
    print(f"\n-> Da ghi toan bo ket qua vao: {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    main()