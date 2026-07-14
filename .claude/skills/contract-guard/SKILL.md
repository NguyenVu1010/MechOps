---
name: contract-guard
description: BẮT BUỘC đọc trước khi sửa bất kỳ thứ gì trong specs/ (asyncapi.yaml, schemas/, testvectors/), message struct Go (envelope, telemetry, state, events, cmd, OTA manifest), topic string MQTT, hoặc Probe API. Trigger với từ khóa: schema, payload, topic, envelope, profile, manifest, probe hello, asyncapi, contract.
adr: [0001]
---

# Contract Guard

`specs/` (AsyncAPI 3 + JSON Schema) là hợp đồng — nguồn sự thật DUY NHẤT của payload.
Narrative (state machine, offline, luật cứng): `docs/protocol-notes.md`. Code đi theo spec, không ngược lại.
Layout chi tiết của specs/: đọc `reference.md` cùng thư mục.

## Luật
1. Sửa BẤT KỲ file nào trong `specs/` → trước khi kết thúc PHẢI chạy: `make gen` (validate toàn bộ testvectors + codegen types khi pipeline sẵn sàng) rồi `make verify`. Types Go sinh từ schema — không sửa tay `types.gen.go`.
2. Thêm field mới: PHẢI optional, bên nhận cũ phải bỏ qua được (forward-compat, TEL-07). Thêm test vector mới cho field đó (cả valid lẫn invalid nếu có ràng buộc), cập nhật `covers:` của schema.
3. Đổi tên/đổi nghĩa/xóa field đang có: DỪNG LẠI. Breaking change → tăng version topic → quyết định của founder. Hỏi, không tự làm.
4. Topic string: chỉ dùng constant trong package `protocol` (`protocol/topics.go`), không hardcode string ở nơi khác. Grep trước khi thêm constant mới. Topic mới phải khai trong `asyncapi.yaml` CÙNG commit.
5. Payload > 64KB → từ chối ở agent (protocol-notes mục 9). Mọi encoder mới phải có check này.
6. Nhớ ánh xạ VDA 5050 (protocol-notes mục 8): sửa `profiles.amr` thì kiểm tra mapping còn sạch không, ghi chú vào PR nếu ảnh hưởng.
7. Schema mới → có `covers:` trỏ test ID trong catalog; `make trace` phải sạch lỗi.
