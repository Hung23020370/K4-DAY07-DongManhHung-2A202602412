# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đồng Mạnh Hùng
**Nhóm:** 4aesieunhan
**Ngày:** 20/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Độ tương tự cosine cao phản ảnh ai đoạn văn bản có sự tương đồng lớn về mặt ngữ nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: Khách hàng có thể yêu cầu trả hàng và hoàn tiền trong vòng 15 ngày.
- Câu B: Thời hạn để người mua gửi yêu cầu hoàn tiền hoặc trả lại hàng là mười lăm ngày.
- Tại sao tương đồng: Cả hai câu sử dụng từ ngữ và cách diễn đạt khác nhau nhưng đều truyền tải chính xác cùng một quy định và thời hạn trả hàng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Hôm nay trời nắng.
- Câu B: Tôi mệt
- Tại sao khác: Hai câu này chủ đề khác nhau nên độ tương tự thấp

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity chỉ đo góc giữa các vector mà bỏ qua độ dài (magnitude), giúp triệt tiêu ảnh hưởng của độ dài văn bản đến kết quả so khớp. Trong khi đó, khoảng cách Euclid bị ảnh hưởng bởi độ dài vector, dễ khiến hai đoạn văn bản cùng chủ đề nhưng khác độ dài bị đánh giá là xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* chunk đầu 500 kí tự, các chunk sau do overlap nên chỉ có 450 kí tự. Số ký tự còn lại cần phân tách cho các chunk sau là 9500. Số chunks là [9500/450] +1 = 23.
> *Đáp án:* 23

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Khi overlap tăng từ 50 lên 100, số chunks là 25. Người ta muốn tăng overlap để giảm thiểu hiện tượng đứt gãy ngữ cảnh tại ranh giới cắt, giúp các thực thể hoặc câu văn quan trọng nằm ở mép chunk không bị chia cắt làm mất ý nghĩa khi đưa vào mô hình embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
Dùng biểu thức chính quy với positive lookbehind (?<=[.!?])\s+ để tách câu sau các dấu ., !, ? mà vẫn bảo toàn nguyên vẹn dấu câu ở cuối câu trước. Edge case được xử lý triệt để: loại bỏ khoảng trắng rác bằng điều kiện not text or not text.strip() ngay đầu hàm, và dùng list comprehension để lọc bỏ các chuỗi rỗng trước khi gom nhóm theo max_sentences_per_chunk.
**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
Thuật toán hoạt động theo cơ chế chia để trị (divide-and-conquer), ưu tiên cắt theo cấu trúc lớn giảm dần: đoạn văn (\n\n), dòng đơn (\n), câu (. ), từ ( ) và ký tự (""). Trường hợp cơ sở (base case) xảy ra khi độ dài đoạn văn bản đã $\le$ chunk_size hoặc khi đã duyệt hết danh sách separators thì cắt cứng theo ký tự; các đoạn con nhỏ sau đó được gộp lại tối đa cho tới khi chạm ngưỡng chunk_size để tránh làm vỡ vụn nội dung.
### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
Lưu trữ in-memory dưới dạng danh sách các từ điển (list of dicts), mỗi phần tử chứa id, content, bản sao metadata (đảm bảo luôn có khóa doc_id) và vector nhúng sinh bởi _embedding_fn. Khi thực hiện search, hàm tính tích vô hướng (dot product) giữa embedding của câu truy vấn và tất cả record trong store, sắp xếp giảm dần và cắt lấy top_k, đồng thời loại bỏ trường vector nhúng ở kết quả đầu ra để tránh làm nặng bộ nhớ.
**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
Áp dụng cơ chế tiền lọc (pre-filtering): duyệt và chọn lọc các record khớp toàn bộ cặp key-value trong metadata_filter trước, sau đó mới đưa tập ứng viên hợp lệ vào hàm _search_records để tránh tình trạng top-$k$ bị chiếm bởi tài liệu sai đối tượng. Hàm delete_document thực hiện lọc bỏ tất cả record có metadata['doc_id'] == doc_id và so sánh độ dài danh sách trước/sau để trả về True nếu có chunk bị xóa, ngược lại trả về False.
### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
Cấu trúc prompt được thiết kế theo 3 khối rõ ràng: Chỉ dẫn tác tử (System Instruction), Ngữ cảnh trích xuất (Context) và Câu hỏi người dùng (Question). Ngữ cảnh được đưa vào bằng cách đánh số thứ tự [1], [2], [3] kèm mã nguồn doc_id của từng chunk nhằm đảm bảo khả năng truy vết nguồn gốc (Source Traceability), đồng thời đặt ràng buộc chống bịa đặt (hallucination) và xử lý sớm trường hợp store rỗng để tránh gọi LLM vô ích.
---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|:---:|---|---|:---:|:---:|:---:|
| 1 | Khách hàng có thể yêu cầu trả hàng và hoàn tiền trong 15 ngày. | Thời hạn người mua gửi yêu cầu hoàn tiền là mười lăm ngày. | cao | -0.1080 | Sai |
| 2 | Người bán phải chịu phí vận chuyển chiều về nếu giao sai hàng. | Chi phí ship hoàn trả do shop thanh toán khi gửi nhầm mẫu mã. | cao | -0.0815 | Sai |
| 3 | Thời hạn tối đa để yêu cầu trả hàng và hoàn tiền sau khi giao hàng? | Quy trình cài đặt môi trường Python 3.11 trên hệ điều hành Ubuntu. | thấp | -0.0324 | Đúng |
| 4 | Người mua đổi ý không muốn nhận sản phẩm nữa. | Khách hàng từ chối thanh toán khi shipper giao hàng tận nơi. | cao | -0.1889 | Sai |
| 5 | Hướng dẫn người bán nộp khiếu nại quyết định trả hàng của sàn. | Quy chế xử lý kỷ luật sinh viên vi phạm quy chế thi học kỳ. | thấp | -0.0131 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*
Bất ngờ nhất là Cặp 1 và Cặp 2: dù hai câu hoàn toàn tương đồng về mặt ngữ nghĩa và quy định nghiệp vụ, điểm tương đồng thực tế lại nhận giá trị âm (-0.1080 và -0.0815). Hiện tượng này phản ánh hạn chế cốt lõi của hàm giả lập `_mock_embed` khi dùng thuật toán băm chuỗi (MD5) để sinh vector ngẫu nhiên thay vì học ngữ nghĩa sâu; do đó, các vector không nắm bắt được mối quan hệ từ vựng hay bối cảnh nếu không sử dụng các mô hình Semantic Embedding chuyên dụng.
---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|:---:|:---:|---|
| 1 | Người mua có bao lâu để yêu cầu trả hàng/hoàn tiền sau khi đơn giao thành công? | # Chinh sach huy don hang tra hang va hoan tien tren TikTok Shop Từ chối trả hàn... (`tiktok-chinh-sach-huy-tra-hoan-tien#31`) | 0.3071 | Không (đúng tài liệu nhưng rơi vào mục từ chối trả hàng, không chứa mốc 15 ngày/24 giờ) | Không tìm thấy thông tin cụ thể về thời hạn yêu cầu trả hàng/hoàn tiền trong ngữ cảnh được cung cấp. |
| 2 | Người mua cần làm gì để gửi yêu cầu trả hàng hoặc hoàn tiền trên Shopee? | # CHINH SACH TRA HANG VA HOAN TIEN SHOPEE 6. YÊU CẦU ĐỐI VỚI SẢN PHẨM HOÀN TRẢ... (`shopee-buyer-chinh-sach-tra-hang#43`) | 0.2759 | Không (nêu yêu cầu quy cách sản phẩm hoàn trả, không hướng dẫn thao tác trên app) | Ngữ cảnh không hướng dẫn các bước thao tác trên ứng dụng Shopee để gửi yêu cầu. |
| 3 | Trong trường hợp được hoàn tiền ngay, cần làm gì nếu không đồng ý với quyết định? | # Quy dinh ty le tra hang hoan tien do loi cua Nguoi ban Trả hàng do sản phẩm bị... (`tiktok-seller-ty-le-tra-hang-loi#2`) | 0.3232 | Có (Top-2 chứa đúng thông tin: người bán khiếu nại trong 2 ngày kèm bằng chứng) | Người bán cần gửi khiếu nại kèm bằng chứng trong vòng 2 ngày kể từ khi có thông báo hoàn tiền ngay [2]. |
| 4 | Chính sách nào áp dụng cho sản phẩm thuộc Shopee Mall khi yêu cầu trả hàng/hoàn tiền? | # CHINH SACH TRA HANG VA HOAN TIEN SHOPEE CHÍNH SÁCH TRẢ HÀNG VÀ HOÀN TIỀN \| Sho... (`shopee-buyer-chinh-sach-tra-hang#0`) | 0.2406 | Không (chỉ là phần tiêu đề trang giới thiệu chung, chưa dẫn chiếu tới Điều khoản Dịch vụ Shopee Mall) | Chưa có thông tin chi tiết về điều khoản riêng áp dụng cho Shopee Mall trong ngữ cảnh. |
| 5 | Điều kiện nào cần đáp ứng để sản phẩm được bảo hành miễn phí? | # Chinh sach huy don hang tra hang va hoan tien tren TikTok Shop Vấn đề liên qua... (`tiktok-chinh-sach-huy-tra-hoan-tien#14`) | 0.3189 | Không (chỉ đề cập xử lý lỗi bên TikTok Shop, không nêu điều kiện bảo hành miễn phí) | Không tìm thấy điều kiện bảo hành miễn phí của sản phẩm trong tài liệu được cung cấp. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*
Qua kết quả thực nghiệm với 1/5 câu đạt chuỗi nội dung (Q3 đạt ở Top-2 với điểm 0.2957), tôi nhận thấy việc dùng `HeadingChunker` kết hợp `MockEmbedder` dễ khiến các đoạn tiêu đề mở đầu hoặc mục mang tính cảnh báo chung chiếm trọn Top-1 do trùng từ khóa bề mặt. Bài học lớn nhất là cần bổ sung cơ chế trượt cửa sổ chồng lấn (overlap) giữa các sub-chunk, đồng thời chuyển sang mô hình Semantic Embedding thực tế kết hợp Reranker để kéo đúng đoạn chứa số liệu và hành động cụ thể lên vị trí ưu tiên cao nhất.
---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5/ 5 |
| Hướng tiếp cận của tôi (My Approach) | 10/ 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | /5 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10/ 10 |
| **Tổng phần cá nhân** | **60 / 60** |
