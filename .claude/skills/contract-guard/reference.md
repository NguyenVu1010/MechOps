# Contract Guard — reference: layout specs/

```
specs/
├── asyncapi.yaml          ← channels (topic MQTT), operations, bindings mqtt5;
│                             message KHÔNG định nghĩa inline — $ref sang schemas/
├── schemas/*.schema.json  ← JSON Schema draft 2020-12 từng payload — nguồn sự thật DUY NHẤT
│                             mỗi file có "covers": [test IDs] cho make trace
├── testvectors/
│   ├── valid/             ← payload phải PASS validate
│   └── invalid/           ← payload phải FAIL validate (tên file nói rõ vì sao, vd telemetry-missing-seq.json)
├── features/<mX-tên>/     ← mini-spec vòng ngoài (spec.md, clarify.md, tasks.md) — skill feature-spec
├── openapi.yaml           ← REST API server (thêm ở M0+)
└── probe-api.md           ← Probe API: Unix socket, NDJSON; JSON Schema hóa dần vào schemas/probe-*.schema.json
```

## Quy ước schema
- `$id`: `https://mechops.io/schemas/<tên>.schema.json`
- Mọi payload MQTT có envelope chung: `v` (const version), `ts` (epoch ms UTC), `seq` — xem telemetry.schema.json làm mẫu
- `additionalProperties: true` ở mọi object nhận từ xa — forward-compat là luật (TEL-07)
- Ràng buộc biểu diễn được bằng schema thì để schema giữ (range, enum, required) — đừng lặp lại trong code Go

## Chuỗi sinh mã (Makefile `gen`)
```
schemas/*.schema.json ──go-jsonschema──> protocol/types.gen.go   (TODO M0)
                      ──validate_vectors.py──> pass/fail testvectors (TEL-01)
asyncapi.yaml         ──asyncapi cli──> docs HTML cho vendor      (TODO M0+)
```
asyncapi-codegen của Go yếu với MQTT — CHỈ sinh types + docs từ nó; MQTT client viết tay quanh paho (ADR-0001).

## Checklist sửa contract (chạy trong đầu trước khi commit)
- [ ] Field mới optional? Bên nhận cũ bỏ qua được?
- [ ] Test vector valid + invalid cập nhật?
- [ ] `covers:` cập nhật, `make trace` sạch?
- [ ] Topic mới có trong asyncapi.yaml VÀ protocol/topics.go, không hardcode nơi khác?
- [ ] `make gen && make verify` xanh?
