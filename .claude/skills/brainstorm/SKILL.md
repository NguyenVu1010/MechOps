---
name: brainstorm
description: Mở không gian phương án TRƯỚC khi viết spec, khi đứng trước một cụm việc lớn hoặc một quyết định chưa rõ đường. Trigger, brainstorm, chưa biết làm sao, có mấy cách, nên chọn gì, thiết kế thế nào, mở milestone lớn.
argument-hint: "[chủ đề]"
---

# Brainstorm — mở không gian trước khi đóng nó lại

Chạy trước `/feature`, không thay thế nó. Đầu ra không phải ý tưởng — đầu ra là
**danh sách phương án đã bị loại kèm lý do**, để nửa năm sau không ai mở lại.

## Khi nào cần

Cụm việc lớn (≥1 milestone), hoặc bất cứ lúc nào câu trả lời đầu tiên nghe hợp lý
mà chưa ai thử phản bác. Việc nhỏ, đường đi rõ → bỏ qua, vào thẳng `/feature`.

## Cách làm

1. **Phát biểu vấn đề bằng ràng buộc, không bằng giải pháp.**
   Viết "robot mất điện giữa lúc đổi version phải bootable lại được", không viết
   "cần A/B partition". Ràng buộc mở ra nhiều phương án; giải pháp thì không.

2. **Ít nhất 3 phương án, trong đó bắt buộc có:**
   - phương án **dùng OSS có sẵn** (constitution #6 — mọi "tự xây" phải trả lời được
     "vì sao không dùng cái có sẵn"; không nêu ra thì không trả lời được)
   - phương án **làm ít nhất có thể** — thường là baseline tốt hơn ta tưởng

3. **Với mỗi phương án, viết một câu cho mỗi mục:** nó hỏng thế nào · chi phí vận
   hành cho team part-time · nó khoá ta vào cái gì · Phase 1–4 có phải đập đi không.

4. **Đối chiếu ràng buộc cứng.** Loại thẳng phương án vi phạm:
   `constitution.md` · stack đã chốt trong `02-dev-plan-phase0.md` · ADR đang có
   trong `docs/adr/`. Đụng ADR cũ mà vẫn muốn đi tiếp → đó là ADR mới supersede,
   không phải im lặng làm khác.

5. **Kết bằng 3 dòng, không kết bằng "tuỳ":**
   ```
   Chọn:      <phương án> — vì <một lý do nặng ký nhất>
   Loại:      <phương án> vì <lý do>; <phương án> vì <lý do>
   Phải viết: ADR-<số kế tiếp> · test ID cần thêm vào catalog: <có/không, ID nào>
   ```

## Sau khi xong

- Có lựa chọn giữa ≥2 phương án hệ quả dài hạn → **viết ADR ngay** (skill `adr`),
  đừng để tới lúc code. Quyết định chỉ nằm trong hội thoại là quyết định sẽ bị mở lại.
- Rồi mới `/feature <tên>`.

## Không làm

- Không kết thúc bằng danh sách ý tưởng ngang hàng. Brainstorm không chọn được gì
  là brainstorm chưa xong.
- Không đề xuất công nghệ ngoài stack đã chốt mà không nói rõ nó cần ADR.
- Không tự quyết thay founder khi phương án ảnh hưởng tới hợp đồng `specs/` — nêu
  ra, rồi hỏi.
