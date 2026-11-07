# ADR-0013: ros2-probe viết bằng C++ (rclcpp), không phải Python (rclpy)
- Status: accepted
- Date: 2026-10-18
- Covers: [PRB-02, PRB-06]
- Supersedes: ADR-0004 **phần ngôn ngữ probe** (kiến trúc sidecar + Unix socket + NDJSON giữ nguyên)

## Context

ADR-0004 chọn sidecar probe nói chuyện với agent qua Unix socket, và ghi probe là
"Python/rclpy". Lý do kiến trúc (agent không phụ thuộc ROS 2, sống khi stack ROS chết)
vẫn đúng và không bàn lại ở đây. Chỉ bàn ngôn ngữ của probe.

Hai dữ kiện mới: (1) team có kinh nghiệm C++ và chưa có kinh nghiệm Go/Rust; probe
là chỗ duy nhất trong hệ thống mà kinh nghiệm đó sinh giá trị ngay từ ngày đầu.
(2) Việc của probe nặng hơn ADR-0004 hình dung: đo hz nhiều topic đồng thời, đọc
`/battery_state`, `/pose`, và ở Phase 1 là pointcloud/image cho bag recorder.
rclpy đuối ở tần số cao vì GIL và chi phí serialize Python.

## Options đã cân nhắc

1. **Python rclpy** (ADR-0004). Chạy source-level trên mọi distro, viết nhanh. Yếu ở
   tần số cao; kéo theo phiên bản Python của distro.
2. **C++ rclcpp.** ← chọn. Ngôn ngữ bản địa của ROS 2, team đã biết, hiệu năng đủ cho
   Phase 1–3. Giá: build theo ma trận distro × arch.
3. **Rust rclrs** (ros2-rust). Cùng ngôn ngữ với agent (ADR-0012), nhưng chưa production,
   kéo colcon vào build, và không cho team C++ việc gì. Xét lại khi rclrs có binary
   release chính thức.

## Decision

`probe/ros2/` viết bằng **C++17 với rclcpp**, build thành image Docker theo ma trận
`{humble, jazzy} × {amd64, arm64}` bằng GitHub Actions matrix. Probe chạy **trong
container ROS 2 của robot** (cùng network namespace DDS), connect vào
`/run/mechops/agent.sock` theo contract Probe API v1 (`specs/probe-api.md`).

Ranh giới an toàn đi kèm (từ ADR-0012): lỗi bộ nhớ trong probe làm **probe** chết,
agent phát hiện qua 3 ping không pong (PRB-03), device chuyển `degraded`. Probe không
bao giờ được nạp vào không gian địa chỉ của agent.

Chốt chặn máy: probe build với `-Wall -Wextra -Werror`, chạy ASan/UBSan trong CI nightly;
`clang-tidy` với bộ rule `cppcoreguidelines-*` mức warning-as-error cho `bugprone-*`.

## Consequences

+ Người giỏi C++ nhất trong team có việc từ ngày đầu, không chờ học Rust.
+ Đo hz hàng chục topic và đọc pointcloud không đụng trần hiệu năng.
+ Không phụ thuộc Python version của distro.
− Mỗi distro ROS 2 mới = thêm một trục ma trận build. Chấp nhận: Docker matrix là
  việc của CI, không phải của người.
− Hai ngôn ngữ hệ thống nữa trong repo (Rust agent, Go server, C++ probe). Probe là
  thành phần nhỏ nhất và cô lập nhất, nên chi phí thêm là một Dockerfile và một job CI.
