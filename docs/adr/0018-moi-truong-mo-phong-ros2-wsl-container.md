# ADR-0018: Môi trường mô phỏng ROS 2 trên máy dev = ROS 2 native trong WSL cho việc hằng ngày + container theo distro cho ma trận
- Status: accepted
- Date: 2026-10-22
- Covers: [PRB-02, PRB-03, PRB-04, PRB-05]

## Context

Team dev trên Windows 11. Máy founder: WSL2 Ubuntu 26.04, Docker CE 29 chạy trong
WSL (systemd), WSLg bật (X11 + Wayland), GPU GTX 1070 nhìn thấy từ WSL qua
`/dev/dxg` + `/usr/lib/wsl/lib`, 16 GB RAM, đĩa dư 900 GB. Chưa có ROS 2 ở đâu cả.

Cần một chỗ chạy robot giả để: (1) phát triển và chạy test [I] của probe (PRB-01..05)
mà không cần Jetson; (2) demo OTA/telemetry trên robot bất kỳ cho design partner;
(3) build và test probe trên **nhiều distro** (ADR-0013: ma trận distro × arch).

Ràng buộc, không phải giải pháp:
- Robot ngoài đời chạy Humble (22.04, EOL 05/2027) nhiều nhất, Jazzy (24.04, LTS tới
  2029) cho robot mới, Lyrical (26.04, 05/2026, LTS) chưa phổ biến. Ma trận probe phải
  chạy được cả ba.
- Ubuntu 26.04 trong WSL chỉ cài native được Lyrical. Kho `packages.ros.org` ngày
  2026-10-22 có 2.684 gói Lyrical cho 26.04, đủ desktop-full, ros-gz (Gazebo Jetty),
  Nav2, MoveIt, ros2_control, SLAM Toolbox, TurtleBot3 Gazebo; thiếu TurtleBot4 sim và
  metapackage `turtlebot3`.
- Founder muốn môi trường làm việc hằng ngày nằm thẳng trong Ubuntu WSL đã có, không
  phải qua Docker: gõ `ros2`, `rviz2`, `gz` như trên một máy Ubuntu thật, workspace
  `~/ros2_ws` là thư mục thật.
- GUI phải ra màn hình Windows có GPU. Team part-time: setup là script idempotent.

## Options đã cân nhắc

1. **Chỉ native trên WSL 26.04**: `apt install ros-lyrical-desktop-full`. Đơn giản nhất,
   nhưng không có Humble/Jazzy để test probe với distro robot thật đang dùng.
2. **Chỉ container theo distro** (`osrf/ros:<distro>-desktop-full` + WSLg): ba distro
   cạnh nhau, cùng image dùng cho CI probe. Hỏng: mọi thao tác hằng ngày phải đi qua
   `docker exec`, workspace là volume, GUI trong container phải chỉnh Mesa
   (`GALLIUM_DRIVER=d3d12`, đo ngày 2026-10-21 mới thấy). Founder không muốn làm việc
   hằng ngày kiểu này.
3. **Cài lại WSL thành Ubuntu 24.04 + Jazzy native**: Jazzy phổ biến hơn Lyrical,
   nhưng phá Docker và việc khác đang chạy trong distro hiện có.
4. **RoboStack (conda/pixi)**: nhiều distro không cần Docker. Gói cộng đồng, Gazebo
   trễ, khác robot thật chạy apt. Cần ADR riêng.
5. **VM Hyper-V / dual boot**: GPU passthrough khó, vận hành nặng nhất.

## Decision

Kết hợp (1) và (2), mỗi cái một việc:

- **Hằng ngày: ROS 2 Lyrical native trong WSL Ubuntu 26.04**, cài bằng
  `sim/ros2/install-native.sh` (idempotent, kho `ros2-apt-source` chính thức,
  desktop-full + Gazebo + Nav2 + MoveIt + ros2_control + TurtleBot3 sim, `~/.bashrc`
  source sẵn, workspace `~/ros2_ws`). Đây là nơi viết probe, chạy Gazebo, demo.
- **Ma trận distro: container** `mechops/rossim:{humble,jazzy,lyrical}` qua
  `sim/ros2/compose.yml` và lệnh `rossim`. Chỉ dùng khi cần test probe trên Humble/
  Jazzy hoặc trong CI. `network_mode: host` nên container thấy agent và topic của
  ROS native trên cùng máy.
- Cả hai dùng chung `optional-packages.txt` để danh sách gói mô phỏng chỉ có một bản.

## Consequences

- Hai cách chạy ROS trên một máy. Quy ước: không rõ thì dùng native; chỉ gõ `rossim`
  khi câu hỏi có chữ "Humble" hoặc "Jazzy". Ghi trong `sim/ros2/README.md`.
- ros2-probe (ADR-0013) build và test trong ba image container; dev viết probe trên
  native Lyrical trước, rồi chạy ma trận bằng `rossim <distro> colcon test`.
- Robot demo mặc định là TurtleBot3 trong Gazebo Jetty (native) và Harmonic/Fortress
  (container). TurtleBot4 sim chỉ có trong image jazzy.
- Isaac Sim, perception GPU nặng: cần máy Linux native, không hứa trên WSL.
- `.wslconfig` 10 GB RAM / 12 CPU / 8 GB swap, có hiệu lực sau `wsl --shutdown`.
  Máy 16 GB không chừa được hơn: thử 12 GB đã làm Windows thiếu RAM (2026-10-21).
- Môi trường này là của dev, không phải sản phẩm. Agent/server không import gì ở đây.
