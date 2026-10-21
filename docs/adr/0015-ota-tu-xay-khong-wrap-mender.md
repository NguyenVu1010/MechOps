# ADR-0015: OTA app-level tự xây, không wrap Mender / hawkBit / balena
- Status: accepted
- Date: 2026-10-18
- Covers: [OTA-01, OTA-07, OTA-09]
- Trả nợ constitution #6 cho ADR-0005 (ADR-0005 quyết rollback tại agent nhưng chưa trả lời "vì sao không dùng OSS có sẵn")

## Context

Constitution #6: mọi "tự xây" phải trả lời "vì sao không dùng OSS có sẵn" bằng ADR.
OTA là phần tự xây lớn nhất của Phase 0, và ADR-0005 chỉ nhắc Mender như "playbook
tham chiếu" trong ADR-0002. Ba OSS gần nhất:

| OSS | Có gì ta cần | Thiếu gì |
|---|---|---|
| **Mender** (client Apache 2.0, server có bản OSS) | Update module `docker` và `docker-compose` có rollback; artifact ký; state machine đã battle-tested | Phased rollout, delta, multi-tenant, device filtering là **tính năng trả phí**; server là cụm microservice + MongoDB + NATS; không biết ROS, không white-label; không chạy qua kênh MQTT của ta |
| **Eclipse hawkBit** (Java) | Rollout management, device group | Không có agent; không container-aware; thêm JVM phải vận hành |
| **balena / openBalena** | Container-first, Supervisor open source | Đòi balenaOS trên thiết bị — vendor không đổi OS robot để dùng ta |

## Options đã cân nhắc

1. **Nhúng Mender client làm OTA executor trong agent, server gọi Mender server.**
   Hai agent trên robot (mechops + mender), hai server stack, hai kênh mạng. Phần ta
   cần nhất (staged rollout, OTA-09) lại nằm ở bản trả phí. Vi phạm constitution #5.
2. **Dùng hawkBit làm rollout engine, agent tự viết DDI client.** Thêm JVM + DB riêng
   cho một việc mà Fleet Manager Go làm được trong vài trăm dòng trên Postgres sẵn có.
3. **Tự xây theo ADR-0005, mượn thiết kế của Mender.** ← chọn

## Decision

OTA app-level tự xây trong agent (Rust, ADR-0012) và Fleet Manager (Go). Bề mặt tự
xây được giữ nhỏ bằng cách **mượn ba thiết kế đã được kiểm chứng của Mender**, không
mượn code:

1. **Artifact định danh bằng digest, không bằng tag** (constitution #3, OTA-07). Image
   kéo từ Docker Registry v2 nội bộ của instance, không đóng gói image vào artifact
   như Mender làm — ta có registry sẵn trong Compose, Mender không.
2. **State machine có commit/rollback tường minh, persist trước hành động** (OTA-04/05).
   Mender dùng file state trên đĩa; ta dùng SQLite, cùng nguyên tắc.
3. **Health check là một phần của artifact manifest**, không phải cấu hình ngoài
   (`healthCheck` trong manifest, protocol-notes mục 5.1). Mender gọi đây là
   "update module verify step".

Những gì OTA của ta **không** làm ở Phase 0, và khi cần thì wrap OSS thay vì tự xây:
OS-level/kernel update → wrap **RAUC** (đã ghi ở 02-dev-plan mục 5); delta update →
xét `zstd` diff hoặc Mender delta khi có số đo băng thông; firmware ESP32/STM32 →
`artifactType: firmware-binary` Phase 2 với bootloader của chip.

## Consequences

+ Một agent, một kênh MQTT, một server stack. Staged rollout là của ta, không phải
  tính năng trả phí của ai.
+ Bề mặt tự xây giới hạn ở: state machine (~10 state), Docker swap, health check
  executor, Fleet Manager wave. Toàn bộ có test ID OTA-01..12 canh.
− Ta tự chịu lớp lỗi mà Mender đã trả giá 8 năm. Giảm bằng ma trận [H] OTA-04/05/11/12
  bắt buộc trước mỗi release (quy tắc catalog #4) và bằng việc mượn thiết kế thay vì
  phát minh.
− Không có artifact signing ở Phase 0 ngoài digest. Thêm cosign ký image và binary agent
  ở M3 (việc của plan OTA, không cần ADR riêng vì không thêm service).
