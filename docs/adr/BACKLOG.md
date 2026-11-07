# ADR backlog

Đã hồ sơ hóa 0002..0009 (open-core, EMQX, probe unix socket, OTA rollback tại agent, TimescaleDB, SSE, tenant trong topic, Go vs C++) — 2026-07-15.

Đã hồ sơ hóa 0010..0011 (toolchain dev trong Docker + `./mo`; cưỡng chế luật bằng máy thay vì văn bản) — 2026-08-23.

Đã hồ sơ hóa 0012..0017 (Rust cho agent, probe C++ rclcpp, EMQX BSL 1.1, OTA tự xây vs Mender, PKI CA trong server, Next.js) — 2026-10-18. Kế hoạch tổng thể đi kèm: `docs/product/08-master-plan.md`.

Đã hồ sơ hóa 0018 (môi trường mô phỏng ROS 2 trên máy dev: WSL2 + container theo distro + WSLg) — 2026-10-21. File: `sim/ros2/`.

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
