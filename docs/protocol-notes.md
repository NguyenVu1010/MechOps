# RobotOps Protocol Spec v0.1

> Trạng thái: Draft — đóng băng khi M1 bắt đầu. File này là **hợp đồng** giữa agent ↔ server ↔ probe.
> Thuộc phần **open source** cùng với agent (spec v2.0 mục 7).
> Quy tắc sửa đổi: thay đổi phá vỡ tương thích → tăng version segment trong topic; thêm field mới optional → không cần.

---

## 1. Quy ước chung

- **Transport:** MQTT 5 qua mTLS (agent ↔ EMQX). Terminal PTY và WebRTC signaling đi qua WebSocket riêng (mTLS) — **không nằm trong spec này**, chỉ MQTT.
- **Payload:** JSON UTF-8. Field đặt tên camelCase. Field không nhận diện được → bên nhận **bỏ qua, không lỗi** (forward compatible).
- **Timestamp:** epoch milliseconds UTC, field `ts`. Kèm `seq` (uint64 tăng dần per-publisher) để phát hiện mất gói và sắp lại thứ tự sau replay.
- **Agent vs Device:** `agentId` = tiến trình agent (1 per host). `deviceId` = thiết bị logic. Mode A: agent quản lý đúng 1 device. Mode B: 1 agent quản lý N device. Mọi dữ liệu vận hành gắn với `deviceId`; vòng đời kết nối/OTA gắn với `agentId`.

### 1.1 Cấu trúc topic

```
robotops/v1/{tenant}/agents/{agentId}/status        retained · LWT
robotops/v1/{tenant}/agents/{agentId}/inventory     retained
robotops/v1/{tenant}/agents/{agentId}/cmd           QoS 1 · server → agent
robotops/v1/{tenant}/agents/{agentId}/cmd/res       QoS 1 · agent → server
robotops/v1/{tenant}/agents/{agentId}/ota/state     QoS 1 · retained
robotops/v1/{tenant}/devices/{deviceId}/telemetry   QoS 0
robotops/v1/{tenant}/devices/{deviceId}/state       QoS 1 · retained
robotops/v1/{tenant}/devices/{deviceId}/events      QoS 1
robotops/v1/{tenant}/devices/{deviceId}/logs/{stream}  QoS 0 · chỉ khi bật
```

- `{tenant}`: Phase 0 luôn là `default`. Có mặt từ đầu để multi-tenant Phase 1 **không đổi topic layout** (chỉ đổi ACL).
- `v1`: version của topic layout + envelope, không phải version sản phẩm.

### 1.2 QoS & retained — nguyên tắc chọn

| Loại dữ liệu | QoS | Retained | Lý do |
|---|---|---|---|
| Telemetry tần số cao | 0 | không | Mất 1 mẫu không sao, mẫu mới thay thế |
| State (trạng thái hiện tại) | 1 | **có** | Dashboard mở lên thấy ngay, không chờ mẫu kế |
| Events / alarms | 1 | không | Không được mất, nhưng là dòng sự kiện |
| OTA cmd/progress | 1 | state retained | Không được mất, state phục hồi được sau reconnect |

---

## 2. Danh tính & Provisioning

```
robotops-agent enroll --server https://... --token <ENROLL_TOKEN>
```

1. Vendor tạo enroll token (TTL 24h, dùng 1 lần) trên dashboard.
2. Agent sinh keypair, gửi CSR + token → server ký cert (CN = agentId, TTL 90 ngày), trả về CA chain + cấu hình MQTT.
3. Agent lưu cert tại `/var/lib/robotops/identity/`, tự gia hạn khi còn < 30 ngày (qua API mTLS bằng cert hiện tại).
4. **ACL EMQX (backed by PostgreSQL):** agent chỉ được publish/subscribe topic chứa đúng `{agentId}` và các `{deviceId}` trong inventory của nó. Robot A không đọc được topic robot B — kiểm tra ở broker, không tin agent.

---

## 3. Envelope & Profile schema

### 3.1 `devices/{deviceId}/telemetry` — QoS 0, mặc định 2s/lần (cấu hình được)

```json
{
  "v": 1,
  "ts": 1752051600000,
  "seq": 48213,
  "metrics": {
    "cpuPct": 41.2, "memPct": 63.0, "diskPct": 71.5,
    "netRxKbps": 120, "netTxKbps": 45, "tempC": 55.1
  },
  "profiles": {
    "amr": {
      "batteryPct": 84, "charging": false,
      "pose": { "x": 12.4, "y": 8.5, "yaw": 1.57, "frame": "map" },
      "velocity": { "linear": 0.6, "angular": 0.0 },
      "missionId": "m-2091", "missionState": "executing"
    },
    "ros": { "nodesUp": 14, "nodesTotal": 15 }
  }
}
```

**Quy tắc profile (chống nhiễm schema — đã chốt):** envelope lõi chỉ có `v/ts/seq/metrics`. Mọi thứ đặc thù domain nằm trong `profiles.{tên}`. Server lưu profile dạng JSONB — thêm profile mới **không cần migration**. Phase 0 định nghĩa: `amr`, `ros`. Chừa chỗ: `plc`, `arm`.

### 3.2 `devices/{deviceId}/state` — QoS 1, retained, publish khi thay đổi

```json
{
  "v": 1, "ts": 1752051600000,
  "status": "online",            // online | offline | degraded | updating
  "agentId": "agt-7f3a",
  "activeAlarms": [
    { "code": "ROS_NODE_DOWN", "severity": "warning", "detail": "nav2_controller", "since": 1752051000000 }
  ],
  "app": { "name": "delivery-stack", "version": "1.4.2" }
}
```

### 3.3 `devices/{deviceId}/events` — QoS 1

```json
{ "v": 1, "ts": 1752051600000, "seq": 91,
  "type": "alarm.raised",        // alarm.raised | alarm.cleared | mission.started |
                                  // mission.completed | mission.failed | agent.restarted
  "code": "BATTERY_LOW", "severity": "warning",
  "data": { "batteryPct": 18 } }
```

### 3.4 `agents/{agentId}/status` — retained + LWT

- Khi connect: agent publish `{"status":"online","ts":...,"agentVersion":"0.3.1","host":{"os":"ubuntu22.04","arch":"arm64"}}`
- **LWT** đăng ký lúc CONNECT: `{"status":"offline","reason":"lwt"}` — broker tự phát khi agent rớt. Server suy ra mọi device trong inventory của agent đó → `offline`.

### 3.5 `agents/{agentId}/inventory` — retained (Mode B là đây)

```json
{ "v": 1, "ts": 1752051600000,
  "devices": [
    { "deviceId": "amr-001", "profiles": ["amr","ros"], "probe": "ros2-probe" },
    { "deviceId": "plc-line3", "profiles": ["plc"], "probe": "modbus-probe" }
  ] }
```

---

## 4. Command channel

`agents/{agentId}/cmd` (server → agent) và `cmd/res` (agent → server). Mọi lệnh có `cmdId` (UUID) để đối chiếu.

```json
{ "v": 1, "cmdId": "c-9d21", "ts": 1752051600000,
  "action": "ota.deploy",       // ota.deploy | ota.rollback | agent.restart |
                                 // logs.start | logs.stop | probe.exec
  "params": { ... },
  "expiresAt": 1752051900000 }   // lệnh hết hạn nếu agent offline quá lâu — tránh robot bật lại sau 3 ngày tự chạy lệnh cũ
```

Response: `{ "cmdId": "c-9d21", "status": "accepted|rejected|done|failed", "error": null, "data": {...} }`

`expiresAt` là bắt buộc với lệnh có tác dụng phụ (OTA, restart). Agent nhận lệnh quá hạn → trả `rejected/expired`.

---

## 5. OTA — manifest & state machine

### 5.1 Manifest (nội dung `params` của `ota.deploy`)

```json
{
  "deploymentId": "d-3341",
  "artifactType": "docker-image",          // Phase 0 chỉ hỗ trợ giá trị này;
                                            // chừa chỗ: firmware-binary, os-image
  "app": {
    "name": "delivery-stack",
    "image": "registry.internal:5000/vendor/delivery-stack:1.5.0",
    "digest": "sha256:ab12...",             // pull theo digest, tag chỉ để hiển thị
    "composeOverride": { "environment": { "FLEET_MODE": "prod" } }
  },
  "healthCheck": {
    "type": "http",                          // http | ros-topic | exec
    "spec": { "url": "http://localhost:8080/healthz", "expectStatus": 200 },
    "timeoutSec": 120, "intervalSec": 5, "successStreak": 3
  },
  "keepPreviousHours": 24
}
```

### 5.2 State machine (chạy trong agent, persist vào SQLite local)

```
IDLE → DOWNLOADING → VERIFYING(digest) → SWITCHING(stop cũ, giữ nguyên → start mới)
     → HEALTH_CHECK ─ pass ─→ SUCCESS (dọn image cũ sau keepPreviousHours)
                    └ fail ─→ ROLLING_BACK → ROLLED_BACK
Bất kỳ state nào gặp lỗi không phục hồi → FAILED (không tự thử lại — chờ lệnh)
```

**Ba luật cứng:**
1. **Rollback quyết định tại agent** — health check fail hoặc container mới crash-loop → tự về version cũ, không chờ server (robot có thể đang mất mạng đúng lúc đó).
2. **Sống sót qua mất điện:** mọi chuyển state ghi SQLite *trước khi* hành động. Boot lên thấy state dở dang (`DOWNLOADING`/`SWITCHING`) → coi như fail → rollback về version cũ còn nguyên trên đĩa.
3. **Pull theo digest, không theo tag** — tag bị ghi đè trên registry không được phép đổi thứ robot chạy.

### 5.3 `agents/{agentId}/ota/state` — QoS 1, retained

```json
{ "v": 1, "ts": 1752051600000, "deploymentId": "d-3341",
  "state": "HEALTH_CHECK", "progressPct": 90,
  "current": { "version": "1.4.2", "digest": "sha256:77aa..." },
  "target":  { "version": "1.5.0", "digest": "sha256:ab12..." },
  "error": null }
```

**Staged rollout là logic phía server** (Fleet Manager chọn nhóm, gửi lần lượt, chờ SUCCESS trước khi sang nhóm kế) — protocol không đổi, agent không biết mình thuộc "wave" nào.

---

## 6. Hành vi offline

- **Buffer:** SQLite tại `/var/lib/robotops/buffer.db`. Events + state: buffer **tất cả**, replay theo `seq` khi reconnect. Telemetry: buffer downsample 1 mẫu/30s, giữ tối đa 24h (đủ vẽ lại biểu đồ, không ngập băng thông khi reconnect).
- **Replay:** publish lại đúng topic gốc, `ts` gốc giữ nguyên — server phân biệt dữ liệu muộn nhờ `ts`/`seq`, không nhờ thời điểm nhận.
- **Clock:** agent dùng monotonic clock cho `seq` và đo khoảng cách; `ts` từ system clock kèm cảnh báo event `agent.clock_skew` nếu lệch NTP > 30s (nhà máy hay có máy sai giờ — dữ liệu time-series sai giờ là nợ khó đòi).

---

## 7. Probe API — contract v1

Kênh: probe **connect vào** Unix socket của agent `/run/robotops/agent.sock`. Khung tin: **NDJSON** (mỗi dòng một JSON object). Agent chấp nhận nhiều probe đồng thời.

### 7.1 Handshake

```json
→ probe gửi:
{ "type": "hello", "apiVersion": 1,
  "probe": { "name": "ros2-probe", "version": "0.2.0" },
  "capabilities": ["telemetry.profile:ros", "telemetry.profile:amr",
                   "logs.tail", "exec:ros2-cli"],
  "devices": [ { "deviceId": "amr-001", "profiles": ["amr","ros"] } ] }

← agent trả:
{ "type": "helloAck", "apiVersion": 1, "accepted": true,
  "config": { "telemetryIntervalMs": 2000 } }
```

- `apiVersion` là số nguyên. Agent công bố khoảng hỗ trợ trong docs; không khớp → `accepted:false` + lý do. Thêm capability/field mới **không** tăng version; đổi nghĩa field cũ mới tăng.
- `devices` trong hello là nguồn để agent hợp nhất thành `inventory` (mục 3.5) — **Mode B tự nhiên mà có:** gateway chạy 2 probe, mỗi probe khai devices của nó.

### 7.2 Luồng dữ liệu (probe → agent)

```json
{ "type": "data", "deviceId": "amr-001", "ts": 1752051600000,
  "profiles": { "amr": { "batteryPct": 84, "pose": {...} },
                 "ros": { "nodesUp": 14, "nodesTotal": 15 } } }

{ "type": "event", "deviceId": "amr-001", "ts": ...,
  "code": "ROS_NODE_DOWN", "severity": "warning", "data": { "node": "nav2_controller" } }
```

Agent gộp `data` của probe với metrics hệ thống của chính nó → envelope telemetry (mục 3.1). Probe **không biết MQTT tồn tại** — đó là toàn bộ mục đích của seam này.

### 7.3 Lệnh (agent → probe) & heartbeat

```json
{ "type": "cmd", "cmdId": "c-11", "action": "logs.tail",
  "deviceId": "amr-001", "params": { "stream": "rosout" } }
{ "type": "cmdRes", "cmdId": "c-11", "status": "streaming" }
{ "type": "logChunk", "cmdId": "c-11", "lines": ["..."] }

{ "type": "ping", "ts": ... }   // agent gửi mỗi 10s
{ "type": "pong", "ts": ... }   // 3 lần không pong → probe coi như chết
                                 // → devices của nó chuyển "degraded" + event
```

---

## 8. Ghi chú tương thích VDA 5050 (kiểm tra chéo — chưa build)

Mapping dự kiến `profiles.amr` ↔ VDA 5050 `state`: `batteryPct/charging` ↔ `batteryState` · `pose` ↔ `agvPosition` · `activeAlarms` ↔ `errors` · `missionId/missionState` ↔ `orderId/actionStates`. Kết luận kiểm tra: envelope hiện tại map sạch, **không cần đổi schema** — vda5050-probe Phase 1 chỉ là bộ dịch hai chiều.

---

## 9. Checklist đóng băng spec (trước M1)

- [ ] Review ACL pattern EMQX với topic layout thật (viết SQL rule mẫu)
- [ ] Định nghĩa bảng mã `code` chuẩn cho events/alarms (file `codes.md` riêng)
- [ ] Quyết định giới hạn kích thước payload (đề xuất: 64KB, từ chối ở agent)
- [ ] Viết JSON Schema máy-đọc-được cho mọi message (thư mục `/schemas`, dùng cho validate trong test + context cho Claude Code)
- [ ] Test vector: bộ payload mẫu hợp lệ/không hợp lệ cho CI của cả agent lẫn server
