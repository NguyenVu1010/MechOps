---
name: dev
description: Cửa vào DUY NHẤT của quy trình. Chẩn đoán đang ở bước nào rồi gọi đúng skill tiếp theo. Dùng khi không nhớ phải làm gì, khi mở phiên mới, hoặc khi vừa xong một bước.
argument-hint: "[TEST-ID hoặc tên feature]"
disable-model-invocation: true
allowed-tools: Bash(bash ./mo:*) Bash(git status:*) Bash(git branch:*) Bash(git log:*)
---

# /dev — không phải nhớ gì cả

Quy trình có 8 bước và 17 skill. Skill này tồn tại để **không ai phải nhớ cái nào
đến trước**. Nó không lặp lại nội dung của skill khác — nó chỉ định vị và chuyển tiếp.

## Làm gì

```bash
./mo next
```

Lệnh đọc tracker, `.steering/plans/*/`, mục nhật ký còn `open`, và git; trả về
**giai đoạn đang đứng** + **lệnh tiếp theo** + **căn cứ**. Đọc phần căn cứ trước
khi làm theo: chẩn đoán sai thì phải nhìn ra được, không được sai im lặng.

Rồi gọi đúng skill mà nó chỉ. Có `$1` thì bỏ qua chẩn đoán, vào thẳng
`/task $1` nếu đó là test ID.

## Bảng chuyển tiếp

| `./mo next` báo | Gọi | Ghi chú |
|---|---|---|
| NỢ NHẬT KÝ | `./mo steer close …` | đóng trước mọi thứ khác — mục `open` là chuyện không ai biết đã xảy ra gì |
| chưa có plan | `./mo steer plan new` rồi `/feature` | `--covers` bắt buộc, bị kiểm với catalog |
| specify | `/feature` | điền `spec.md` |
| **GATE NGƯỜI — clarify** | **DỪNG** | founder trả lời trong `clarify.md`. Agent **không** tự trả lời thay (constitution #9) |
| chốt spec | `./mo steer plan lock <plan> spec` | chỉ được khi clarify `answered` |
| tech-plan | `/tech-plan <plan>` | 6 mục, có ma trận thất bại → `lock plan` |
| testcases | điền `testcases.md` | mỗi ID trong covers một mục `## <ID>` → `lock testcases` |
| tasks | `/feature` | task ≤ nửa ngày, mỗi task ≥1 test ID → `lock tasks` |
| bắt đầu task | `/spec-analyze` rồi `/task <ID>` | analyze nếu vừa sửa spec/plan/tasks |
| đang làm | `./mo verify` → `/audit` | vòng ĐỎ → XANH → GỌN |
| sẵn sàng PR | `/pr` | |

`STATUS.md` trong thư mục plan là mặt tiền: cổng nào đã chốt, task mấy/mấy, ID nào
xanh. Dấu tích `tasks.md` do máy điền — không tick tay.

## Ba chỗ /dev **không** tự đi qua

1. **Gate clarify** — câu hỏi chưa có đáp án của founder thì dừng, không đoán.
2. **Test [H]** — chỉ người chạy `./mo hw-test`. Agent soạn checklist rồi dừng.
3. **Merge vào `main`** — constitution #9.

## Khi lệch khỏi đường thẳng

`./mo next` chỉ biết trạng thái, không biết ý định. Ba tình huống nó không bắt được,
tự nhận ra thì gọi thẳng:

- Chưa rõ nên làm theo cách nào → `/brainstorm` **trước** khi mở plan
- Test đỏ không hiểu vì sao → `troubleshoot` (tái hiện trước, sửa sau)
- Phát hiện bug → `bug-to-test` (thêm test ID mới **trước** khi sửa)
- Bỏ một hướng đi → `steering` ngay lúc đổi hướng, `--plan <tên>` để vào JOURNAL

## Kết phiên

`/handoff`. Trước đó `./mo steer list --open` — mục treo là nợ, và trạng thái thật
phải nằm ở tracker + git + plan file, không nằm trong hội thoại.
