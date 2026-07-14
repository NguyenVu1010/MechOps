# ADR-0009: Go cho agent + server, không dùng C++
- Status: accepted
- Date: 2026-07-15 (founder chuẩn thuận sau thảo luận Go vs C++ 2026-07-14)
## Context
MechOps là sản phẩm hạ tầng vận hành (telemetry, MQTT, OTA, PTY, WireGuard) — không phải phần mềm điều khiển robot. Agent chạy quyền cao trên robot của khách hàng, nhiều vendor, nhiều bản Ubuntu, nhiều kiến trúc (amd64/arm64). Toàn bộ workload là I/O-bound network plumbing, không có vòng lặp điều khiển real-time nào cần độ trễ micro-giây.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. Go — 2. C++ — 3. Rust*
## Decision
Go 1.22+ cho cả agent lẫn server. Lý do theo thứ tự nặng ký:
1. **Single static binary, cross-compile bằng một biến `GOARCH`**, không phụ thuộc glibc — cài lên robot đa vendor/đa kiến trúc không vật lộn dependency/ABI. Khớp nguyên tắc tối thiểu hóa chi phí vận hành cho team part-time (dev-plan).
2. **An toàn bộ nhớ trên máy khách hàng**: agent nhận lệnh từ mạng với quyền cao (OTA, remote terminal) — buffer overflow kiểu C++ ở đây là lỗ hổng bảo mật nghiêm trọng; Go loại bỏ nguyên lớp lỗi này.
3. **Concurrency khớp bài toán**: goroutines cho MQTT client + Unix socket server + PTY + OTA chạy đồng thời.
4. **Hệ sinh thái first-class đúng stack đã chốt**: paho.golang (MQTT 5), Docker SDK for Go, gopsutil, slog.
5. **GC không phải vấn đề** ở tần suất telemetry vài Hz — GC pause chỉ đáng bàn ở control loop kHz, thứ không nằm trong agent.
Lợi thế của C++ (kiểm soát bộ nhớ, hard real-time) không được dùng đến: phần real-time/hiệu năng cao sống trong stack ROS 2 sẵn có của robot, đã cố tình đẩy ra ngoài agent qua kiến trúc probe (ADR-0004). Nếu sau này cần node C++ hiệu năng cao, nó là component ROS 2 riêng, không phải viết lại agent.
## Consequences
+ Một toolchain cho agent + server; onboard dev Go dễ hơn C++ đa nền tảng; đổi kiến trúc robot mới = một lần cross-compile.
− Không nhúng thẳng DDS/rclgo được (chấp nhận, đã giải bằng ADR-0004); binary Go lớn hơn C++ tương đương vài MB — không đáng kể trên robot có Docker.
