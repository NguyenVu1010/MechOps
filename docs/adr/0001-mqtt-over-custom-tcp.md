# ADR-0001: MQTT làm transport, không tự xây trên TCP
- Status: accepted
- Date: 2026-07-09
## Context
Cần "tự chủ truyền thông" cho agent↔server; cân nhắc tự xây protocol trên raw TCP.
## Options đã cân nhắc
1. MQTT 5 (EMQX) — 2. Tự xây trên TCP — 3. gRPC streaming — 4. Zenoh
## Decision
MQTT 5. Tự chủ nằm ở application protocol (topic, schema, state machine) — phần ta sở hữu trong specs/. Transport interface trong agent để không khóa cứng (Publish/Subscribe/Connect), MQTT là implementation đầu tiên.
## Consequences
+ LWT, QoS, reconnect, ecosystem client mọi ngôn ngữ miễn phí.
− Phụ thuộc broker (giảm nhẹ bằng transport interface). WebRTC bổ sung ở Phase 1 cho video — ADR riêng khi build (phía agent là Rust, phía server là Go/Pion).

_Chuẩn hoá 2026-11-08 trước khi tách repo (ADR-0019): bỏ giả định agent dùng Pion (agent là Rust theo ADR-0012)._
