---
name: tech-plan
description: Viết plan.md kỹ thuật của một feature — bước giữa clarify và tasks. Dùng khi đã có spec.md + clarify.md và trước khi bẻ task. Trigger, plan kỹ thuật, thiết kế feature, state machine, chia task, trước khi implement.
argument-hint: <tên feature>
disable-model-invocation: true
---

# Tech plan — quyết định "làm thế nào" trước khi bẻ task

`spec.md` nói **cái gì** và **vì sao**. `tasks.md` nói **thứ tự**. Ở giữa còn một
câu chưa ai trả lời: **làm thế nào**. Bẻ task khi chưa trả lời câu đó thì task chỉ
là danh sách mong muốn, và mọi quyết định thật bị đẩy vào lúc đang code — lúc tệ
nhất để quyết định.

Đầu ra: `.steering/plans/<mX-ten>/plan.md`. Một trang. Không phải tài liệu thiết kế.

## Sáu mục, không thiếu mục nào

1. **Delta hợp đồng** — `specs/` phải đổi gì.
   Liệt kê từng file: schema nào thêm field gì, topic nào mới, message nào đổi.
   Field mới **phải optional** (forward-compat, TEL-07). Có bất kỳ đổi nghĩa hoặc
   xoá field nào → **DỪNG, hỏi founder** (constitution #4). Đọc skill `contract-guard`.

   Xong mục này thì khai luôn danh sách file vào `contract:` của `spec.md` —
   `./mo steer plan contract <x> --add specs/...`. Văn xuôi ở đây không ai kiểm
   được; `contract:` mới là thứ CI đối chiếu với diff `specs/` của PR. Sửa file
   hợp đồng chưa khai = CI đỏ.

2. **State machine** — nếu feature có trạng thái (OTA, provisioning, phiên terminal).
   Vẽ bằng chữ: `state → sự kiện → state`. Chỉ rõ **trạng thái nào ghi xuống SQLite
   và ghi ở thời điểm nào** — với `agent/`, luật là ghi TRƯỚC hành động, không có
   ngoại lệ (constitution #3).

3. **Ma trận thất bại** — không phải "xử lý lỗi", mà là bảng:

   | Hỏng ở đâu | Lúc nào | Hành vi mong đợi | Test ID |
   |---|---|---|---|
   | mất điện | giữa DOWNLOADING | bootable lại, state khôi phục | OTA-04 |
   | mất mạng | giữa download | resume hoặc fail sạch | OTA-06 |

   Mỗi dòng phải trỏ một test ID. Dòng không có ID = thiếu ID trong catalog, thêm trước.
   Bốn tình huống luôn phải cân nhắc: **mất điện · mất mạng · disk đầy · lệch giờ**.

4. **Chia tầng test** — mỗi test ID của feature vào đúng tầng:
   - `[U]` chạy được không cần hạ tầng → ưu tiên tối đa, vòng phản hồi ngắn nhất
   - `[I]` cần docker compose → gom lại, đừng rải
   - `[H]` cần phần cứng thật → **agent không bao giờ tick**; việc của agent là
     soạn sẵn checklist để người chạy `./mo hw-test`

5. **Đường ranh module** — code mới nằm ở đâu và **vì sao không nằm chỗ khác**.
   Chiều phụ thuộc `server → protocol ← agent` là bất biến (constitution #7);
   thứ dùng chung đi vào `protocol/`. `depguard` sẽ chặn nếu sai, nhưng phát hiện
   ở plan rẻ hơn phát hiện ở lint.

6. **Quyết định cần ADR** — liệt kê. Không có = ghi rõ "không có", đừng bỏ trống.

## Kiểm trước khi sang tasks

- Mọi ID trong `covers:` của `spec.md` xuất hiện ở mục 3 hoặc mục 4.
- Không mục nào còn chữ "sẽ tính sau".
- Có delta hợp đồng → test vector mới (hợp lệ **và** không hợp lệ) đã nằm trong plan.

## Chốt xong mới đi tiếp

```bash
./mo steer plan lock <plan> plan
```

Lệnh chặn nếu `plan.md` còn chỗ `<...>` hoặc `spec` chưa chốt. Xong thì sang
`testcases.md` (thiết kế test từng ID), rồi `tasks.md`, rồi `/spec-analyze`.
