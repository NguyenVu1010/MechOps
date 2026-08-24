---
paths:
  - "server/**"
---

# Luật khi làm việc trong server/

## SQL

- Query viết trong `server/queries/*.sql`, sinh code bằng **sqlc**. Không có
  string SQL trong file `.go` — kể cả query "chỉ một dòng".
- **Mọi query chạm dữ liệu thiết bị phải scope theo tenant.** Tenant nằm trong
  topic từ ngày đầu (ADR 0008); nếu query không có điều kiện tenant thì nó đang
  đọc dữ liệu của khách hàng khác. Đây là lỗi chặn merge, không phải nit.
- Migration là thêm, không phải sửa. Đã chạy ở đâu đó thì không sửa nữa.

## Chiều phụ thuộc

`server/` không import `agent/` (constitution #7). Message struct dùng chung nằm ở
`protocol/` — đó là nơi DUY NHẤT định nghĩa message.

## HTTP và handler

- Router: `chi`. Handler nhận đủ dependency qua struct, không dùng biến global.
- Mọi hàm chạm network/DB nhận `context.Context` làm tham số đầu.
- Lỗi bọc bằng `fmt.Errorf("ngữ cảnh: %w", err)`. Không log-rồi-return-nil.

## Realtime

Dashboard nhận cập nhật qua **SSE**, không phải MQTT-over-WebSocket (ADR 0007).
Đừng mở đường MQTT ra browser.

## Log

`slog`, JSON. Không bao giờ log cert, token, hay payload thô. Kèm
`deviceId`/`agentId`/`cmdId`/`deploymentId` khi ngữ cảnh có.
