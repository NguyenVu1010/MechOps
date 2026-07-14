# MechOps Platform — Product Spec v2.0

> Phiên bản: 2.0 · Cập nhật: 07/2026
> Thay đổi so với v1.0: chốt beachhead, thu gọn tech stack, định nghĩa lại OTA, thêm VDA 5050, chiến lược open-core, mô hình thu tiền, và scope Phase 0 khớp với nguồn lực thực tế.

---

## 1. Vision (giữ nguyên tinh thần v1.0)

MechOps là **Robot Operations Platform** — lớp hạ tầng trung gian giúp doanh nghiệp triển khai, giám sát, cập nhật và vận hành đội robot, PLC và thiết bị Industrial IoT trên cùng một nền tảng.

MechOps **không** điều khiển robot (không thay thế navigation/motion control). MechOps **vận hành** robot — tương tự quan hệ Kubernetes với container.

Mục tiêu dài hạn: hạ tầng tiêu chuẩn cho hệ sinh thái Robotics tại Việt Nam và Đông Nam Á.

---

## 2. Bối cảnh thị trường (mới — kết quả nghiên cứu 07/2026)

### 2.1 Đối thủ toàn cầu
| Đối thủ | Định vị | Điểm yếu khai thác được |
|---|---|---|
| Formant | Enterprise, teleop mạnh | ~$250/robot/tháng, sales-gated, không self-serve |
| InOrbit | AMR observability | Cloud-first, edge yếu |
| Foxglove | ROS 2 visualization/debug | Không có OTA, không fleet ops |
| Open-RMF | Open source fleet interop | Cần effort tích hợp lớn, không có sản phẩm hoàn chỉnh |
| AWS RoboMaker | — | **Đã đóng cửa 09/2025** — khoảng trống thị trường |

Mặt bằng giá thị trường: $50–500/robot/tháng tùy tính năng.

### 2.2 Đối thủ Việt Nam
- **VnRobo**: monitoring self-serve, free 3 robot, $29/tháng cho 25 robot, setup ROS 2 qua pip. Chiếm phân khúc monitoring giá rẻ. **Không có OTA.**
- **VNX Robotics**: bán AMR kèm Fleet SaaS $30–50/tháng (bundle với phần cứng của họ).

**Hệ quả chiến lược:** không cạnh tranh bằng monitoring dashboard giá rẻ. Cạnh tranh bằng **OTA + edge on-premise + white-label + industrial integration** — tầng khó mà đối thủ nội địa chưa chạm tới.

### 2.3 Thị trường VN
- Hệ sinh thái robotics VN ~$420–480M (2024), dự kiến ~$700–750M (2030).
- Động lực: China+1, FDI (Samsung, Foxconn, Intel), chính sách hỗ trợ automation/AI.
- Rào cản: SME hạn chế ngân sách, ROI chậm → **không bán SaaS per-robot cho SME giai đoạn đầu**.
- Nhà máy FDI Hàn/Nhật ngại đưa data ra cloud → **on-premise/edge là lợi thế cấu trúc**.

---

## 3. Khách hàng mục tiêu (đã chốt)

### Beachhead — Phase 0
**Robot vendor / System Integrator nội địa** cần white-label:
- Dashboard mang thương hiệu của họ giao cho khách cuối
- OTA để update robot đã bàn giao mà không phải đến tận nơi
- Remote support (log, terminal) giảm chi phí bảo hành

Mỗi vendor một instance riêng (single-tenant, Docker Compose) — dữ liệu tách biệt, dễ bán, dễ deploy.

### Phân khúc 2 — Phase 1
**Startup robotics / lab ROS 2** qua kênh self-serve (multi-tenant SaaS). Lùi lại Phase 1 vì self-serve đòi hỏi multi-tenant + billing + signup — không đáng đầu tư khi chưa có core cứng.

### Design Partner Program (bắt buộc)
Tuyển **1 vendor design partner** dùng miễn phí từ tháng 3–4 của Phase 0. Mục đích: feature list do nhu cầu thật định hình, không phỏng đoán. Đổi lại: họ được ảnh hưởng roadmap + giá ưu đãi khi thương mại hóa.

---

## 4. Nguồn lực & ràng buộc (mới)

- Team: founder + 1–2 cộng sự part-time.
- Founder học Master's tại Pháp từ 09/2026 → Phase 0 phải scope theo quỹ thời gian part-time, không theo lịch full-time.
- Phần cứng test: Jetson, Raspberry Pi (có sẵn). Chưa có fleet thật → design partner bù khoảng trống này.
- Nguyên tắc scope: **mọi hạng mục "tự xây" phải trả lời được câu hỏi "vì sao không dùng OSS có sẵn".**

---

## 5. Phase Development (đã điều chỉnh)

### Phase 0 — Foundation (part-time, mục tiêu ~6–9 tháng)

**Goal:** 1 vendor design partner chạy instance riêng, quản lý robot ROS 2 thật với OTA hoạt động tin cậy.

**Deliverables (theo thứ tự ưu tiên đã chốt):**

1. **OTA app-level (tự xây — sản phẩm chủ lực)**
   - Deploy/swap Docker container ROS 2 app trên robot
   - Giữ image cũ → rollback 1 lệnh
   - Staged rollout: update 1 robot → nhóm → toàn fleet
   - Trạng thái update realtime trên dashboard
   - *OS-level OTA: KHÔNG tự xây. Khi khách cần → wrap RAUC (A/B partition, đã battle-tested). Jetson dùng bootloader NVIDIA riêng — tự xây là bẫy scope.*

2. **Monitoring / Telemetry / Alert**
   - Agent: heartbeat, CPU/RAM/disk/network, battery, ROS 2 node & topic status
   - Alert rule cơ bản: offline, battery thấp, node chết
   - Notification: email + Telegram/Zalo webhook

3. **Remote terminal + remote log**
   - Shell qua reverse tunnel (WireGuard), audit log mọi phiên
   - Tail/tải log từ robot

4. ~~Video/teleop~~ → dời Phase 1

**Robot Agent:**
- Core generic cho mọi thiết bị ROS 2 + **AMR profile mặc định** (map, pose, battery, mission — widget/alert có sẵn)
- Chạy trên Ubuntu/Debian: Jetson, Pi, Industrial PC
- Ngôn ngữ: Go (single binary, dễ deploy, footprint thấp)

**Deploy:** Docker Compose single-tenant. Một file `docker-compose.yml` + script cài đặt → vendor tự host hoặc MechOps host hộ trên VPS.

**Trong scope Phase 0:** Agent, OTA app-level, dashboard, alert, remote terminal, user login (RBAC 2 role: admin/viewer), theming cơ bản cho white-label (logo, màu).

**Ngoài scope Phase 0 (chống scope creep):** multi-tenant, billing, VDA 5050, video, PLC/OPC-UA, Kubernetes, mobile app, AI.

### Phase 1 — Multi-tenant & Interop (sau Phase 0, ~6–12 tháng)

Thứ tự ưu tiên đã chốt:
1. **Multi-tenant + self-serve signup** → mở kênh startup/lab, freemium (free ≤2 robot)
2. **VDA 5050 adapter** (v2.1.0) → vé vào nhà máy FDI/ô tô; Unified Robot API map trực tiếp lên VDA 5050 thay vì schema tự chế
3. **Video/teleop qua WebRTC** → lý do chính thị trường trả $200+/robot/tháng
4. **Fleet dashboard multi-robot** (mission history, robot health tổng hợp)

Kèm theo: các tính năng ROS 2 ops của v1.0 (topic/node monitor, bag recorder, replay) — nhưng **tích hợp Foxglove** cho visualization thay vì tự xây, chỉ tự làm phần Foxglove không có (OTA, deploy, terminal, VPN).

### Phase 2 — Industrial Platform (năm 2–3)
OPC-UA, Modbus, PLC dashboard, alarm center, factory layout. (Gộp Phase 2+3 cũ — fleet features đã lên Phase 1.)

### Phase 3 — Data Platform (năm 3–5)
Telemetry storage dài hạn, mission/lidar replay, dataset builder.

### Phase 4 — AI Platform (năm 5+)
Predictive maintenance, anomaly detection, fleet optimization, digital twin.

---

## 6. Kiến trúc kỹ thuật (thu gọn)

```
Vendor Instance (Docker Compose)
├── API Server + Fleet Manager (Go)
├── MQTT Broker (EMQX hoặc Mosquitto)
├── PostgreSQL (+ TimescaleDB extension cho time-series)
├── OTA Registry (container image storage)
├── Dashboard (Next.js + TypeScript + Tailwind)
└── WireGuard hub (remote terminal/tunnel)

Robot (Jetson / Pi / IPC)
└── mechops-agent (Go, single binary, open source)
    ├── Telemetry → MQTT
    ├── OTA client (Docker container swap + rollback)
    ├── WireGuard client
    └── ROS 2 bridge (node/topic status, AMR profile)
```

### Tech stack Phase 0 — quy tắc "một thứ mỗi lớp"
| Lớp | Chọn | Bỏ / hoãn |
|---|---|---|
| Backend | Go | ~~FastAPI, gRPC, GraphQL~~ |
| Message | MQTT | ~~NATS, Kafka~~ |
| DB | PostgreSQL + TimescaleDB | ~~InfluxDB, Redis (thêm khi cần cache)~~ |
| Frontend | Next.js + TS + Tailwind | ~~ThreeJS (Phase 1 khi có map view)~~ |
| Deploy | Docker Compose | ~~Kubernetes, Helm, Terraform~~ |
| VPN | WireGuard | giữ |
| Auth | JWT tự triển khai đơn giản | ~~Keycloak (Phase 1 khi multi-tenant)~~ |
| Observability | Prometheus + Grafana (nội bộ) | ~~Loki, OpenTelemetry~~ |

Lý do: mỗi công nghệ thêm vào là chi phí vận hành vĩnh viễn với team part-time. Stack v1.0 (8 tháng lắp ráp) → stack v2.0 (build sản phẩm).

---

## 7. Chiến lược mã nguồn: Open-core (đã chốt)

| Thành phần | License | Lý do |
|---|---|---|
| `mechops-agent` | Apache 2.0, public GitHub | Chạy trên robot của khách — vendor sẽ audit; open tạo lòng tin + lan truyền trong cộng đồng ROS 2 (kênh marketing chi phí 0) |
| Protocol spec (MQTT topics, schema) | Open | Cho phép cộng đồng viết adapter |
| Server, Dashboard, OTA orchestration, Fleet Manager | Closed, trả phí | Phần thu tiền |

Playbook tham chiếu: Mender, balena, Grafana.

---

## 8. Business Model (đã chốt)

### Vendor white-label — nguồn thu chính năm 1–2
- **License/năm theo instance** (vendor tự host hoặc MechOps host hộ)
- Không tính per-robot → tránh chiến giá với VnRobo, vendor dễ dự toán
- Gợi ý khung giá (cần validate với design partner): tier theo số robot tối đa (≤10 / ≤50 / không giới hạn)
- Kèm: phí setup + adapter development + training (professional service)

### Self-serve SaaS — Phase 1
- Freemium: free ≤2 robot → trả phí theo bậc
- Mục đích chính: phễu người dùng + thương hiệu trong cộng đồng ROS 2, không phải doanh thu chính

### Professional Service
- Integration, deployment, adapter development — **thực tế sẽ là dòng tiền chính 12–24 tháng đầu**, ghi nhận đúng vai trò này trong kế hoạch tài chính

---

## 9. Compliance & Security roadmap

Phase 0: TLS everywhere, device certificate, audit log phiên remote, OTA rollback.
Phase 1+: chuẩn bị hồ sơ theo **IEC 62443** (industrial) và **SOC 2** (khi bán SaaS) — hai chuẩn xuất hiện lặp lại trong tiêu chí chọn platform của khách công nghiệp.

---

## 10. North Star Metrics (điều chỉnh theo mục tiêu "sản phẩm trước")

| Mốc | Chỉ số |
|---|---|
| Tháng 4 | 1 design partner ký kết, agent chạy trên robot thật của họ |
| Tháng 9 | OTA hoạt động tin cậy trên fleet design partner (≥5 robot), 0 sự cố brick |
| Tháng 12 | Design partner chuyển thành khách trả phí HOẶC 2 vendor mới trong pipeline |
| Năm 2 | 3–5 vendor license + self-serve mở, 100 robot connected |
| Năm 3 | 500 robot, VDA 5050 production tại ≥1 nhà máy FDI |

---

## 11. Rủi ro chính & đối sách

| Rủi ro | Đối sách |
|---|---|
| VnRobo mở rộng sang OTA/white-label | Tốc độ + quan hệ vendor trực tiếp; OTA làm sâu (staged rollout, rollback) khó copy nhanh |
| Part-time không đủ momentum | Scope Phase 0 khóa cứng (mục 5); design partner tạo deadline thật |
| OTA gây brick robot khách | Rollback bắt buộc trong mọi flow; staged rollout mặc định; test matrix trên Jetson + Pi trước mỗi release |
| Xây xong không ai mua | Design partner từ tháng 3–4 — không code 12 tháng trong chân không |
