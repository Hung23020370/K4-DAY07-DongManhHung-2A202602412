# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** 4aesieunhan
**Thành viên:** Đồng Mạnh Hùng, Nguyễn Gia Khánh, Phạm Khắc Tú
**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách trả hàng hoàn tiền của sàn thương mại điện tử

**Tại sao nhóm chọn chủ đề này?**

Nhóm chọn chủ đề này vì quy trình xử lý trả hàng và hoàn tiền hiện nay thường phức tạp, dễ phát sinh tranh chấp và tiêu tốn nhiều thời gian phân tích thủ công của nhân viên hỗ trợ. Việc ứng dụng AI để tự động hóa trích xuất thông tin từ các yêu cầu khiếu nại và quy chế chính sách sẽ giúp tối ưu hóa quy trình vận hành, từ đó minh bạch hóa quy định và nâng cao đáng kể trải nghiệm người dùng.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|:---:|:---:|---|
| 1 | Chính sách Trả hàng và Hoàn tiền Shopee | <https://help.shopee.vn/portal/4/article/77251-CH%C3%8DNH-S%C3%81CH-TR%E1%BA%A3-H%C3%80NG-V%C3%80-HO%C3%80N-TI%E1%BB%80N> | 2026-09-20 / not-stated | 19,950 | `audience: buyer`, `category: return-refund` |
| 2 | Những quy định chung về Trả hàng và Hoàn tiền | <https://help.shopee.vn/portal/4/article/188931-%5BTr%E1%BA%A3-h%C3%A0ng/Ho%C3%A0n-ti%E1%BB%81n%5D-Nh%E1%BB%AFng-quy-%C4%91%E1%BB%8Bnh-chung-v%E1%BB%81-Tr%E1%BA%A3-h%C3%A0ng/Ho%C3%A0n-ti%E1%BB%81n-c%E1%BB%A7a-Shopee> | 2026-09-20 / not-stated | 6,782 | `audience: buyer`, `category: return-refund` |
| 3 | Chính sách hủy đơn hàng trả hàng và hoàn tiền | <https://seller-vn.tiktok.com/university/essay?knowledge_id=6837773789234946&lang=vi-VN> | 2026-09-20 / not-stated | 12,797 | `audience: buyer`, `category: return-refund` |
| 4 | Quy trình khiếu nại yêu cầu Trả hàng | <https://seller-vn.tiktok.com/university/essay?knowledge_id=5104634859620098> | 2026-09-20 / not-stated | 3,571 | `audience: seller`, `category: dispute-resolution` |
| 5 | Quy định phí vận chuyển trả hàng chiều về | <https://seller-vn.tiktok.com/university/essay?knowledge_id=1398156382422785&lang=vi-VN> | 2026-09-20 / not-stated | 5,338 | `audience: seller`, `category: shipping-fee` |
| 6 | Quản lý yêu cầu trả hàng và hoàn tiền | <https://seller-vn.tiktok.com/university/essay?knowledge_id=6819122768905985> | 2026-09-20 / not-stated | 5,356 | `audience: seller`, `category: return-refund` |
| 7 | Quy trình và thời gian phản hồi yêu cầu | <https://seller-vn.tiktok.com/university/essay?knowledge_id=1766935302801169&lang=vi-VN> | 2026-09-20 / not-stated | 20,438 | `audience: seller`, `category: return-refund` |
| 8 | Quy định tỷ lệ trả hàng hoàn tiền do lỗi Người bán | <https://seller-vn.tiktok.com/university/essay?knowledge_id=89407391336193> | 2026-09-20 / not-stated | 3,215 | `audience: seller`, `category: seller-performance` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|---|:---:|---|---|
| `doc_id` | string | `shopee-buyer-chinh-sach-tra-hang` | Định danh tài liệu gốc; phục vụ thao tác xóa toàn bộ chunk (`delete_document`) và hỗ trợ tính năng trích dẫn nguồn gốc (Source Traceability) cho câu trả lời của Agent[cite: 4, 5]. |
| `audience` | string | `buyer` / `seller` | Cho phép tiền lọc (pre-filtering) để phân tách rạch ròi quy định giữa người mua và người bán, ngăn ngừa ô nhiễm ngữ cảnh khi hai đối tượng dùng chung từ vựng (ví dụ: thời hạn phản hồi vs thời hạn gửi đơn)[cite: 5]. |
| `category` | string | `refund_policy`, `shipping_fee` | Giúp thu hẹp không gian tìm kiếm vào từng nghiệp vụ chuyên biệt (phí vận chuyển, khiếu nại kháng cáo, chính sách đổi ý) trước khi tính toán tương đồng vector. |
| `source_url` | string | `https://help.shopee.vn/...` | Cung cấp đường dẫn tra cứu thực tế để kiểm chứng thông tin hoặc hiển thị nguồn dẫn cho người dùng cuối khi hệ thống hoàn tất trả lời. |
| `document_version` | string | `2026.1` | Quản lý phiên bản văn bản quy định; giúp hệ thống ưu tiên lọc và sử dụng phiên bản chính sách mới nhất, loại bỏ tài liệu cũ đã hết hiệu lực. |
---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `tiktok-chinh-sach-huy-tra-hoan-tien` | SentenceChunker (`by_sentences`) | 28 | 442.64 | Tốt — các điều kiện và ngoại lệ được gom trọn vẹn trong các cụm 3 câu liền kề. |
| `shopee-buyer-chinh-sach-tra-hang` | SentenceChunker (`by_sentences`) | 43 | 405.71 | Tốt — bảo toàn nguyên vẹn ngữ pháp câu văn, điều khoản không bị đứt đoạn vô lý. |
| `shopee-buyer-chinh-sach-tra-hang` | FixedSizeChunker (`500/100`) — Phạm Khắc Tú | 49 | 498.29 | Trung bình — độ dài ổn định và overlap giữ ngữ cảnh ở ranh giới, nhưng vẫn có thể cắt giữa câu. |
| `tiktok-chinh-sach-huy-tra-hoan-tien` | FixedSizeChunker (`500/100`) — Phạm Khắc Tú | 31 | 499.00 | Trung bình — chunk tập trung hơn cấu hình 900/150, đổi lại không bảo toàn ranh giới đề mục/câu. |
| `shopee-buyer-chinh-sach-tra-hang` | RecursiveChunker (`chunk_size=500`) | 62 | 314.45 | Tốt — ưu tiên ranh giới đoạn/câu nên giữ ngữ cảnh tốt hơn cắt cứng, nhưng độ dài chunk không đồng đều. |
| `tiktok-chinh-sach-huy-tra-hoan-tien` | RecursiveChunker (`chunk_size=500`) | 33 | 375.94 | Tốt — tách theo separator tự nhiên trước khi cắt nhỏ, hạn chế chia vỡ điều kiện và ngoại lệ. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Đồng Mạnh Hùng**
- **Loại chiến lược:** Sentence
- **Mô tả & lý do chọn cho chủ đề này:** Tôi chọn `SentenceChunker` với cấu hình gom nhóm 3 câu mỗi chunk (`max_sentences_per_chunk=3`). Đối với văn bản chính sách trả hàng và hoàn tiền, các quy định, điều kiện và mốc thời hạn thường được diễn đạt trọn vẹn trong phạm vi từng câu; việc phân tách theo ranh giới câu giúp bảo toàn hoàn toàn cấu trúc ngữ pháp và tính nguyên vẹn của điều khoản, loại bỏ triệt để hiện tượng câu văn hoặc từ khóa bị cắt đứt gãy nửa chừng như khi dùng `FixedSizeChunker`.

**Thành viên 2 — Phạm Khắc Tú**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=100)`.
- **Mô tả & lý do chọn:** Tôi chia mỗi tài liệu thành các đoạn tối đa 500 ký tự, trong đó hai chunk liên tiếp dùng chung 100 ký tự. Kích thước cố định giúp độ dài đầu vào embedding ổn định, còn overlap 20% hạn chế mất điều kiện hoặc mốc thời gian nằm sát ranh giới. Tôi thử `900/150` trước nhưng cấu hình đó bỏ lỡ điều khoản Shopee Mall ở top-3; với `500/100`, điều khoản này lên top-1 nên tôi chọn cấu hình nhỏ hơn.

**Thành viên 3 — Nguyễn Gia Khánh**
- **Loại chiến lược:** Custom `HeadingChunker(chunk_size=1200)`.
- **Mô tả & lý do chọn:** Tài liệu chính sách trả hàng và hoàn tiền thường được tổ chức theo tiêu đề, mục và tiểu mục, nên heading là ranh giới ngữ nghĩa tự nhiên. Chiến lược giữ nội dung của cùng một quy định trong một section; nếu section vượt 1.200 ký tự thì phần thân được chia tiếp bằng `RecursiveChunker` và tiêu đề được gắn lại vào mỗi chunk con để không mất ngữ cảnh. Lần benchmark bằng `MockEmbedder` cho thấy kết quả còn hạn chế, vì vậy chưa thể dùng score mock để kết luận chất lượng ngữ nghĩa của chiến lược.
- **Code snippet (custom):**
```python
import re

from src import RecursiveChunker


class HeadingChunker:
    HEADING_PATTERN = re.compile(
        r"(?m)(?=^#{1,6}\s+|^\d+(?:\.\d+)*\.?\s+\S)"
    )

    def __init__(self, chunk_size: int = 1200) -> None:
        self.chunk_size = chunk_size
        self.fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = [part.strip() for part in self.HEADING_PATTERN.split(text) if part.strip()]
        chunks: list[str] = []
        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            lines = section.splitlines()
            heading = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            body_size = max(100, self.chunk_size - len(heading) - 1)
            for part in RecursiveChunker(chunk_size=body_size).chunk(body):
                chunks.append(f"{heading}\n{part}")
        return chunks
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Gia Khánh (HeadingChunker) | Heading theo mục, section dài chia đệ quy và lặp heading | 4/10 (2/5 câu có bằng chứng) | Q1/Q4 có bằng chứng; giữ đơn vị theo đề mục | Q2/Q3/Q5 mất bằng chứng; Q5 trả về chunk trả hàng thay vì bảo hành |
| Đồng Mạnh Hùng (SentenceChunker) | Phân tách theo ranh giới câu (max 3 câu/chunk) | 4/10 (2/5 câu có bằng chứng) | Q3 lấy được cụm "2 ngày" ở hạng 3; Q4 ở hạng 2; bảo toàn nguyên vẹn ngữ pháp câu văn, điều khoản và điều kiện không bị đứt đoạn vô lý. | Các câu dài hoặc điều khoản liệt kê nhiều ý bị dồn vào một chunk làm loãng mật độ từ khóa; Q1/Q2/Q5 không đưa được đoạn chứa mốc thời gian cụ thể lên top đầu. |
| Phạm Khắc Tú | `FixedSizeChunker(500, 100)` + embedding đa ngôn ngữ | 5/10 (3/5 câu có chunk liên quan) | Q1 và Q4 lên top-1; top-3 của Q1 giữ được cả mốc 15 ngày và 24 giờ | Q2/Q5 thiếu dữ liệu; Q3 có nội dung kháng nghị và bằng chứng nhưng không xác nhận đúng mốc 2 ngày của gold answer |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Trong lần chạy dùng mock, HeadingChunker và FixedSizeChunker cùng tìm thấy bằng chứng cho 2/5 câu; HeadingChunker tốt hơn ở Q1 và Q4, còn FixedSize tốt hơn ở Q3. Chưa có chiến lược thắng ổn định: embeddings mock băm nội dung nên điểm cosine không phản ánh nghĩa, còn FixedSize có thể cắt rời câu trả lời khỏi tiêu đề.

Trong lần chạy riêng bằng embedding ngữ nghĩa thật, cấu hình `FixedSizeChunker(500, 100)` của Phạm Khắc Tú đạt 3/5 câu có chunk liên quan và đưa Q1, Q4 lên top-1. Đây là kết quả tốt nhất trong phần cá nhân của Phạm Khắc Tú, nhưng nhóm vẫn cần chạy mọi chiến lược bằng cùng model trước khi kết luận chiến lược thắng chung.

### Failure case đã quan sát

- **Câu hỏi hỏng:** Q5 — điều kiện bảo hành miễn phí, chạy với HeadingChunker.
- **Điều gì xảy ra và vì sao:** Top-3 đều là chunk từ chính sách trả hàng, nhưng không chứa cụm bằng chứng “Sản phẩm bị lỗi kỹ thuật do nhà sản xuất”. Chỉ kiểm `doc_id` sẽ bỏ sót lỗi này; MockEmbedder băm MD5 nên xếp hạng gần như ngẫu nhiên, và tài liệu dài có nhiều section cùng chủ đề mua hàng.
- **Cách sửa đề xuất:** Dùng embedding ngữ nghĩa đã tải/cấu hình sẵn, giữ chunk theo mục ngắn hơn cho trang bảo hành, rồi đánh giá lại theo cụm bằng chứng ở top-3 thay vì chỉ theo tên tài liệu.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Người mua có bao lâu để yêu cầu trả hàng/hoàn tiền sau khi đơn giao thành công? | Thông thường trong vòng 15 ngày; với thực phẩm tươi sống và đông lạnh là 24 giờ. | `shopee-chinh-sach-tra-hang-hoan-tien`, mục 3.2 |
| 2 | Người mua cần làm gì để gửi yêu cầu trả hàng hoặc hoàn tiền trên Shopee? | Vào Tôi > Chờ giao hàng/Đã giao, chọn đơn và Trả hàng/Hoàn tiền, chọn tình huống/lý do, điền mô tả, bằng chứng và email rồi gửi yêu cầu. | `shopee-huong-dan-gui-yeu-cau-tra-hang`, mục 1, Cách 1 |
| 3 | Trong trường hợp được hoàn tiền ngay, cần làm gì nếu không đồng ý với quyết định? *(lọc `audience=seller`)* | Người bán cần khiếu nại kèm bằng chứng trong vòng 2 ngày kể từ khi Shopee gửi thông báo hoàn tiền ngay. | `shopee-quan-ly-tra-hang-hoan-tien-huy-nguoi-ban`, mục B.1 |
| 4 | Chính sách nào áp dụng cho sản phẩm thuộc Shopee Mall khi yêu cầu trả hàng/hoàn tiền? | Chính sách trả hàng/hoàn tiền cho sản phẩm Shopee Mall được quy định tại Điều khoản Dịch vụ Shopee Mall. | `shopee-chinh-sach-tra-hang-hoan-tien`, mục 2.3 |
| 5 | Điều kiện nào cần đáp ứng để sản phẩm được bảo hành miễn phí? | Sản phẩm bị lỗi kỹ thuật do nhà sản xuất, còn trong thời hạn bảo hành, có hóa đơn điện tử khi yêu cầu hoặc mã đơn hàng; với đồ điện gia dụng, tem/phiếu bảo hành và tem niêm phong cần nguyên vẹn theo yêu cầu hãng. | `shopee-huong-dan-bao-hanh`, mục 1 |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Người mua có bao lâu để yêu cầu trả hàng/hoàn tiền sau khi đơn giao thành công? | FixedSizeChunker `500/100` — Phạm Khắc Tú | Có, hạng 1 | Top-1 chứa mốc 15 ngày; một chunk khác trong top-3 chứa mốc 24 giờ cho thực phẩm tươi sống/đông lạnh |
| 2 | Người mua cần làm gì để gửi yêu cầu trả hàng hoặc hoàn tiền trên Shopee? | Chưa xác định | Không | Không chiến lược nào lấy được cụm thao tác cụ thể vào top-3 |
| 3 | Trong trường hợp được hoàn tiền ngay, cần làm gì nếu không đồng ý với quyết định? | FixedSizeChunker | Có, hạng 3 | Chỉ FixedSize/Recursive có bằng chứng “2 ngày” trong top-3; Heading không có |
| 4 | Chính sách nào áp dụng cho sản phẩm thuộc Shopee Mall khi yêu cầu trả hàng/hoàn tiền? | Đồng hạng: HeadingChunker và FixedSize `500/100` | Có, hạng 1 | Lượt chạy của Phạm Khắc Tú đưa đúng điều khoản Shopee Mall lên top-1 với score 0,8438 |
| 5 | Điều kiện nào cần đáp ứng để sản phẩm được bảo hành miễn phí? | Không chiến lược nào | Không | Cả ba top-3 đều bỏ lỡ chunk chứa điều kiện bảo hành |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Ở Q3, lọc `audience=seller` loại các tài liệu hướng dẫn cho người mua: với HeadingChunker top-3 không lọc là tài liệu bảo hành/chính sách người mua, còn lọc trả về tài liệu người bán; FixedSize cũng đưa chunk có bằng chứng “2 ngày” lên top-3 (hạng 3) chỉ khi lọc. Recursive lấy cùng tài liệu người bán ở cả hai lần chạy và thứ hạng bằng chứng không đổi, nên tác dụng của filter phụ thuộc chunker; toàn bộ số liệu vẫn bị giới hạn bởi MockEmbedder. Trong lượt chạy embedding thật của Phạm Khắc Tú, filter `audience=buyer` ở Q1 loại hai chunk seller đang đứng hạng cao và đưa chunk Shopee dành cho người mua lên top-1; ở Q3, top-3 trước và sau filter đều đã là tài liệu seller nên thứ hạng không đổi.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- Đối chiếu nội dung chunk quan trọng hơn kiểm tra tên tài liệu: Q5 top-3 của HeadingChunker có cùng tài liệu chính sách trả hàng nhưng không có câu trả lời bảo hành.
- A/B filter Q3 cho thấy audience có thể loại tài liệu sai đối tượng, nhưng không tự đảm bảo chunk chứa đúng bằng chứng.
- Số điểm của MockEmbedder không đánh giá được ngữ nghĩa; cần chạy lại với model embedding thật trước khi kết luận chiến lược retrieval.

**Bài học rút ra khi so sánh trong nhóm:**
Trên cùng corpus và mock embedding, HeadingChunker tìm thấy bằng chứng ở Q1/Q4, FixedSize ở Q3/Q4, còn Recursive chỉ ở Q3. Các chiến lược tạo chunk khác nhau nên đáp án có thể nằm ngoài top-3 dù đúng tài liệu đã xuất hiện; đây là kết quả thử nghiệm tại máy, chưa có kết quả của thành viên khác để so sánh.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nếu làm lại, nhóm sẽ xây dựng bộ câu hỏi gold song song với quá trình thu thập dữ liệu để bảo đảm mỗi câu đều có tài liệu và đoạn bằng chứng tương ứng, đặc biệt bổ sung hướng dẫn thao tác gửi yêu cầu và chính sách bảo hành đang thiếu ở Q2, Q5. Nhóm cũng sẽ chuẩn hóa metadata theo cả nền tảng, đối tượng và loại nghiệp vụ, sau đó chạy mọi chiến lược chunking trên cùng một model embedding ngữ nghĩa để kết quả so sánh công bằng. Cuối cùng, nhóm sẽ kiểm tra thủ công top-3 theo nội dung bằng chứng thay vì chỉ dựa vào score hoặc tên tài liệu.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 6 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **36 / 40** |

