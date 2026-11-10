# ADR backlog

Đã hồ sơ hóa 0002..0009 (open-core, EMQX, probe unix socket, OTA rollback tại agent, TimescaleDB, SSE, tenant trong topic, Go vs C++) — 2026-07-15.

Đã hồ sơ hóa 0010..0011 (toolchain dev trong Docker + `./mo`; cưỡng chế luật bằng máy thay vì văn bản) — 2026-08-23.

Đã hồ sơ hóa 0012..0017 (Rust cho agent, probe C++ rclcpp, EMQX BSL 1.1, OTA tự xây vs Mender, PKI CA trong server, Next.js) — 2026-10-18. Kế hoạch tổng thể đi kèm: `docs/product/08-master-plan.md`.

Đã hồ sơ hóa 0018 (môi trường mô phỏng ROS 2 trên máy dev: WSL2 + container theo distro + WSLg) — 2026-10-21. File: `sim/ros2/`.

Đã hồ sơ hóa 0019 (tách repo theo đội, repo chính là umbrella ghim submodule theo tag) — 2026-11-08. Cùng ngày, đợt chuẩn hoá một lần sửa trực tiếp 0001, 0002, 0004, 0009, 0010, 0012, 0013, 0015, 0018 để không còn ADR supersede một phần (ADR-0019 mục "Đợt chuẩn hoá"); 0018 nay ghi Jazzy trên 24.04. Kế hoạch tách và bảng xếp chỗ cho mọi ADR: `docs/product/09-tach-repo.md`. Từ sau khi tách, ADR mới chạm từ hai repo trở lên đánh số tiếp ở đây; ADR riêng một đội dùng `WEB-`, `ROB-`, `MOB-` trong repo của đội đó. Danh sách dưới đây đã được xếp sẵn chỗ ở mục 3 của file kế hoạch.

Đã hồ sơ hóa 0020 (hợp đồng giữa robotics-backend, platform và robot: lease qua MQTT, lệnh qua REST, sự kiện qua MQTT, không thêm giao thức) — 2026-11-10. Đóng mục "robotics-backend ra lệnh qua platform hay nối thẳng MQTT". Bản sao ở cả ba repo đội.

Chờ viết khi build:
- **Remote terminal: PTY qua WebSocket mTLS hay qua WireGuard** — spec v2 mục 5 và
  dev-plan mục 1.6 đang mâu thuẫn. Viết trước M5, kèm quyết định WireGuard có còn
  trong scope Phase 0 không.
- **Broker cho kênh SaaS Phase 1**: mua EMQX Commercial hay broker nhúng Go (ADR-0014).
  Cần số đo LOD-01/02.
- **k3s cho SaaS Phase 1** — đụng constitution #5 (Compose). Phải là ADR supersede.
- WebRTC/Pion cho video (Phase 1, ADR-0001 Consequences). Phía agent là `webrtc` crate
  Rust — spike trước (ADR-0012 Consequences).
- Foxglove thay tự xây visualization (Phase 1)
- JWT tự triển khai vs Keycloak (khi multi-tenant)
- **Rust cho server?** Xét sau M3 nếu team đã thạo Rust (ADR-0012 option 2). Không
  trước đó.
- **zenoh-probe**: rmw_zenoh đã Tier 1 từ ROS 2 Kilted; probe nói Zenoh thay DDS có thể
  bỏ được ma trận distro của ADR-0013. Xét Phase 1 khi có robot chạy Zenoh thật.
- **Review PR bằng `anthropics/claude-code-action`** — hiện dùng `REVIEW.md` +
  `/code-review` local (ADR-0011 Decision). Xét lại khi có người thứ ba vào dự án.
- **Headless `claude -p` chạy task từ issue có label `agent-ok`** — nấc tự động hoá
  thứ 2 trong `06-spec-management.md`, dự kiến cuối M2 khi đã đủ tin cậy.

Xếp chỗ sau khi tách repo (ADR-0019) cho các đề tài chưa viết, kể cả các mục ở trên:

| Đề tài | Chỗ | Viết trước |
|---|---|---|
| Agent lõi mỏng, profile do server giao, probe và middleware đi qua OTA | repo chính | M2 |
| Bản khai năng lực khi enroll, vùng `ext.<vendor>.*`, server chấp nhận spec N và N-1 | repo chính | code M1 |
| Remote terminal qua WebSocket mTLS hay WireGuard | repo chính | M5 |
| k3s cho SaaS, WebRTC cho video | repo chính | Phase 1 |
| Review PR bằng `claude-code-action` | repo chính | khi có người thứ ba |
| Công cụ sinh mã từ OpenAPI | `WEB-0001` | M1 |
| Broker cho SaaS, JWT hay Keycloak, Rust cho server | `WEB-` | Phase 1 / multi-tenant / sau M3 |
| zenoh-probe, Foxglove | `ROB-` | Phase 1 |
| Stack mobile | `MOB-0001` | khi đội mobile vào việc |
