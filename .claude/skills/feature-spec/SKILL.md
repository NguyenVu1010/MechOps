---
name: feature-spec
description: Đọc khi bắt đầu một feature/cụm việc mới của milestone (vòng ngoài), trước khi viết bất kỳ test/code nào. Trigger, feature mới, bắt đầu milestone, mini-spec, tasks, clarify, spec.md, plan.md.
paths:
  - ".steering/plans/**"
---

# Feature Spec — vòng ngoài

Vòng ngoài SDD của repo: `.steering/plans/<mX-ten>/` gồm **bốn** file theo thứ tự
`spec.md → clarify.md → plan.md → tasks.md`. Cấu trúc từng file:
`.steering/plans/TEMPLATE.md`. Chạy cả chuỗi bằng `/feature`.

1. **spec.md** — hành vi + ngoài scope + `covers: [test ID]` từ
   `docs/product/05-test-catalog.md`. Không cover ID nào = không hợp lệ.
2. **clarify.md** — mọi điểm mờ thành câu hỏi, **DỪNG** chờ founder. Không tự giả định.
3. **plan.md** — làm thế nào (skill `tech-plan`). Không có bước này thì quyết định
   kỹ thuật bị đẩy vào lúc đang code.
4. **tasks.md** — task ≤ nửa ngày, mỗi task ≥1 test ID. Task không có ID = không hợp lệ.

Rồi `/spec-analyze` để đối chiếu chéo, sau đó mới vào vòng trong (`/task <ID>`).

## Vì sao bốn file chứ không phải một

Mỗi file trả lời một câu khác nhau và **bị người khác đọc vào lúc khác nhau**:
`spec.md` là thứ founder duyệt, `clarify.md` là chỗ founder trả lời, `plan.md` là
thứ người review PR đối chiếu, `tasks.md` là thứ agent lấy việc. Gộp lại thì không
cái nào đọc được cho tử tế.

## Sửa sau khi đã mở feature

Đổi bất kỳ file nào trong bốn file → chạy lại `/spec-analyze`. Lệch giữa chúng không
tự báo; nó chỉ hiện ra ở review hoặc ở khách hàng.
