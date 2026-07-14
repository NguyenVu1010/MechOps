---
name: go-conventions
description: Quy ước Go riêng của repo RobotOps. Đọc khi viết code Go mới, tạo package, viết query SQL, hoặc thêm logging. Trigger: Go, handler, sqlc, slog, package layout.
---

# Go Conventions — RobotOps

## Layout
- `/agent` — robotops-agent (binary riêng, KHÔNG import code server)
- `/server` — API + Fleet Manager
- `/protocol` — struct message + topic constant + validate, import được từ cả hai phía. Đây là NƠI DUY NHẤT định nghĩa message.
- `/probe` — ros2-probe (Python, không phải Go)

## Quy ước
- Router: chi. Handler nhận đủ dependency qua struct, không global.
- DB: sqlc, query trong `server/queries/*.sql`. Không string SQL trong .go.
- Log: slog, JSON. Luôn attach `deviceId`/`agentId`/`cmdId`/`deploymentId` khi có trong ngữ cảnh — đây là các key tra cứu sự cố.
- Error: `fmt.Errorf("ngữ cảnh: %w", err)`. Không log-rồi-return-nil.
- Agent: mọi state ghi SQLite TRƯỚC khi hành động (luật OTA #2). Dùng transaction.
- Time: `time.Now().UnixMilli()` cho ts; seq từ counter monotonic, persist qua restart.
- Context: mọi hàm chạm network/DB nhận `context.Context` tham số đầu.
