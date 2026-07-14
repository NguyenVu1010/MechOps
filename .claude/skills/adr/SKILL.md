---
name: adr
description: Đọc khi đưa ra hoặc thay đổi quyết định kiến trúc, chọn thư viện/công nghệ, hoặc user hỏi "vì sao dùng X". Trigger: ADR, decision, quyết định, chọn công nghệ, thay thế, supersede.
---
# ADR
- Mọi lựa chọn giữa ≥2 phương án có hệ quả dài hạn → 1 file docs/adr/NNNN-*.md theo TEMPLATE.md.
- ADR bất biến. Đổi ý → ADR mới, đánh dấu supersedes, cập nhật Status file cũ. CÙNG PR đó: sửa skill nào có frontmatter adr trỏ tới ADR bị supersede.
- Không có ADR cho một dependency mới = không thêm dependency đó (constitution #5, #6).
