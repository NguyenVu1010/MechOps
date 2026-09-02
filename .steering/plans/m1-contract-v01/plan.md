---
plan: m1-contract-v01
milestone: M1
status: draft
covers: [TEL-01, TEL-07]
adr: [0001]
requirements:
  - docs/protocol-notes.md#3
  - docs/product/06-spec-management.md
---

# m1-contract-v01 · plan — LÀM THẾ NÀO

## 1. Delta hợp đồng `specs/`
<field/topic/message nào đổi; field mới phải optional>

## 2. State machine
<state → sự kiện → state; ghi SQLite lúc nào>

## 3. Ma trận thất bại

| Hỏng ở đâu | Lúc nào | Hành vi mong đợi | Test ID |
|---|---|---|---|
| mất điện |  |  |  |
| mất mạng |  |  |  |
| disk đầy |  |  |  |
| lệch giờ |  |  |  |

## 4. Chia tầng test
<ID nào [U] / [I] / [H]>

## 5. Đường ranh module
<code mới nằm đâu, vì sao không nằm chỗ khác>

## 6. Quyết định cần ADR
<liệt kê, hoặc ghi rõ 'không có'>
