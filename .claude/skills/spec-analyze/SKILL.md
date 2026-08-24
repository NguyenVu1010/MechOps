---
name: spec-analyze
description: Đối chiếu chéo spec.md ↔ plan.md ↔ tasks.md ↔ catalog trước khi viết dòng code đầu tiên. Chạy lại mỗi khi một trong bốn thứ đó đổi.
argument-hint: <tên feature>
disable-model-invocation: true
---

# Spec-analyze — bắt lệch khi còn rẻ

Bốn artifact của một feature dễ trôi khỏi nhau: sửa `tasks.md` mà quên `spec.md`,
thêm hành vi vào `plan.md` mà không có test ID. Skill này là bước `analyze` của SDD —
chạy **sau `tasks.md`, trước `/task` đầu tiên**, và **chạy lại** mỗi lần sửa một
trong bốn thứ.

Chỉ đọc và báo cáo. Không tự sửa artifact — sửa spec là quyết định, không phải dọn dẹp.

## Sáu đối chiếu

1. **spec → tasks**: mọi ID trong `covers:` của `spec.md` xuất hiện ở ≥1 task.
   Thiếu → hành vi đã hứa mà không ai làm.

2. **tasks → spec**: mọi ID trong `tasks.md` có trong `covers:` của `spec.md`.
   Thừa → đang làm việc ngoài scope đã thoả thuận, hoặc `spec.md` cũ.

3. **ID → catalog**: mọi ID xuất hiện ở bất kỳ đâu đều có thật trong
   `docs/product/05-test-catalog.md`. ID ma là ID sẽ không bao giờ được tick
   (`track.py` bỏ qua ID lạ — hỏng im lặng). `./mo trace` kiểm được phần này.

4. **plan → test ID**: mọi dòng trong ma trận thất bại của `plan.md` trỏ một ID.
   Không có ID = tình huống hỏng không ai canh.

4b. **covers → testcases**: mọi ID trong `covers:` có một mục `## <ID>` trong
   `testcases.md`, và mục đó nêu được **mong đợi quan sát từ bên ngoài** (không
   phải "không lỗi") cùng **bằng chứng** cụ thể. ID không có thiết kế test là ID
   sẽ được implement theo phỏng đoán.

4c. **cổng chốt đúng thứ tự**: `status` của spec → plan → testcases → tasks không
   được nhảy bậc. `./mo trace` cũng kiểm; ở đây chỉ nhắc để không đi tiếp khi lệch.

5. **clarify đã đóng**: `clarify.md` không còn câu hỏi nào chưa có đáp án của founder.
   Còn treo → **DỪNG**, đây là gate người, không được tự trả lời thay.

6. **Đụng chạm hợp đồng**: task nào sửa `specs/` thì `plan.md` mục 1 phải đã liệt kê
   delta đó. Sửa contract ngoài kế hoạch là cách spec-drift bắt đầu.

## Báo cáo

Đúng ba khối, không thêm:

```
KHỚP:    <n> ID, <n> task
LỆCH:    - <mô tả cụ thể + file:dòng>
DỪNG:    - <thứ bắt buộc phải có người quyết trước khi đi tiếp>   (hoặc "không")
```

Có bất kỳ mục nào trong `DỪNG` → không vào `/task`. Có `LỆCH` mà không có `DỪNG` →
sửa artifact rồi chạy lại skill này, không đi tiếp bằng trí nhớ.
