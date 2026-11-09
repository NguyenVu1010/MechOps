# ADR-0009: Go cho server, không dùng C++
- Status: accepted
- Date: 2026-07-15 (founder chuẩn thuận sau thảo luận Go vs C++ 2026-07-14)
## Context
MechOps là sản phẩm hạ tầng vận hành: telemetry, MQTT, OTA, PTY, quản lý thiết bị. Nó không phải phần mềm điều khiển robot. Server làm CRUD, SSE, điều phối rollout (Fleet Manager), ký cert, ghi TimescaleDB theo batch. Toàn bộ workload là I/O-bound network plumbing, không có vòng lặp real-time nào cần độ trễ micro-giây. Server chạy trên VPS hoặc edge server của vendor, đóng gói bằng Docker Compose.

Agent trên robot là bài toán khác (chạy trên thiết bị khách, quyền cao, sống nhiều năm), nên ngôn ngữ của nó quyết riêng ở ADR-0012.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. Go — 2. C++ — 3. Rust*
## Decision
Go 1.22+ cho server và cho mã Go sinh từ `specs/` (`protocol/`). Lý do theo thứ tự nặng ký:
1. **Hệ sinh thái first-class đúng stack đã chốt**: chi, pgx + sqlc, golang-migrate, paho.golang (MQTT 5), slog; Phase 1 có Pion cho WebRTC signaling.
2. **Tốc độ viết và khả năng review**: code server phần lớn là ống nước HTTP/DB/MQTT, người không chuyên vẫn review được code do AI sinh.
3. **Single static binary, cross-compile bằng một biến `GOARCH`**: image server nhỏ, chạy được trên edge server amd64 hoặc arm64 của vendor.
4. **An toàn bộ nhớ**: server giữ khoá CA và mở cổng ra Internet; Go loại bỏ lớp lỗi buffer overflow của C++.
5. **Concurrency khớp bài toán**: goroutine cho MQTT subscriber, SSE fan-out, ingest batch chạy đồng thời. GC không phải vấn đề ở tải này.

Loại C++: không có lợi thế hiệu năng nào được dùng tới, còn chi phí an toàn bộ nhớ và build đa nền tảng là thật. Loại Rust cho server ở Phase 0: server không được lợi từ kiểu-an-toàn như state machine OTA của agent, mà nhân đôi rủi ro học cho team part-time. Xét lại sau M3 nếu team đã thạo Rust (ADR-0012).
## Consequences
+ Server viết nhanh, hệ sinh thái sẵn cho mọi việc Phase 0. Đội web chỉ cần Go và TypeScript.
+ Một binary tĩnh trong một image nhỏ.
− Hệ thống có hai ngôn ngữ hệ thống (Go ở server, Rust ở agent). Chấp nhận vì ranh giới agent/server vốn là ranh giới cứng nhất, nối bằng `specs/` chứ không bằng code dùng chung.

_Chuẩn hoá 2026-11-08 trước khi tách repo (ADR-0019): bản gốc chọn Go cho cả agent; phần agent nay chỉ nằm ở ADR-0012, ADR này chỉ còn server._
