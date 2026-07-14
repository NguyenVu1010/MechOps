---
name: protocol-guard
description: BẮT BUỘC đọc trước khi sửa bất kỳ thứ gì trong schemas/, message struct Go (envelope, telemetry, state, events, cmd, OTA manifest), topic string MQTT, hoặc Probe API. Trigger với từ khóa: schema, payload, topic, envelope, profile, manifest, probe hello.
---

# Protocol Guard

Protocol spec (`docs/04-protocol-spec-v0.1.md`) là hợp đồng. Code đi theo spec, không ngược lại.

## Luật
1. Sửa schema/struct message → chạy validate TOÀN BỘ `schemas/testvectors/` trước khi kết thúc: `make verify` (bao gồm TEL-01).
2. Thêm field mới: PHẢI optional, bên nhận cũ phải bỏ qua được (forward-compat, spec mục 1). Thêm test vector mới cho field đó.
3. Đổi tên/đổi nghĩa/xóa field đang có: DỪNG LẠI. Đây là breaking change → tăng version topic → quyết định của founder. Hỏi, không tự làm.
4. Topic string: chỉ dùng constant trong package `protocol`, không hardcode string ở nơi khác. Grep trước khi thêm constant mới.
5. Payload > 64KB → từ chối ở agent (spec mục 9). Mọi encoder mới phải có check này.
6. Nhớ ánh xạ VDA 5050 (spec mục 8): sửa `profiles.amr` thì kiểm tra mapping còn sạch không, ghi chú vào PR nếu ảnh hưởng.
