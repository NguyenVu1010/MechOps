# MechOps — Kế hoạch phát triển tổng thể theo module

> Ngày chốt: 2026-10-18. Đi kèm `02-dev-plan-phase0.md` (stack), `03-phase-plan-1-4.md`
> (gate từng phase), `05-test-catalog.md` (định nghĩa "xong"). File này nối ba thứ đó
> lại theo trục **giai đoạn → module → vào/ra → nghiệm thu**.
> Khi mâu thuẫn: nghiệm thu theo `05`, công nghệ theo `docs/adr/`, gate phase theo `03`.
> Nguyên tắc chi tiết giảm theo khoảng cách: Phase 0 tới từng module và test ID,
> Phase 1 tới module, Phase 2–4 tới ranh giới kiến trúc.

---

## 0. Kiến trúc chi tiết và bản đồ module

### 0.1 Sơ đồ hệ thống Phase 0

```
┌─ VENDOR INSTANCE (Docker Compose, một node mỗi vendor) ────────────────────────────┐
│                                                                                     │
│  DSH  dashboard (Next.js)  ──HTTPS/SSE──▶  SRV  server (Go)                          │
│                                            ├── api        REST + SSE hub + JWT/RBAC │
│                                            ├── ca         PKI: enroll, sign, renew  │
│                                            ├── ingest     MQTT sub → Timescale      │
│                                            ├── fleet      OTA orchestrator, waves   │
│                                            ├── alert      rule engine + notifier    │
│                                            ├── audit      phiên terminal, lệnh      │
│                                            └── relay      terminal WS ⇄ agent (M5)  │
│                                                 │  sqlc        │ paho MQTT 5        │
│                                                 ▼              ▼                    │
│  DB  PostgreSQL 16 + TimescaleDB      BRK  EMQX 5 (1 node, mTLS, ACL SQL → DB)      │
│  REG Docker Registry v2 (image app ROS 2 của vendor)                                │
└───────────────────────────────────────────────────┬───────────────────▲─────────────┘
                                                    │ MQTT 5 / mTLS      │ HTTPS enroll/renew
                                                    │ 8883                │ pull image (digest)
┌─ ROBOT (Jetson / Pi / IPC, Ubuntu) ────────────────▼───────────────────┴─────────────┐
│  AGT  mechops-agent (Rust, 1 binary tĩnh, systemd, Apache 2.0)                       │
│  ├── identity   key + cert 90 ngày, renew < 30 ngày                                  │
│  ├── transport  trait Publish/Subscribe; impl MQTT (rumqttc v5)                      │
│  ├── telemetry  cpu/mem/disk/net/temp (sysinfo) + gộp data từ probe → envelope       │
│  ├── buffer     SQLite offline: events/state đủ, telemetry downsample 30s/24h        │
│  ├── probe_hub  Unix socket /run/mechops/agent.sock, NDJSON, N probe, ping 10s       │
│  ├── ota        state machine (SQLite trước hành động) + bollard Docker + health      │
│  ├── cmd        dispatcher cmd/cmd-res, expiresAt                                    │
│  ├── pty        terminal (M5)      └── logs  tail có TTL (M4)                        │
│        ▲ Unix socket NDJSON                                                          │
│  PRB  ros2-probe (C++ rclcpp, chạy TRONG container ROS 2 của robot)                  │
│       node/topic hz · /battery_state · /pose · event ROS_NODE_DOWN                   │
│  APP  container ROS 2 của vendor  ◀── OTA swap theo digest, giữ image cũ            │
└──────────────────────────────────────────────────────────────────────────────────────┘
Chiều phụ thuộc: SRV → specs/ ← AGT ← PRB.  AGT không biết SRV; PRB không biết MQTT.
```

### 0.2 Bảng module

| Mã | Module | Ngôn ngữ | Thư mục | Phase | ADR |
|---|---|---|---|---|---|
| SPEC | Hợp đồng MQTT + Probe API + REST | AsyncAPI 3, JSON Schema, OpenAPI | `specs/` | 0 | 0001, 0008 |
| PROTO-GO | Kiểu Go sinh từ schema, topic const | Go | `protocol/` | 0 | 0009 |
| PROTO-RS | Kiểu Rust sinh từ schema (typify) | Rust | `agent/crates/mechops-protocol` | 0 | 0012 |
| AGT | mechops-agent | Rust | `agent/` | 0 | 0005, 0012, 0016 |
| PRB-ROS | ros2-probe | C++ rclcpp | `probe/ros2/` | 0 | 0004, 0013 |
| SRV | API server + Fleet Manager + CA | Go | `server/` | 0 | 0007, 0009, 0015, 0016 |
| DB | Schema, migration, retention | SQL (golang-migrate, sqlc) | `server/migrations`, `server/queries` | 0 | 0006 |
| BRK | Cấu hình EMQX: mTLS, ACL SQL | HOCON + SQL | `deploy/emqx/` | 0 | 0003, 0014 |
| REG | Docker Registry v2 | cấu hình | `deploy/` | 0 | 0015 |
| DSH | Dashboard | Next.js + TS | `dashboard/` | 0 | 0007, 0017 |
| DEP | Compose, install.sh, backup/restore | bash, YAML | `deploy/` | 0 | 0010 |
| SIM | Agent giả lập cho test [I] và LOD | Rust (feature flag của AGT) | `agent/` | 0 | — |
| PRB-VDA | vda5050-probe | Rust hoặc Go (ADR khi làm) | `probe/vda5050/` | 1 | — |
| VID | WebRTC view-only: agent track + server signaling + coturn | Rust (`webrtc`) + Go (Pion) | `agent/`, `server/` | 1 | ADR chờ |
| CP | Control plane: license, usage, signup/billing | Go | `controlplane/` | 1 | ADR chờ |
| PRB-OPCUA, PRB-MODBUS | Probe công nghiệp | Rust/Go | `probe/` | 2 | ADR chờ |
| ALM | Alarm center (ack, escalation, ca kíp) | Go + DSH | `server/` | 2 | — |
| DATA | Tiering Parquet/MinIO, replay, dataset builder | Rust (Arrow, DataFusion) | `data/` | 3 | ADR chờ |
| AI | Anomaly, predictive maintenance | Python/Rust | `ai/` | 4 | ADR chờ |

### 0.3 Bốn luồng đầu-cuối Phase 0

**Enroll (PRV):** dashboard tạo token → vendor chạy `mechops-agent enroll --server --token`
→ AGT.identity sinh key, CSR → `POST /v1/enroll` → SRV.ca kiểm token (hash, TTL, chưa dùng),
sinh agentId, ký cert CN=agentId 90 ngày, ghi `agents` + đánh dấu token trong một
transaction → trả cert + CA chain + cấu hình MQTT → AGT lưu `/var/lib/mechops/identity/`
→ connect EMQX mTLS → BRK verify cert, username=CN, tra ACL SQL → AGT publish
`agents/{agentId}/status` retained + đăng ký LWT → SRV.ingest nhận → DSH thấy online.

**Telemetry (TEL, PRB):** PRB-ROS gửi `data` NDJSON mỗi 2s → AGT.probe_hub → AGT.telemetry
gộp với metrics hệ thống thành envelope `v/ts/seq/metrics/profiles` → AGT.transport
publish QoS 0 → SRV.ingest batch insert hypertable `telemetry` (profiles JSONB) → SRV.api
đẩy SSE `telemetry:{deviceId}` → DSH vẽ ECharts. Mất mạng: AGT.buffer ghi SQLite,
reconnect replay theo `seq` giữ `ts` gốc.

**OTA (OTA):** vendor push image vào REG → DSH tạo deployment (manifest + nhóm + wave)
→ SRV.fleet gửi `ota.deploy` QoS 1 có `expiresAt` tới agent wave 1 → AGT.cmd kiểm hạn
→ AGT.ota: ghi `DOWNLOADING` SQLite → pull theo digest (bollard) → ghi `VERIFYING` →
so digest → ghi `SWITCHING` → stop container cũ (giữ image) → start mới → ghi
`HEALTH_CHECK` → chạy health check theo manifest → pass: `SUCCESS`, dọn image cũ sau
`keepPreviousHours`; fail hoặc crash-loop: `ROLLING_BACK` → start lại cũ → `ROLLED_BACK`.
Mọi chuyển state publish `ota/state` retained → SRV.fleet chờ SUCCESS toàn wave rồi
mới sang wave 2; một fail là dừng. Boot lên thấy state dở dang = fail = rollback.

**Terminal (TRM, M5):** DSH mở phiên (role admin) → SRV.relay tạo session, ghi audit →
gửi `cmd` `terminal.open` → AGT.pty mở PTY, mở WebSocket mTLS ra SRV.relay → luồng
byte hai chiều, SRV.audit ghi toàn bộ input/output → đóng hoặc rớt mạng 30s → PTY kill.

---

## 1. Phân tích vào/ra từng module Phase 0

Mỗi dòng: **Vào** (nhận gì, từ đâu) · **Ra** (phát gì, tới đâu) · **Giữ** (state bền)
· **Hỏng phải xử** (lỗi bắt buộc có hành vi định nghĩa) · **Test ID**.

### AGT — mechops-agent (Rust)

| Sub-module | Vào | Ra | Giữ | Hỏng phải xử | Test ID |
|---|---|---|---|---|---|
| identity | token (CLI), cert hiện tại, đồng hồ hệ thống | CSR → SRV; cert mới; sự kiện `cert.expiring` | key, cert, CA chain (0600) | token sai/hết hạn: lỗi rõ, exit; cert hết hạn: hướng dẫn, không crash-loop; renew thất bại: thử lại backoff tới hạn | PRV-01..04 |
| transport | cấu hình MQTT, cert | publish/subscribe theo trait; LWT đăng ký lúc connect | không | mất mạng: reconnect backoff; broker từ chối ACL: log, không retry vô hạn; payload > 64 KB: từ chối trước khi publish | ACL-01..04, TEL-03 |
| telemetry | sysinfo, `data` từ probe_hub, cấu hình interval | envelope telemetry QoS 0 mỗi 2s; `state` retained khi đổi | seq monotonic (persist) | probe không có data: chỉ metrics hệ thống; clock lệch > 30s: event `agent.clock_skew` | TEL-01, TEL-02, TEL-06, TEL-07 |
| buffer | events/state/telemetry khi offline | replay đúng topic, đúng `seq`, `ts` gốc | SQLite `buffer.db` | disk gần đầy: downsample mạnh hơn rồi bỏ telemetry cũ nhất, không bỏ events; DB hỏng: tạo lại + event | TEL-04, TEL-05 |
| probe_hub | kết nối Unix socket, `hello`, `data`, `event`, `pong`, `cmdRes`, `logChunk` | `helloAck`, `ping` 10s, `cmd`; inventory hợp nhất retained | danh sách probe sống | `apiVersion` lạ: `accepted:false`; 3 ping không pong: devices `degraded` + event; probe reconnect: không nhân đôi inventory | PRB-01, PRB-03, PRB-04, PRB-05 |
| cmd | `cmd` QoS 1 | `cmd/res` accepted/rejected/done/failed | cmdId đã xử (chống lặp QoS 1) | `expiresAt` quá hạn: `rejected/expired`; action lạ: `rejected/unsupported`; lệnh trùng cmdId: trả kết quả cũ | OTA-08, OTA-10 |
| ota | manifest, Docker daemon, health check | `ota/state` retained mỗi chuyển state | SQLite: state, current, target, deploymentId | xem mục 0.3; thêm: disk không đủ: fail sạch ở DOWNLOADING; registry không tới: retry backoff rồi FAILED; digest sai: FAILED không start | OTA-01..07, OTA-11, OTA-12 |
| logs | `logs.start/stop`, log từ probe hoặc journald | `logs/{stream}` QoS 0 | TTL phiên | quên tắt: tự tắt sau 15 phút | TRM-04 |
| pty | `terminal.open`, byte từ relay | byte PTY ra relay | không | rớt mạng 30s: kill PTY, không mồ côi | TRM-01, TRM-03 |

### PRB-ROS — ros2-probe (C++)

| Vào | Ra | Giữ | Hỏng phải xử | Test ID |
|---|---|---|---|---|
| ROS graph (node list, topic hz), `/battery_state`, `/pose` hoặc TF, cấu hình profile AMR, `cmd` từ agent | `hello` (devices, capabilities), `data` mỗi 2s, `event` (ROS_NODE_DOWN ≤ 10s), `pong`, `logChunk` | không (stateless, agent giữ) | socket agent chưa có: thử lại 5s; DDS discovery chậm: báo `nodesTotal` theo cấu hình kỳ vọng; node biến mất: event một lần, clear khi về | PRB-02, PRB-06 |

### SRV — server (Go)

| Package | Vào | Ra | Giữ (bảng) | Hỏng phải xử | Test ID |
|---|---|---|---|---|---|
| ca | `POST /v1/enroll` (token, CSR), `POST /v1/agents/me/renew` (mTLS) | cert, CA chain, cấu hình MQTT | `enroll_tokens`, `agents`, khoá CA (volume) | token dùng hai lần cùng lúc: transaction + unique; CSR CN khác agentId: từ chối | PRV-01..04 |
| ingest | mọi topic `mechops/v1/+/#` qua shared subscription | insert `telemetry` (batch 1s), upsert `device_state`, insert `events`, cập nhật `agents.online` từ status/LWT; publish nội bộ cho SSE hub | hypertable `telemetry`, `events`, `device_state`, `ota_state` | payload lệch schema: drop + đếm metric, không chết; replay muộn: ghi theo `ts` gốc; LWT: mọi device trong inventory → offline | TEL-03, TEL-04, TEL-07, LOD-01, LOD-02 |
| api | REST từ DSH (JWT), SSE subscribe | JSON, dòng SSE theo tenant/device | `users`, `sessions` | viewer gọi API admin: 403; SSE quá nhiều client: giới hạn + 429 | TRM-02, WLB-01 |
| fleet | deployment (manifest, nhóm, wave) từ api; `ota/state` từ ingest | `cmd ota.deploy/rollback` theo wave; trạng thái wave | `deployments`, `deployment_targets`, `waves` | agent fail trong wave: dừng wave sau; agent offline quá `expiresAt`: đánh dấu expired; deploy chồng: từ chối | OTA-08, OTA-09, OTA-10 |
| alert | `device_state`, `events`, `agents.online`, rule cấu hình | notification email/Telegram/Zalo; `alarms` raised/cleared | `alert_rules`, `alarms`, `notifications` | bão 50 robot: gộp theo cửa sổ 60s; webhook chết: retry 3 lần, hiện lỗi, không chặn alert khác; cooldown chống spam | ALT-01..04 |
| audit | phiên terminal, lệnh OTA, đăng nhập | bản ghi tra cứu từ DSH | `audit_log` (append-only) | ghi audit thất bại: từ chối mở phiên | TRM-01 |
| relay | WebSocket từ DSH (admin) và từ AGT (mTLS) | ghép hai luồng byte, ghi audit | phiên đang mở | một đầu rớt: đóng đầu kia ≤ 30s | TRM-01..03 |

### DB, BRK, REG, DSH, DEP

| Module | Vào | Ra | Hỏng phải xử | Test ID |
|---|---|---|---|---|
| DB | migration từ SRV; insert/query qua sqlc | hypertable `telemetry` compression sau 7 ngày, continuous aggregate 1 phút giữ 90 ngày, retention | volume đầy: retention chạy trước; restore từ backup | INS-03, LOD-01 |
| BRK | cert client, CONNECT, PUBLISH/SUBSCRIBE | cho/không cho theo ACL SQL (`agentId` → topic của nó và devices trong inventory); LWT | không cert: từ chối tầng TLS; publish sai topic: disconnect theo cấu hình; `max_packet_size` 64 KB | ACL-01..04 |
| REG | `docker push` từ vendor | image theo digest cho AGT | registry tắt giữa pull: AGT retry (OTA-06) | OTA-06, OTA-07 |
| DSH | REST + SSE từ SRV; cấu hình theme instance | giao diện thiết bị, chart, deploy, alert, terminal (xterm.js) | SSE rớt: tự reconnect, TanStack invalidate; theme thiếu: mặc định | WLB-01, TRM-02 |
| DEP | VPS trống, biến môi trường, docs | `docker compose up` đủ 6 service, CA bootstrap, user seed; backup/restore script | chạy lại: idempotent; restore: device reconnect bình thường | INS-01..03 |

---

## 2. Phase 0 — giai đoạn, module, nghiệm thu

Nguyên tắc thứ tự trong mỗi milestone: **lát cắt dọc trước** (một luồng chạy xuyên
agent → broker → server → dashboard), rồi mới mở rộng chiều ngang. Mỗi milestone chỉ
đóng khi đủ test ID trong `05-test-catalog.md`; bảng dưới chỉ nói **làm trước cái gì**
trong milestone đó, không đổi ID thuộc milestone nào (tracker và catalog giữ nguyên).

### M0' — Nền hạ tầng và hợp đồng (3 tuần, tính từ 2026-10-20)

Lý do có M0': M0 cũ dừng ở skeleton; hợp đồng mới có một channel và toolchain chưa
có Rust. Không có M0' thì PRV-01 không có gì để đứng.

| Module | Việc |
|---|---|
| SPEC | Điền đủ 8 channel còn `TODO(M0)` vào `asyncapi.yaml`; JSON Schema cho `status`, `inventory`, `cmd`, `cmdRes`, `otaState`, `deviceState`, `event`; `probe-*.schema.json` cho hello/helloAck/data/event/cmd/ping; test vector hợp lệ/không hợp lệ cho mỗi schema; `openapi.yaml` cho enroll/renew/devices. Bảng mã `codes.md`. Giới hạn 64 KB ghi vào spec. |
| PROTO-GO, PROTO-RS | `make gen` chạy go-jsonschema và typify từ cùng `specs/schemas`; CI đỏ nếu file sinh lệch. |
| DEP (toolchain) | `dev.Dockerfile` thêm Rust stable pinned, cargo-nextest, cargo-deny, sccache, mold; Go nâng 1.25; `.rust-toolchain`; `devcontainer.json`. `agent/` rời `go.work`, thành Cargo workspace. |
| Tracker | `track.py` đọc JUnit từ `cargo nextest --profile ci`; `Makefile` tách `lint-go`/`lint-rust`/`lint-cpp`; `trace.py` kiểm `forbid(unsafe_code)`. |
| DEP (compose) | `docker-compose.yml` thật: EMQX pin phiên bản, listener 8883 mTLS, ACL SQL; Timescale; registry; server; dashboard. `install.sh` bootstrap CA và user seed. |
| BRK | `deploy/emqx/acl.sql` theo topic layout thật, test bằng `mosquitto_pub` thủ công. |

**Nghiệm thu M0':** `./mo verify` xanh và tick **TEL-01** [U] ở cả Rust và Go (test
vector validate đúng hai phía) · `./mo trace` OK với 17 ADR · `docker compose up` trên
máy trắng, đăng nhập dashboard bằng user seed · `./mo doctor` không thiếu gì · `.steering`
có mục ghi quyết định M0'. Không có test [I] nào ở M0'.

### M1 — Agent v0 + provisioning (8 tuần)

| Thứ tự | Module | Việc | Test ID mục tiêu |
|---|---|---|---|
| 1 | SRV.ca + DB | Bảng `enroll_tokens`, `agents`; enroll, renew; CA bootstrap | PRV-01, PRV-02 [I] |
| 2 | AGT.identity + AGT.transport | enroll CLI, key/CSR, connect mTLS, LWT, status retained | PRV-01 [I] xanh đầu-cuối |
| 3 | BRK | ACL SQL theo agentId và inventory | ACL-01, ACL-02, ACL-03 [I] |
| 4 | AGT.telemetry + SRV.ingest + DB | envelope, batch insert hypertable, LWT → offline | TEL-03 [I] |
| 5 | SRV.api + DSH | device list online/offline qua SSE; login JWT 2 role | (DoD M1) |
| 6 | AGT.buffer | SQLite offline, replay theo seq | TEL-04 [I] |
| 7 | AGT.transport | giới hạn 64 KB | ACL-04 [I] |
| 8 | AGT.identity | renew < 30 ngày; hết hạn không crash-loop | PRV-03, PRV-04 [I] |
| 9 | SIM | agent giả lập N thiết bị cho CI nightly | phục vụ TEL-02 và LOD sau |
| 10 | [H] | Jetson + Pi thật, `curl \| sh` | PRV-05, TEL-07 [H] biên bản |

**Gate rút lui Rust** (ADR-0012): hết tuần 8 kể từ `/task PRV-01` mà PRV-01 và TEL-03
chưa xanh → ADR quay về Go cho agent.

**Nghiệm thu M1:** PRV-01..04, ACL-01..04, TEL-01, TEL-03, TEL-04 xanh trong CI nightly
· PRV-05, TEL-07 có biên bản `./mo hw-test` ký tên · DoD: dashboard thấy 2 thiết bị thật
online/offline realtime. TEL-02, TEL-05, TEL-06 thuộc nhóm M1–M2, cho phép kéo sang M2.

### M2 — Probe ROS 2 + dashboard v0 (6 tuần)

| Thứ tự | Module | Việc | Test ID |
|---|---|---|---|
| 1 | AGT.probe_hub | Unix socket, hello/helloAck, ping/pong, inventory hợp nhất | PRB-01 [U], PRB-03, PRB-04, PRB-05 [I] (probe giả lập) |
| 2 | PRB-ROS | rclcpp: node list, topic hz, battery, pose; event ROS_NODE_DOWN; image matrix humble/jazzy × amd64/arm64 | PRB-02 [I] (sim ROS 2 trong CI), PRB-06 [H] |
| 3 | DSH | device detail, ECharts telemetry, profile AMR (battery, pose), RBAC admin/viewer | — |
| 4 | AGT + SIM | chạy 24h, clock skew, buffer 24h | TEL-02, TEL-05, TEL-06 [I] |

**Nghiệm thu M2:** toàn bộ PRB [I] xanh, PRB-06 [H] biên bản, TEL nhóm C đủ 7/7 · DoD:
robot ROS 2 (sim hoặc thật) hiện node status + battery trên dashboard · bắt đầu tiếp
cận design partner (có demo).

### M3 — OTA v1 ⭐ (10 tuần, trọng tâm Phase 0)

| Thứ tự | Module | Việc | Test ID |
|---|---|---|---|
| 0 | spike | rumqttc v5 response topic + user properties (đã phải xong ở M1, kiểm lại) | — |
| 1 | AGT.ota | state machine với `Persisted<_>`, SQLite, bollard pull theo digest, verify | OTA-07 [I], OTA-06 [I] |
| 2 | AGT.ota | switch giữ image cũ, health check http/exec/ros-topic, rollback tự trị | OTA-01, OTA-02, OTA-03 [I] |
| 3 | AGT.ota | boot thấy state dở dang → rollback | OTA-04, OTA-05 [H] |
| 4 | AGT.cmd | expiresAt, một deployment tại một thời điểm | OTA-08, OTA-10 [I] |
| 5 | SRV.fleet + DB + DSH | deployment, nhóm, wave, dừng khi fail, UI tiến độ | OTA-09 [I] |
| 6 | REG + DEP | registry trong compose, docs push image cho vendor | — |
| 7 | Release | goreleaser-tương-đương cho Rust (cargo-dist hoặc script), cosign ký binary + image | — |
| 8 | [H] | disk gần đầy; toàn ma trận Jetson + Pi | OTA-11, OTA-12 [H] |

**Nghiệm thu M3:** OTA-01..10 [I] xanh · OTA-04, 05, 11, 12 [H] biên bản trên **cả**
Jetson và Pi · DoD: demo deploy version lỗi → robot tự về version cũ không can thiệp ·
design partner ký (North Star tháng 4 của spec v2, tính lại theo lịch thật).

### M4 — Alert + remote log (5 tuần)

| Module | Việc | Test ID |
|---|---|---|
| SRV.alert | rule offline > X, battery < Y, node chết; raised/cleared; cooldown; gộp bão | ALT-01, ALT-02, ALT-03 [I] |
| SRV.alert notifier | email SMTP, Telegram, Zalo webhook; retry có giới hạn | ALT-04 [I] |
| AGT.logs + PRB-ROS | `logs.start/stop`, TTL 15 phút, tải log | TRM-04 [I] |
| DSH | trang alert, cấu hình rule, log viewer | — |

**Nghiệm thu M4:** ALT-01..04, TRM-04 xanh · DoD: rút mạng robot → Telegram trong 1 phút.

### M5 — Terminal + white-label + installer (6 tuần)

Trước khi bắt đầu: **ADR terminal** (WebSocket mTLS hay WireGuard, xem BACKLOG) — hoà
giải mâu thuẫn spec v2 và dev-plan.

| Module | Việc | Test ID |
|---|---|---|
| AGT.pty + SRV.relay + SRV.audit + DSH (xterm.js) | phiên terminal, audit đầy đủ, role admin, đóng sạch 30s | TRM-01, TRM-02, TRM-03 [I] |
| DSH + SRV.api | theme logo/màu qua cấu hình instance, CSS variables | WLB-01 [I] |
| DEP | `install.sh` idempotent, backup/restore, docs cài < 30 phút | INS-02, INS-03 [I], INS-01 [H] |

**Nghiệm thu M5:** TRM-01..03, WLB-01, INS-02, INS-03 xanh · INS-01 [H] do người ngoài
team thực hiện có biên bản · DoD: cài instance mới < 30 phút theo docs.

### M6 — Hardening với design partner (8 tuần trở lên)

| Module | Việc | Test ID |
|---|---|---|
| SIM + SRV.ingest + DB | 50 agent giả lập 72h, compression, backpressure, bão reconnect | LOD-01, LOD-02 [I] |
| Toàn hệ | fleet design partner 30 ngày, rà ACL, rotate cert, review audit | LOD-03 [H] |
| Security pass | cargo-deny/govulncheck sạch, SBOM, ký release | — |

**Nghiệm thu Phase 0 (= gate vào Phase 1, theo `03`):** 49/49 ✅ trong tracker có
evidence · design partner production ≥ 3 tháng · OTA 0 sự cố brick · ≥ 1 vendor trả phí
hoặc 2 vendor pipeline nghiêm túc. Chưa đạt → ở lại hardening.

**Tổng thời lượng Phase 0 theo lịch này:** khoảng 46 tuần kể từ 2026-10-20, với
~15–20 giờ/tuần cả team. Lịch cũ (26 tuần) viết cho team chưa đi học.

---

## 3. Phase 1 — Multi-tenant & Interop (gate: Phase 0 đạt + tiền nuôi ≥ 1 full-time)

Theo `03-phase-plan-1-4.md`. Nếu gate tài chính không đạt: **Phase 1 rút gọn** = chỉ
PRB-VDA và VID-1a.

| Thứ tự | Module | Vào | Ra | Nghiệm thu |
|---|---|---|---|---|
| 1 | PRB-VDA (vda5050-probe) | MQTT VDA 5050 `state/visualization/connection/factsheet` từ AGV chuẩn | `hello/data/event` Probe API; chiều ngược `order/instantActions` khi làm bridge | AGV VDA 5050 thật hiện trên dashboard không cài agent lên robot; test ID mới nhóm VDA-xx thêm vào catalog |
| 2 | VID-1a (view-only) | GStreamer H.264 hardware encode trên robot | track WebRTC qua `webrtc` crate; signaling qua WS sẵn có; coturn relay | xem camera từ dashboard qua NAT nhà máy; test ID VID-xx |
| 3 | DB + SRV (multi-tenant) | `tenant_id` + Postgres RLS; ACL EMQX theo tenant prefix (ADR-0008) | mọi query có điều kiện tenant | test cách ly tenant TNT-xx; **ADR broker SaaS** (ADR-0014) và **ADR k3s** trước khi deploy |
| 4 | Auth | Keycloak thay JWT tự làm | SSO, org/team, invite | ADR Keycloak |
| 5 | CP (control plane) | license, usage report từ instance vendor | signup/billing Stripe + VietQR thủ công; grace 30 ngày offline | instance vendor sống 30 ngày không gọi về được |
| 6 | DSH fleet | vị trí nhiều robot trên floorplan, mission history, health score, link-out Foxglove, bag recorder | — | — |
| 7 | VID-1b (teleop) | chỉ sau 1a ổn định | deadman, watchdog RTT, role teleop, audit | test ID TEL-OP-xx, không thương lượng |

Ranh giới kiến trúc phải giữ: topic layout `mechops/v1/{tenant}/…` không đổi; agent
ngoài đồng không cần update khi vào multi-tenant; probe mới chỉ là tiến trình mới nói
Probe API v1.

## 4. Phase 2 — Industrial Platform (gate: ≥ 5 khách trả phí + hợp đồng PLC/OPC-UA)

| Module | Vào | Ra | Nghiệm thu |
|---|---|---|---|
| PRB-OPCUA | address space OPC-UA, subscribe node | profile `plc` qua Probe API, Mode B trên gateway | 1 nhà máy thật đọc PLC qua MechOps |
| PRB-MODBUS | register map cấu hình từ dashboard, TCP + RTU | profile `plc` | — |
| ALM (alarm center) | alarms từ robot và PLC | ack, escalation, bàn giao ca | khách nhà máy dùng hằng ngày; đo bằng renew hợp đồng |
| OTA firmware | `artifactType: firmware-binary` | nạp ESP32/STM32 qua bootloader chip | ma trận [H] riêng |
| Compliance | gap assessment IEC 62443 (zone/conduit) | hồ sơ trả lời audit khách FDI | không cần certify |

## 5. Phase 3 — Data Platform (gate: ≥ 100 robot + khách hỏi retention/replay)

| Module | Vào | Ra | Nghiệm thu |
|---|---|---|---|
| DATA tiering (Rust) | Timescale 90 ngày | Parquet trên MinIO theo năm | truy vấn 1 năm dữ liệu < 10s |
| Replay | telemetry + video + bag cùng timeline | "hộp đen" sự cố | tái dựng một sự cố thật của khách |
| Dataset builder | fleet data | cắt/gắn nhãn/xuất cho team AI khách | 1 khách dùng để train |

Đây là nơi Rust trả công: Arrow/DataFusion, và team đã có hai năm Rust từ agent.

## 6. Phase 4 — AI Platform (gate: Phase 3 ≥ 1 năm)

Thứ tự theo độ khó: anomaly thống kê → predictive maintenance (cần nhãn từ ALM) →
fleet optimization → inspection → digital twin chỉ khi có khách tài trợ. Bán insight,
không bán model. Mọi module ở đây là service tách riêng đọc từ DATA, không đụng agent.

---

## 7. Phụ thuộc giữa module và rủi ro chặn đường

```
SPEC ──▶ PROTO-GO ──▶ SRV.ca ──▶ SRV.ingest ──▶ SRV.api ──▶ DSH
  │                      ▲            ▲
  └────▶ PROTO-RS ──▶ AGT.identity ──▶ AGT.transport ──▶ AGT.telemetry ──▶ AGT.buffer
                                                  │
                        PRB-ROS ──▶ AGT.probe_hub ─┘
                                                  ▼
                       REG ──▶ AGT.ota ◀── AGT.cmd ◀── SRV.fleet
```

| Rủi ro | Chặn gì | Đối sách | Ghi ở |
|---|---|---|---|
| rumqttc v5 thiếu response topic / user properties | AGT.transport, toàn bộ OTA | spike tuần 1 M1; fallback: đóng `cmdId` vào payload (spec đã có `cmdId`), không dùng MQTT 5 property | ADR-0012 |
| Team học Rust chậm | M1 | gate rút lui 8 tuần | ADR-0012 |
| EMQX BSL cho SaaS | Phase 1 | ADR broker SaaS với số đo LOD | ADR-0014 |
| Mất khoá CA | toàn fleet | INS-03 backup gồm `ca/`, passphrase tách | ADR-0016 |
| Design partner không ký | M3 trở đi thiếu phần cứng thật | Jetson + Pi nội bộ cho [H]; "Phase 1 rút gọn" | `03` |
| Founder đi học, nhịp giảm | mọi milestone | lịch 46 tuần đã tính; mỗi phiên vào bằng `/dev`, ra bằng `/handoff` | `07-ai-flow` |
| Bộ công cụ repo phình tiếp | mọi milestone | đóng băng `tools/` cho tới TEL-03 xanh, ngoại lệ duy nhất là parser nextest | mục 2 M0' |

---

## 8. Việc làm ngay (tuần 2026-10-20)

1. Commit bộ ADR 0012–0017 và file này với `Implements: none`.
2. `./mo steer plan new m0-nen-rust` cho M0' với `covers: [TEL-01]`, `adr: [0012, 0013, 0016]`;
   plan `m1-contract-v01` hiện có nhập vào hoặc abandon có lý do (không xoá).
3. Spike rumqttc v5 trong `agent/spikes/` (ngoài workspace chính, có ghi `.steering`).
4. `dev.Dockerfile` thêm Rust; `track.py` đọc nextest; chạy `./mo verify` thấy TEL-01 đỏ thật.
5. Điền 8 channel vào `asyncapi.yaml` theo `protocol-notes.md`, qua `./mo steer plan contract`.
