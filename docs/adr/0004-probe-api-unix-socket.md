# ADR-0004: Probe tách khỏi agent, nói chuyện qua Unix socket
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ dev-plan mục 1.5, chốt 2026-07-09)
- Covers: [PRB-02, PRB-03, PRB-06]
## Context
Go không nói chuyện DDS/ROS 2 tự nhiên (rclgo chưa production-ready). Agent cần dữ liệu ROS 2 (node, topic hz, battery, pose) nhưng không được phụ thuộc phiên bản ROS 2 của robot.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. ros2-probe sidecar (Python/rclpy trong container ROS 2 của robot) + Unix socket NDJSON — 2. Agent gọi `ros2 node list` bằng subprocess — 3. rclgo nhúng thẳng vào agent — 4. Probe nói chuyện agent qua localhost TCP/gRPC*
## Decision
Sidecar + Unix socket `/run/mechops/agent.sock`, khung NDJSON. Agent không phụ thuộc ROS 2 (Humble/Iron/Jazzy chỉ đổi probe); agent vẫn sống và OTA được khi stack ROS 2 chết — đúng tình huống cần OTA nhất (PRB-03). Loại subprocess: DDS discovery 2–5s mỗi lần gọi, không streaming. Unix socket thay TCP: không mở port mạng, quyền truy cập bằng file permission.
## Consequences
+ Cô lập vòng đời: probe chết → device `degraded`, agent sống. Mode B (nhiều probe/agent) mở sẵn.
− Thêm một tiến trình phải giám sát (heartbeat ping/pong trong Probe API); contract probe phải versioned (`apiVersion`, PRB-01).
