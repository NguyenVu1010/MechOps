# RobotOps — Phase 1→4 Plan

> Đi kèm spec v2.0 và dev plan Phase 0.
> Nguyên tắc viết plan: **độ chi tiết giảm dần theo khoảng cách thời gian.** Phase 1 chi tiết gần bằng Phase 0 (sẽ build trong 12–18 tháng tới); Phase 2–4 là định hướng có kiến trúc — đủ để quyết định hôm nay không khóa cửa ngày mai, nhưng không giả vờ biết trước thị trường 3 năm nữa. Mỗi phase có **decision gate**: điều kiện phải đạt trước khi bơm nguồn lực vào phase kế.

---

## Phase 1 — Multi-tenant & Interop

**Điều kiện vào (gate từ Phase 0):** design partner chạy production ≥ 3 tháng, OTA 0 sự cố brick, ≥ 1 vendor trả phí hoặc 2 vendor pipeline nghiêm túc. Chưa đạt → ở lại Phase 0 hardening, không build tiếp.

### 1.1 Multi-tenant + Self-serve (ưu tiên #1)

**Quyết định kiến trúc — hai sản phẩm, một codebase:**

```
┌─ Kênh vendor (giữ nguyên) ──────────────────┐
│  Single-tenant Docker Compose per vendor     │
│  License/năm · vendor tự host hoặc host hộ   │
├─ Kênh self-serve (mới) ─────────────────────┤
│  1 deployment multi-tenant do RobotOps host  │
│  Freemium ≤2 robot → trả phí theo bậc        │
└─ Control Plane (mới, nhẹ) ──────────────────┘
   License registry · usage report · signup/billing
```

- **Tenant isolation:** row-level (cột `tenant_id` + Postgres RLS) cho self-serve — không schema-per-tenant (đau migration), không instance-per-user (đắt hạ tầng). Kênh vendor đã cách ly vật lý sẵn.
- **MQTT isolation:** topic prefix `robotops/{tenantId}/{deviceId}/…` + ACL EMQX theo tenant. Đây là lý do chọn EMQX từ Phase 0.
- **Auth:** đến lúc đưa **Keycloak** vào (đã hoãn từ Phase 0) — SSO, org/team, invite flow. Agent giữ device cert, không đổi.
- **Billing:** Stripe cho quốc tế + chuyển khoản/VietQR thủ công cho VN (đừng tự động hóa billing VN sớm — số lượng khách chưa đáng).
- **Control plane license:** instance vendor gọi về kiểm tra license định kỳ, **grace period 30 ngày offline** — không được chết khi mất mạng (khách on-premise là lý do tồn tại của sản phẩm).

### 1.2 VDA 5050 Adapter (ưu tiên #2)

VDA 5050 chuẩn hóa giao tiếp master control ↔ AGV qua MQTT (topics: `order`, `instantActions`, `state`, `visualization`, `connection`, `factsheet`). RobotOps đứng được ở **hai phía**, build theo thứ tự:

1. **vda5050-probe (làm trước):** RobotOps *nói chuyện với* robot đã tuân thủ VDA 5050 — nhà máy FDI có sẵn AGV chuẩn này chỉ việc kết nối, không cài agent lên robot. Đây là Mode B gateway, đúng seam đã thiết kế từ Phase 0.
2. **VDA 5050 bridge (làm sau, khi có khách cần):** phơi robot ROS 2 trong RobotOps *ra ngoài* như thiết bị VDA 5050 — để vendor của ta bán robot vào nhà máy yêu cầu chuẩn này trong gói thầu. Đây là feature bán hàng cho vendor, giá trị thương mại cao.

Envelope schema Phase 0 cần map sạch sang `state` message của VDA 5050 — kiểm tra chéo khi viết protocol spec v0.1 (việc của M0, không phải Phase 1).

### 1.3 Video / Teleop qua WebRTC (ưu tiên #3)

- **Stack:** Pion (Go — cùng ngôn ngữ agent) · signaling qua kênh WebSocket sẵn có · **coturn** làm TURN relay (bắt buộc — robot sau NAT nhà máy, đừng ảo tưởng STUN xuyên được)
- **Pipeline camera:** GStreamer trên robot → H.264 hardware encode (Jetson NVENC, Pi V4L2) → track WebRTC. CPU encode trên Pi sẽ không kham nổi — hardware encode là yêu cầu cứng.
- **Lộ trình 2 bước an toàn:**
  - **1a — View-only streaming:** xem camera robot từ dashboard. Đủ cho use case remote support của vendor, rủi ro thấp, ship trước.
  - **1b — Teleop (điều khiển):** chỉ sau khi 1a ổn định. Yêu cầu cứng: deadman switch (nhả phím = dừng), watchdog latency (RTT > ngưỡng = dừng), audit log phiên điều khiển, quyền teleop là role riêng trong RBAC. *Teleop là tính năng đầu tiên có thể gây tai nạn vật lý — mọi shortcut ở đây đều là nợ không trả được.*

### 1.4 Fleet Dashboard (ưu tiên #4)

- Map view 2D (canvas/deck.gl — **chưa cần ThreeJS**): vị trí realtime nhiều robot trên bản đồ nhà máy (ảnh floorplan + occupancy grid từ ROS)
- Mission history + timeline per robot · Health score tổng hợp (uptime, lỗi, pin chai)
- Foxglove tích hợp cho debug sâu (link-out từ device detail, không nhúng lại)
- Bag recorder: trigger ghi rosbag từ xa, upload về server — cầu nối sang Phase 3

### 1.5 Hạ tầng & nguồn lực Phase 1

| Thêm vào | Lý do |
|---|---|
| Keycloak | Multi-tenant auth — đúng thời điểm đã hẹn từ Phase 0 |
| Redis | Session + rate-limit cho self-serve public — giờ mới có số đo justify |
| coturn | TURN relay cho WebRTC |
| MinIO | Bag file + video clip storage — đặt nền Phase 3 |
| k3s (chỉ cho self-serve SaaS) | Deployment multi-tenant do ta host cần rolling update; **kênh vendor giữ Docker Compose** |

**Thực tế nguồn lực:** Phase 1 không kham nổi bằng part-time — multi-tenant + WebRTC + VDA 5050 là khối lượng của 2–3 người full-time /12 tháng. Gate tài chính đi kèm gate kỹ thuật: doanh thu vendor + service đủ nuôi ≥ 1 full-time, hoặc gọi vốn seed. **Không đạt → cắt scope Phase 1 xuống còn mục 1.2 (VDA probe) + 1.3a (view-only video)** — hai món bán được cho vendor hiện có mà không cần multi-tenant.

---

## Phase 2 — Industrial Platform

**Gate:** ≥ 5 khách trả phí · có ≥ 1 khách nhà máy thật yêu cầu PLC/OPC-UA bằng hợp đồng (không build trước khi có người trả tiền cho nó).

- **opcua-probe** (thư viện `gopcua`): browse address space, subscribe node, map sang envelope schema — chạy Mode B trên gateway
- **modbus-probe**: TCP + RTU, polling theo register map cấu hình từ dashboard (không hardcode)
- **Alarm center:** chuẩn hóa alarm PLC/robot về một chỗ — ack/escalation/shift handover. *Đây là tính năng nhà máy dùng hằng ngày, quyết định renew hợp đồng — đầu tư UX nhiều nhất phase này.*
- **Factory layout:** nâng map 2D Phase 1 thành sơ đồ nhà máy đa tầng — vẫn chưa cần 3D trừ khi khách trả tiền cho nó
- **IEC 62443:** bắt đầu gap assessment (network segmentation, zone/conduit model) — chưa cần certify, cần *trả lời được câu hỏi audit* của khách FDI
- Firmware OTA (`artifactType: firmware-binary`) cho ESP32/STM32 — seam đã chừa từ Phase 0, giờ mới build

---

## Phase 3 — Data Platform

**Gate:** ≥ 100 robot connected · khách chủ động hỏi về data retention/replay (tín hiệu kéo, không đẩy).

- Telemetry retention phân tầng: TimescaleDB (nóng, 90 ngày) → MinIO Parquet (lạnh, năm)
- Mission replay: đồng bộ timeline telemetry + video + bag — "hộp đen" tai nạn robot, tính năng bán cho bảo hiểm/tranh chấp trách nhiệm
- Lidar/pointcloud replay (giờ mới đến lượt ThreeJS)
- Dataset builder: cắt/gắn nhãn/xuất dữ liệu fleet cho team AI của khách — **cầu nối sang Phase 4 và là lý do khách không rời platform**

---

## Phase 4 — AI Platform

**Gate:** Phase 3 vận hành ≥ 1 năm — không có dữ liệu tích lũy thì AI phase là trang trí.

Thứ tự theo độ khó tăng dần: anomaly detection trên telemetry (thống kê, không cần ML nặng — ship sớm được) → predictive maintenance (cần nhãn hỏng hóc tích lũy từ alarm center Phase 2) → fleet optimization → AI inspection (camera) → digital twin (chỉ khi có khách enterprise tài trợ).

Nguyên tắc: **AI phase bán insight, không bán model.** Khách không mua "anomaly detection", khách mua "robot số 7 sẽ hỏng bánh trong 2 tuần".

---

## Tổng hợp — bảng quyết định xuyên phase

| | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|---|
| Khách chính | 1 vendor design partner | Vendor + startup self-serve | + Nhà máy | + Fleet lớn | + Enterprise |
| Doanh thu chính | Service | Vendor license + SaaS đầu | + Hợp đồng industrial | + Data tier | + AI module |
| Deploy | Compose single-tenant | + k3s cho SaaS | + Edge HA option | như cũ | như cũ |
| Nguồn lực tối thiểu | Part-time team | ≥ 1–2 full-time | 3–5 người | 5+ | tùy vốn |
| Gate vào | — | Partner prod 3 tháng + tiền nuôi full-time | 5 khách + hợp đồng PLC | 100 robot + tín hiệu kéo | Data 1 năm |

## Rủi ro cấp roadmap

| Rủi ro | Đối sách |
|---|---|
| Phase 1 quá tải với nguồn lực thật | Đã có sẵn "Phase 1 rút gọn": VDA probe + view-only video, hoãn multi-tenant |
| Build Phase 2 khi chưa ai trả tiền | Gate hợp đồng — industrial feature chỉ build khi có chữ ký |
| Teleop gây sự cố vật lý | Tách 1a/1b, deadman + watchdog là yêu cầu cứng không thương lượng |
| VDA 5050 ra bản mới làm lệch adapter | Probe versioned theo spec VDA (2.1.x), cách ly trong probe — core không biết VDA tồn tại |
| Đối thủ nội địa thêm OTA | Tốc độ Phase 0 + độ sâu (staged rollout, auto-rollback, firmware OTA) — bề rộng feature dễ copy, độ tin cậy thì không |
