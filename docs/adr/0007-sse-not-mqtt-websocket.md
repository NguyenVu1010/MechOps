# ADR-0007: Dashboard realtime qua SSE từ API server, không MQTT-over-WebSocket
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ dev-plan mục 1.4, chốt 2026-07-09)
## Context
Dashboard cần dữ liệu realtime (state, telemetry, events). Cách hiển nhiên là cho browser connect thẳng broker qua MQTT-over-WebSocket.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. SSE từ API server (server subscribe MQTT nội bộ, đẩy SSE) — 2. MQTT-over-WebSocket thẳng từ browser — 3. WebSocket tự chế từ API server*
## Decision
SSE từ API server. Broker KHÔNG BAO GIỜ expose ra Internet; ACL theo user (RBAC admin/viewer) kiểm soát ở API server — broker chỉ biết device cert, không biết user. Loại WebSocket tự chế: SSE đủ cho luồng một chiều server→browser, tự động reconnect built-in, đi qua proxy/LB dễ hơn.
## Consequences
+ Một cửa duy nhất ra Internet (API server); phân quyền user tách khỏi phân quyền device; TanStack Query + SSE invalidation là đủ, không cần Redux.
− API server thành điểm trung chuyển mọi realtime — cần đo khi số client tăng; lệnh chiều ngược (user → robot) vẫn đi REST → server → MQTT như thiết kế.
