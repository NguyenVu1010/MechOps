# ADR-0004: Probe tách khỏi agent, nói chuyện qua Unix socket
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ dev-plan mục 1.5, chốt 2026-07-09)
- Covers: [PRB-02, PRB-03, PRB-06]
## Context
Agent cần dữ liệu ROS 2 (node, topic hz, battery, pose) nhưng không được phụ thuộc phiên bản ROS 2 của robot: mỗi distro có ABI và client library riêng, còn agent là một binary cho mọi robot. Agent cũng phải sống và OTA được đúng lúc stack ROS 2 chết.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. ros2-probe sidecar (tiến trình riêng trong môi trường ROS 2 của robot) + Unix socket NDJSON — 2. Agent gọi `ros2 node list` bằng subprocess — 3. Nhúng client ROS 2 thẳng vào agent — 4. Probe nói chuyện agent qua localhost TCP/gRPC*
## Decision
Sidecar + Unix socket `/run/mechops/agent.sock`, khung NDJSON. Ngôn ngữ của probe quyết ở ADR-0013. Agent không phụ thuộc ROS 2 (Humble/Iron/Jazzy chỉ đổi probe); agent vẫn sống và OTA được khi stack ROS 2 chết — đúng tình huống cần OTA nhất (PRB-03). Loại subprocess: DDS discovery 2–5s mỗi lần gọi, không streaming. Unix socket thay TCP: không mở port mạng, quyền truy cập bằng file permission.
## Consequences
+ Cô lập vòng đời: probe chết → device `degraded`, agent sống. Mode B (nhiều probe/agent) mở sẵn.
− Thêm một tiến trình phải giám sát (heartbeat ping/pong trong Probe API); contract probe phải versioned (`apiVersion`, PRB-01).

_Chuẩn hoá 2026-11-08 trước khi tách repo (ADR-0019): bỏ lập luận dựa trên agent Go và bỏ chọn ngôn ngữ probe (Python) khỏi ADR này; ngôn ngữ probe chỉ nằm ở ADR-0013._
