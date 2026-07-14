# MechOps — Phase 0 Development Plan

> Đi kèm spec v2.0 · Phạm vi: Phase 0 (Foundation)
> Nguyên tắc xuyên suốt: team part-time → mỗi lựa chọn công nghệ phải tối thiểu hóa chi phí vận hành, không phải tối đa hóa độ "xịn".

---

## 1. Stack — quyết định cụ thể từng lớp

### 1.1 Backend — Go 1.22+
| Hạng mục | Chọn | Lý do / Thay thế đã loại |
|---|---|---|
| HTTP router | `chi` | Nhẹ, stdlib-style, không magic. Loại Gin (nhiều magic), Echo (tương đương nhưng chi gần stdlib hơn) |
| DB access | `pgx` + `sqlc` | SQL thuần sinh code type-safe — không ORM. Loại GORM (ẩn query, khó debug performance với time-series) |
| Migration | `golang-migrate` | Chuẩn de-facto, chạy được trong CI lẫn container init |
| MQTT client | `eclipse/paho.golang` | Bản mới hỗ trợ MQTT 5 (cần cho response topic + user properties trong protocol OTA) |
| Config | env + `caarlos0/env` | Không file config phức tạp — 12-factor, hợp Docker Compose |
| Logging | `slog` (stdlib) | Structured log JSON, đủ dùng, 0 dependency |

### 1.2 MQTT Broker — EMQX (open source)
Chọn **EMQX** thay vì Mosquitto vì 3 thứ Phase 0 cần ngay:
- **Auth/ACL qua PostgreSQL**: device certificate + ACL per-device (robot A không đọc được topic robot B) cấu hình bằng SQL, không file text như Mosquitto
- Dashboard quản trị built-in — debug connection khi deploy tại vendor đỡ tốn thời gian
- MQTT 5 đầy đủ (shared subscription — cần khi scale API server sau này)

Trade-off chấp nhận: nặng hơn Mosquitto (~200MB RAM) — không đáng kể trên VPS/edge server, chỉ đáng kể nếu chạy broker trên robot (không phải kiến trúc của ta).

### 1.3 Database — PostgreSQL 16 + TimescaleDB
Một database duy nhất cho cả relational (users, devices, deployments) lẫn time-series (telemetry):
- Telemetry vào **hypertable** với compression + retention policy (raw 7 ngày, downsample 1-phút giữ 90 ngày)
- Loại InfluxDB: thêm 1 hệ query language + 1 service phải vận hành, không đáng khi TimescaleDB đủ tốt tới hàng trăm nghìn point/giây
- Redis: **chưa dùng** — Postgres `LISTEN/NOTIFY` + in-memory cache trong API server đủ cho single-tenant. Thêm Redis khi có số đo chứng minh cần.

### 1.4 Frontend — Next.js 15 + TypeScript
| Hạng mục | Chọn |
|---|---|
| UI kit | Tailwind + shadcn/ui (copy-in component, dễ theming white-label bằng CSS variables) |
| Charts | ECharts (time-series lớn mượt hơn Recharts, canvas-based) |
| Realtime | **SSE từ API server** — API server subscribe MQTT nội bộ rồi đẩy SSE ra dashboard. Broker không bao giờ expose ra Internet. Loại phương án dashboard connect thẳng MQTT-over-WebSocket (lộ broker, khó kiểm soát ACL theo user) |
| State | TanStack Query + SSE invalidation — không cần Redux/Zustand ở quy mô này |

### 1.5 Agent — Go single binary + ROS 2 sidecar
Vấn đề kỹ thuật quan trọng nhất của agent: **Go không nói chuyện DDS/ROS 2 tự nhiên** (rclgo chưa production-ready). Giải pháp 2 tầng:

```
mechops-agent (Go, single binary, systemd service)
├── Telemetry hệ thống: CPU/RAM/disk/net (gopsutil), battery
├── MQTT client (mTLS, device cert)
├── OTA executor (Docker SDK for Go)
├── PTY server (remote terminal)
├── WireGuard config manager
└── Unix socket ← ros2-probe

ros2-probe (Python/rclpy, chạy trong container ROS 2 của robot)
├── node list + trạng thái, topic hz, /battery_state, /pose (AMR profile)
└── đẩy JSON qua Unix socket cho agent
```

Lý do tách: agent không phụ thuộc phiên bản ROS 2 (Humble/Iron/Jazzy đều chạy — chỉ probe đổi), agent vẫn sống và OTA được kể cả khi stack ROS 2 chết — **đây chính là tình huống cần OTA nhất**.
Loại phương án gọi `ros2 node list` bằng subprocess: chậm (2–5s mỗi lần khởi tạo DDS discovery), không streaming được.

### 1.6 Remote terminal — PTY qua kênh sẵn có, không SSH
Agent mở PTY, stream qua WebSocket (mTLS) tới server, dashboard render bằng xterm.js. Server ghi **audit log toàn bộ phiên** (yêu cầu spec mục 9).
Loại phương án SSH qua WireGuard: phải quản lý SSH key per-user per-robot, không audit tập trung được. WireGuard vẫn giữ nhưng chỉ làm kênh dự phòng/kỹ thuật viên, không phải đường chính của tính năng terminal.

### 1.7 OTA infrastructure
- **Docker Registry v2** (container `registry:2`) chạy trong mỗi instance — vendor push image ROS 2 app vào đây
- Manifest deploy = file JSON versioned trong Postgres: image tag, env, device group, health check định nghĩa
- Agent pull image → stop container cũ (giữ nguyên) → start mới → chạy health check → pass thì xóa tag cũ sau N giờ, fail thì **tự rollback không cần lệnh từ server** (robot có thể đang offline với server đúng lúc đó)

### 1.8 DevOps
| Hạng mục | Chọn |
|---|---|
| Monorepo | 1 repo: `/agent`, `/server`, `/dashboard`, `/probe`, `/deploy`, `/docs` |
| CI | GitHub Actions: lint + test + build mỗi PR |
| Agent release | `goreleaser` → binary arm64 + amd64, install script `curl \| sh` |
| Server release | Docker image + `docker-compose.yml` versioned, script `install.sh` cho vendor |
| Test hardware | Jetson + Pi làm test matrix bắt buộc trước mỗi release OTA |

---

## 2. Thiết kế protocol MQTT (khung — chi tiết hóa ở M0)

```
mechops/{deviceId}/telemetry        ← agent đẩy, QoS 0, 1–5s/lần
mechops/{deviceId}/status           ← retained: online/offline (LWT)
mechops/{deviceId}/ros              ← trạng thái node/topic từ probe, QoS 0
mechops/{deviceId}/ota/command      → server đẩy lệnh deploy/rollback, QoS 1
mechops/{deviceId}/ota/progress     ← agent báo tiến độ, QoS 1
mechops/{deviceId}/logs/{stream}    ← khi user bật log tail
```
- Payload: JSON Phase 0 (dễ debug); cân nhắc CBOR khi có số đo băng thông thực tế
- Offline-first: agent buffer telemetry vào SQLite local khi mất mạng, replay khi reconnect
- Protocol spec này nằm trong phần **open source** (spec v2.0 mục 7)

---

## 3. Milestones — chia theo quỹ part-time (~15–20h/tuần cả team)

### M0 · Tuần 1–2 — Skeleton
- Monorepo + CI + docker-compose chạy được (EMQX, Postgres, API rỗng, dashboard Hello)
- **Viết protocol spec MQTT v0.1** (file markdown trong repo — đây là hợp đồng giữa agent và server, viết trước khi code)
- DoD: `docker compose up` → dashboard login được bằng user seed

### M1 · Tuần 3–6 — Agent v0 + provisioning
- Agent: heartbeat, telemetry hệ thống, LWT online/offline
- Provisioning: sinh device cert, lệnh `mechops-agent enroll --token XXX`
- Chạy thật trên Jetson + Pi
- DoD: dashboard thấy 2 thiết bị thật online/offline realtime

### M2 · Tuần 7–10 — Dashboard v0 + ROS probe
- Device list, device detail (telemetry chart ECharts), auth + RBAC admin/viewer
- ros2-probe: node/topic status, AMR profile (battery, pose)
- DoD: robot ROS 2 (sim hoặc thật) hiện node status + battery trên dashboard

### M3 · Tuần 11–16 — OTA v1 ⭐ (trọng tâm Phase 0)
- Registry, manifest, deploy flow, health check, auto-rollback phía agent
- Staged rollout: chọn device/group, deploy tuần tự có confirm
- Test bắt buộc: rút điện giữa lúc pull image, mất mạng giữa deploy, health check fail → tự rollback
- DoD: demo deploy version lỗi → robot tự về version cũ, không cần can thiệp

### M4 · Tuần 17–20 — Alert + Remote log
- Rule engine tối giản: offline > X phút, battery < Y%, node chết
- Email + Telegram/Zalo webhook
- Log tail realtime + download từ robot
- DoD: rút mạng robot → nhận cảnh báo Telegram trong 1 phút

### M5 · Tuần 21–26 — Remote terminal + White-label + Installer
- PTY qua WebSocket + xterm.js + audit log phiên
- Theming: logo + màu qua CSS variables, cấu hình per-instance
- `install.sh` một lệnh cho vendor + tài liệu deploy
- DoD: người ngoài team cài được instance mới trong < 30 phút theo docs

### M6 · Tuần 27+ — Hardening với design partner
- Deploy lên fleet thật của design partner, sửa theo phản hồi
- Load test telemetry (mô phỏng 50 robot bằng script)
- Security pass: rà ACL MQTT, rotate cert, review audit log

**Mốc design partner:** bắt đầu tiếp cận từ M2 (có demo được), ký ở M3–M4 — khớp mốc "tháng 3–4" trong spec.

---

## 4. Thứ tự build trong từng milestone

1. **Protocol/schema trước, code sau** — mọi tính năng bắt đầu bằng cập nhật protocol spec + SQL schema
2. **Agent trước, dashboard sau** — dashboard chỉ render dữ liệu đã chảy về; tránh xây UI cho dữ liệu chưa tồn tại
3. **Happy path trước, edge case theo checklist** — mỗi tính năng có checklist edge case riêng (mất mạng / mất điện / disk đầy) xử lý trong cùng milestone, không dồn về sau
4. Với Claude Code: protocol spec + SQL schema trong repo chính là context tốt nhất — viết kỹ 2 file đó thì phần code sinh ra sẽ nhất quán

---

## 5. Những thứ cố tình KHÔNG làm ở Phase 0

| Không làm | Làm thay thế | Xét lại khi |
|---|---|---|
| Kubernetes/Helm | Docker Compose | Có khách yêu cầu HA thật |
| Redis | Postgres LISTEN/NOTIFY | Có số đo bottleneck |
| gRPC/GraphQL | REST + SSE | Multi-tenant Phase 1 |
| OS-level OTA | App-level (Docker) | Khách cần update kernel/driver → wrap RAUC |
| Video/WebRTC | — | Phase 1 (ưu tiên #3 đã chốt) |
| Mobile app | Dashboard responsive | Có yêu cầu thật từ vendor |
| Tự viết auth phức tạp | JWT + bcrypt, 2 role | Keycloak khi multi-tenant |
