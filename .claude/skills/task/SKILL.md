---
name: task
description: Mở một task của vòng trong — 1 phiên = 1 task = 1 test ID. Dùng khi bắt đầu làm một test ID cụ thể.
argument-hint: <TEST-ID>
disable-model-invocation: true
---

# Task — vòng trong

Làm task `$1` theo `tasks.md` của feature tương ứng. Một phiên làm đúng một test ID.

## Trước khi chạm file nào

Trình kế hoạch và **chờ founder xác nhận**:

1. **Test ID** đang làm, tầng của nó ([U]/[I]/[H]) — nếu là [H] thì DỪNG, đó là việc của người.
2. **Contract cần đổi gì**: schema/topic/asyncapi. Nếu có → đọc skill `contract-guard` trước.
3. **Test viết trước**: tên đầy đủ theo skill `test-evidence` (`Test<ID bỏ gạch>_<MôTả>`).
4. **File sẽ chạm**: liệt kê đường dẫn, không mô tả chung chung.

Không có xác nhận thì không sửa file. Giả định sai bị giết ở đây rẻ hơn trong code.

## Vòng lặp — ĐỎ → XANH → GỌN

```
đỏ (chứng minh)  →  xanh (tối thiểu)  →  gọn (refactor)  →  ./mo verify  →  /audit  →  commit
```

### 1. ĐỎ — và phải chứng minh là đỏ

Viết test rồi chạy `./mo verify`. **Đọc output, đừng chỉ tin là nó đỏ.** Ba câu hỏi:

- Nó đỏ **vì assert thất bại**, hay vì compile lỗi / panic / thiếu hạ tầng?
  Đỏ sai lý do là test vô dụng — nó sẽ xanh vì lý do sai luôn.
- Thông báo thất bại có nói ra **giá trị thật vs giá trị mong đợi** không?
  Không thì phiên sau sẽ mất thời gian đúng ở chỗ này.
- Test có thể xanh **mà hành vi vẫn sai** không? (assert `!= nil`, assert độ dài,
  assert "không panic" — đều là test rỗng). `test-auditor` sẽ bắt, nhưng bắt ở đây rẻ hơn.

Bỏ qua bước chứng minh là cách phổ biến nhất để có một bộ test xanh mà không canh gì.

### 2. XANH — tối thiểu

Chỉ đủ để test đó xanh. Không "nhân tiện" làm thêm — mỗi thứ nhân tiện là một thứ
không có test nào canh.

### 3. GỌN — refactor khi đang xanh

Bước hay bị bỏ nhất, và là bước duy nhất được phép sửa code mà **không đổi hành vi**:
gộp trùng lặp, đặt lại tên, tách hàm dài, bỏ nhánh chết. Chạy `./mo verify` lại sau
khi gọn — vẫn xanh thì refactor đúng, đỏ lên thì hoàn tác, đừng sửa test cho vừa.

Không có gì để gọn thì nói "không có" và đi tiếp. Skill `/simplify` có sẵn nếu cần.

### Rồi mới

- `./mo verify` là lệnh duy nhất cập nhật tracker. Không gõ tay vào `docs/test-status.*`
  — hook chặn, và đó là chủ đích.
- `/audit` — cả hai kiểm toán viên phải PASS.
- Commit có dòng `Implements: <ID>` — git hook `commit-msg` chặn nếu thiếu.

## Test đỏ mà không hiểu vì sao

Chuyển sang skill `troubleshoot`. Đừng sửa theo phỏng đoán, và đừng `t.Skip` để đi tiếp.

## Nhánh

`feat/<ID viết thường>-<mô tả ngắn>`, ví dụ `feat/prv-01-enroll-token`.
Task song song → `git worktree`, không trộn context trong một phiên.

## Khi bí

Trạng thái thật nằm ở tracker + git, không nằm trong hội thoại. Phiên dài quá thì
chạy skill `handoff` rồi kết phiên — vứt phiên bất kỳ lúc nào cũng không mất gì.
