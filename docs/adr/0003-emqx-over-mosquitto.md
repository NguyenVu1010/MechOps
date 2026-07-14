# ADR-0003: EMQX làm broker, không dùng Mosquitto
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ dev-plan mục 1.2, chốt 2026-07-09)
- Covers: [ACL-01, ACL-02, ACL-03]
## Context
Cần broker MQTT với ACL per-device (robot A không đọc được topic robot B — bộ test bán hàng ACL-01..04), auth bằng device certificate, và MQTT 5 (response topic + user properties cho OTA, shared subscription khi scale API server).
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. EMQX open source — 2. Mosquitto — 3. NanoMQ/VerneMQ* (loại sớm: cộng đồng nhỏ hơn, không thêm được gì EMQX thiếu)
## Decision
EMQX: auth/ACL qua PostgreSQL bằng SQL (Mosquitto dùng file text — khó quản per-device ở quy mô); dashboard quản trị built-in giúp debug connection khi deploy tại vendor; MQTT 5 đầy đủ.
## Consequences
+ ACL per-device cấu hình bằng SQL cùng database chính; đường scale có sẵn (shared subscription).
− Nặng hơn Mosquitto (~200MB RAM) — chấp nhận vì broker chạy trên VPS/edge server, không bao giờ trên robot.
