---
name: go-conventions
description: Quy ước Go riêng của repo MechOps, áp cho server và protocol. Đọc khi viết code Go mới, tạo package, viết query SQL, hoặc thêm logging. Trigger — Go, handler, sqlc, slog, package layout.
paths:
  - "**/*.go"
metadata:
  adr: [0009, 0012]
---

# Go Conventions — MechOps

## Layout
- `/server` — API + Fleet Manager + CA (Go). Đây là nơi Go sống.
- `/protocol` — struct message (sinh từ `specs/schemas`) + topic constant + validate,
  **chỉ server import**. Nguồn sự thật là `specs/`, không phải file Go này.
- `/agent` — mechops-agent viết bằng **Rust** (ADR-0012), xem skill `rust-conventions`.
  Không có code Go trong `/agent`.
- `/probe` — ros2-probe viết bằng **C++** (ADR-0013). Không phải Go.

## Quy ước
- Router: chi. Handler nhận đủ dependency qua struct, không global.
- DB: sqlc, query trong `server/queries/*.sql`. Không string SQL trong .go.
- Log: slog, JSON. Luôn attach `deviceId`/`agentId`/`cmdId`/`deploymentId` khi có trong ngữ cảnh — đây là các key tra cứu sự cố.
- Error: `fmt.Errorf("ngữ cảnh: %w", err)`. Không log-rồi-return-nil.
- PKI: mọi thao tác ký cert nằm trong `server/internal/ca`, dùng `crypto/x509` stdlib (ADR-0016). Không thêm thư viện PKI.
- Time: `time.Now().UnixMilli()` cho ts.
- Context: mọi hàm chạm network/DB nhận `context.Context` tham số đầu.
- Test: tên `Test<ID bỏ gạch>_<MôTả>` (ví dụ `TestPRV01_EnrollTokenHopLe`) để tracker tick được.
