# ĐỌC TRƯỚC: constitution.md — 9 nguyên tắc bất biến.

# CLAUDE.md — MechOps

Luật làm việc trong repo này. Đọc trước khi làm bất kỳ việc gì.

## Nguồn sự thật (đọc theo thứ tự khi cần context)
1. `specs/ (asyncapi.yaml + schemas) — narrative: docs/protocol-notes.md` — hợp đồng MQTT + Probe API. Code không được lệch spec; muốn lệch → dừng, hỏi người.
2. `docs/product/05-test-catalog.md` — định nghĩa "xong". Mỗi tính năng gắn với test ID.
3. `docs/test-status.md` — trạng thái hiện tại. **Việc tiếp theo = test ⬜ đầu tiên của milestone đang mở.**
4. `docs/product/02-dev-plan-phase0.md` — stack đã chốt. Không thêm dependency/công nghệ mới ngoài danh sách nếu chưa hỏi.
5. `specs/schemas/` — JSON Schema + test vectors. Mọi message phải validate.

## Vòng lặp chuẩn
1. Chọn test ID ⬜ theo milestone → nói rõ đang làm ID nào
2. Viết test trước (đỏ) — naming: `Test<ID bỏ gạch>_<MôTả>`, ví dụ `TestOTA07_DigestMismatch`
3. Implement tối thiểu để xanh
4. `make verify` — lệnh DUY NHẤT để cập nhật tracker
5. Trước khi commit: LUÔN chạy subagent spec-guardian rồi test-auditor (hoặc /audit)
6. Commit message có dòng `Implements: <ID>, <ID>`

## Cấm tuyệt đối
- Sửa `docs/test-status.md` / `.json` trực tiếp (hook sẽ chặn — đây là chủ đích, không phải lỗi)
- Skip/comment test để CI xanh
- Đổi nghĩa field trong protocol/schema — đó là quyết định version của founder
- Thêm thư viện ngoài stack đã chốt mà không hỏi
- Tick test [H] — chỉ người chạy `make hw-test` mới tick được

## Lệnh (chi tiết cho người: docs/DEVELOPMENT.md)
- Slash commands: /feature · /task · /audit (định nghĩa trong .claude/commands/)
- `make verify` — fmt + vet + unit test + cập nhật tracker
- `make test-integration` — cần `docker compose up -d` trước
- `make hw-test ID=OTA-04 TESTER=Ng` — biên bản test phần cứng (người chạy)
- `make status` — in tổng kết tracker

## Quy ước Go (chi tiết trong .claude/skills/go-conventions)
- slog mọi log, luôn kèm `deviceId`/`agentId`/`cmdId` nếu có trong ngữ cảnh
- Lỗi wrap bằng `fmt.Errorf("...: %w", err)`, không nuốt lỗi
- SQL qua sqlc, không viết query string trong code Go
