---
name: handoff
description: Kết phiên sạch — đẩy trạng thái ra khỏi hội thoại vào tracker, git và task file.
disable-model-invocation: true
---

# Handoff — kết phiên

Thiết kế của repo này cho phép **vứt bất kỳ phiên nào mà không mất gì**, với điều
kiện trạng thái đã nằm ở tracker + git + task file chứ không nằm trong hội thoại.
Skill này kiểm đúng điều kiện đó.

## Chạy khi

Phiên dài quá ~60% context, hết giờ làm, hoặc chuyển sang test ID khác.

## Checklist

1. `./mo verify` — ghi lại kết quả thật (xanh hay đỏ). **Không** kết phiên mà tuyên bố
   "gần xong" — đỏ là chưa xong, và đó là thông tin có ích cho phiên sau.
2. `git status` — không để file lửng lơ. Hoặc commit, hoặc nói rõ vì sao chưa.
3. Cập nhật `tasks.md` của feature: task nào xong, task nào đang dở, **đang vướng ở đâu**.
   Chỗ vướng là thứ đắt nhất để tái tạo — ghi nó ra.
4. `./mo steer list --open` — mục nhật ký nào còn mở thì đóng bằng kết cục **thật**
   (`kept` / `reverted`), kèm bằng chứng. Mục mở là chỗ duy nhất ghi được thứ đã thử
   rồi bỏ; để nó treo là mất luôn.
5. Nếu có quyết định kiến trúc phát sinh trong phiên → ADR (skill `adr`). Quyết định
   chỉ tồn tại trong hội thoại là quyết định sẽ bị mở lại vào lúc mệt nhất.
6. Nếu bug lặp lần hai → thêm một dòng vào skill liên quan ngay bây giờ.

## Tóm tắt cuối phiên

In đúng bốn dòng:

```
Test ID:      <ID> — <đỏ | xanh | chưa bắt đầu>
Nhánh:        <tên>  (<n> file chưa commit)
Đang vướng:   <một câu, hoặc "không">
Việc kế tiếp: <một câu cụ thể, không phải "tiếp tục">
```

Hook `PreCompact` đã tự chụp nhánh/diff/commit vào `.claude/cache/handoff.md` —
không cần chép lại những thứ đó, chỉ cần bốn dòng trên.
