# ADR-0018: Môi trường mô phỏng ROS 2 trên máy dev = ROS 2 Jazzy native trong WSL Ubuntu 24.04 cho việc hằng ngày + container theo distro cho ma trận
- Status: accepted
- Date: 2026-10-22
- Covers: [PRB-02, PRB-03, PRB-04, PRB-05]

## Context

Team dev trên Windows 11. Máy founder: i5-14400F, 16 GB RAM, GTX 1070, WSL2 với WSLg bật
(X11 + Wayland), GPU nhìn thấy từ WSL qua `/dev/dxg` + `/usr/lib/wsl/lib`. Chưa có ROS 2 ở
đâu cả.

Cần một chỗ chạy robot giả để: (1) phát triển và chạy test [I] của probe (PRB-01..05)
mà không cần Jetson; (2) demo OTA/telemetry trên robot bất kỳ cho design partner;
(3) build và test probe trên **nhiều distro** (ADR-0013: ma trận distro × arch).

Ràng buộc, không phải giải pháp:
- Robot ngoài đời chạy Humble (22.04, EOL 05/2027) nhiều nhất và Jazzy (24.04, LTS tới
  2029) cho robot mới. Lyrical (26.04, 05/2026) chưa có robot nào chạy. Ma trận probe phải
  chạy được cả ba.
- Mỗi bản Ubuntu chỉ cài native được một distro. Kho `packages.ros.org` ngày 2026-10-22:
  Jazzy trên 24.04 có 3.961 gói, Humble trên 22.04 có 3.786, Lyrical trên 26.04 có 2.684.
  TurtleBot4 sim chỉ có trên Jazzy.
- Founder muốn môi trường hằng ngày nằm thẳng trong Ubuntu WSL, không qua Docker: gõ
  `ros2`, `rviz2`, `gz` như trên một máy Ubuntu thật, workspace `~/ros2_ws` là thư mục thật.
- GUI phải ra màn hình Windows có GPU. Team part-time: setup là script idempotent.

## Options đã cân nhắc

1. **Native Lyrical trên WSL 26.04** (bản WSL có sẵn trên máy). Ít gói nhất, không distro
   nào của robot thật.
2. **Native Jazzy trên WSL 24.04.** Distro robot mới đang chạy, nhiều gói nhất, có
   TurtleBot4. Phải cài lại WSL và Docker trong distro mới.
3. **Native Humble trên WSL 22.04.** Distro phổ biến nhất ngoài đời, nhưng EOL 05/2027,
   ngắn hơn đời sản phẩm.
4. **Chỉ container theo distro** (`osrf/ros:<distro>-desktop-full` + WSLg). Ba distro cạnh
   nhau, cùng image dùng cho CI probe. Hỏng: mọi thao tác hằng ngày phải đi qua
   `docker exec`, workspace là volume. Founder không muốn làm việc hằng ngày kiểu này.
5. **RoboStack (conda/pixi)**: nhiều distro không cần Docker. Gói cộng đồng, Gazebo trễ,
   khác robot thật chạy apt.
6. **VM Hyper-V / dual boot**: GPU passthrough khó, vận hành nặng nhất.

## Decision

Kết hợp (2) và (4), mỗi cái một việc:

- **Hằng ngày: ROS 2 Jazzy native trong WSL `Ubuntu-24.04`**, cùng Gazebo Harmonic, cài
  bằng `sim/ros2/install-native.sh`. Script idempotent: kho `ros2-apt-source` chính thức,
  desktop-full + Gazebo + Nav2 + MoveIt + ros2_control + SLAM Toolbox + TurtleBot3/4 sim,
  `rosdep`, workspace `~/ros2_ws`, `~/.bashrc` source sẵn. Distro tự chọn theo bản Ubuntu
  (noble → Jazzy, jammy → Humble, resolute → Lyrical). Cờ `--docker` cài Docker CE trong
  cùng distro cho `./mo` (ADR-0010).
- **Ma trận distro: container** `mechops/rossim:{humble,jazzy,lyrical}` qua
  `sim/ros2/compose.yml` và lệnh `rossim`. Chỉ dùng khi cần test probe trên Humble hoặc
  Lyrical, hoặc trong CI. `network_mode: host` nên container thấy agent và topic của
  ROS native trên cùng máy.
- **Hiển thị GUI:** khối do script quản lý trong `~/.bashrc` đặt `GALLIUM_DRIVER=d3d12`
  (Mesa dùng GPU qua D3D12, không rơi về llvmpipe) và `QT_QPA_PLATFORM=xcb`; container
  đặt cùng biến trong `compose.yml`. WSL phải ≥ 3.0.3: bản 2.7.12 có lỗi cửa sổ WSLg
  trống, tiêu đề `[WARN:COPY MODE]`, chỉ hiện icon trên taskbar.
- Cả native và container dùng chung `optional-packages.txt` để danh sách gói mô phỏng chỉ
  có một bản.

## Consequences

- Hai cách chạy ROS trên một máy. Quy ước: không rõ thì dùng native (Jazzy); chỉ gõ
  `rossim` khi câu hỏi có chữ "Humble" hoặc "Lyrical". Ghi trong `sim/ros2/README.md`.
- ros2-probe (ADR-0013) viết và test trên native Jazzy trước, rồi chạy ma trận bằng
  `rossim <distro> colcon test`.
- Robot demo mặc định là TurtleBot3 trong Gazebo Harmonic; TurtleBot4 có sẵn trên native.
- Isaac Sim, perception GPU nặng: cần máy Linux native, không hứa trên WSL.
- `.wslconfig` 10 GB RAM / 12 CPU / 8 GB swap, có hiệu lực sau `wsl --shutdown`.
  Máy 16 GB không chừa được hơn: thử 12 GB đã làm Windows thiếu RAM (2026-10-21).
- Môi trường này là của dev, không phải sản phẩm. Agent/server không import gì ở đây.
  Theo ADR-0019, `sim/` thuộc repo `mechops-agent`.

_Chuẩn hoá 2026-11-08 trước khi tách repo (ADR-0019): bản gốc chọn Lyrical trên 26.04; founder đổi sang Jazzy trên 24.04 ngay ngày 2026-10-22, nội dung trên là cấu hình đang chạy._
