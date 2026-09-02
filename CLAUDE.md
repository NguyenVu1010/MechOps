# ĐỌC TRƯỚC: constitution.md — 9 nguyên tắc bất biến.

# CLAUDE.md — MechOps

Luật làm việc trong repo này. Đọc trước khi làm bất kỳ việc gì.

## Môi trường: mọi lệnh đi qua `./mo`, không phải `make`

Toolchain (Go, Python, golangci-lint) nằm trong Docker — máy dev không cài gì
ngoài Docker (ADR 0010). Gõ `make` trực tiếp sẽ báo "command not found".

- `./mo verify` — **lệnh DUY NHẤT cập nhật tracker** (gen + lint + vet + test -race)
- `./mo status` — tracker + sinh `docs/PROGRESS.md`
- `./mo trace` — ID mồ côi, skill lệch ADR, milestone lệch catalog
- `./mo steer plan triage` — **plan/quyết định đang treo, cần người quyết**
  (mồ côi nhánh · bị vượt · treo gate người · im lặng 14 ngày · trùng id sau merge).
  Trả lời bằng `plan keep --why` hoặc `plan abandon --why`, không bỏ qua.
- `./mo doctor` — môi trường thiếu gì
- `./mo hw-test ID=OTA-04 TESTER=<tên>` — biên bản test phần cứng (**người** chạy)

## Nguồn sự thật (đọc theo thứ tự khi cần context)

1. `specs/` (asyncapi.yaml + schemas) — hợp đồng MQTT + Probe API. **Chỉ hợp đồng**;
   plan của feature nằm ở `.steering/plans/`.
   Narrative: `docs/protocol-notes.md`. Code lệch spec là bug của code.
2. `docs/product/05-test-catalog.md` — định nghĩa "xong". Mỗi tính năng gắn test ID.
3. `docs/test-status.md` — trạng thái. Dòng "Milestone đang mở" ở đầu file trả lời
   thẳng câu **việc tiếp theo là gì**. `docs/PROGRESS.md` cho burndown và nhịp độ.
4. `docs/product/02-dev-plan-phase0.md` — stack đã chốt.
5. `docs/adr/` — vì sao mọi thứ như hiện tại. Đừng mở lại tranh luận đã có ADR.

## Vòng lặp chuẩn

1. Chọn test ID ⬜ của milestone đang mở → **nói rõ đang làm ID nào**
2. Viết test trước, chạy để thấy nó **đỏ thật** — naming `Test<ID bỏ gạch>_<MôTả>`
   (ví dụ `TestOTA07_DigestMismatch`)
3. Implement tối thiểu để xanh
4. `./mo verify`
5. `/audit` — spec-guardian rồi test-auditor, cả hai phải PASS
6. Commit với dòng `Implements: <ID>, <ID>` (hook `commit-msg` chặn nếu thiếu)
7. `/pr` khi sẵn sàng đưa cho người duyệt

## Cấm tuyệt đối

- Sửa `docs/test-status.*` hoặc `docs/PROGRESS.md` trực tiếp — máy ghi, hook chặn.
  Bị chặn là chủ đích, không phải lỗi cần lách.
- Sửa mục **đã đóng** trong `.steering/entries/`, gõ tay `.steering/INDEX.md`,
  `HISTORY.md` hoặc `JOURNAL.md`. Nhật ký bất biến như ADR: sai thì viết mục mới
  trỏ ngược về mục cũ. (`plans/<x>/` sửa được tới khi `./mo steer plan freeze`.)
- **Xoá thư mục trong `.steering/plans/`** — kể cả plan sai, plan bỏ dở, plan chỉ
  viết được nửa spec. Bỏ một hướng đi là `./mo steer plan abandon <x> --why "..."`:
  thư mục giữ nguyên, lý do vào nhật ký. Đã mất một plan vì xoá (`S0007`).
- `t.Skip` hoặc comment test để CI xanh. Test đỏ = việc chưa xong.
- Đổi nghĩa / xoá field trong `specs/` — breaking change, quyết định của founder.
- Sửa file trong `specs/` mà plan chưa khai trong `contract:` — CI đỏ
  (`./mo check-contract`). Khai thêm: `./mo steer plan contract <x> --add <path> --why "..."`.
  Việc không thuộc feature nào thì khai bằng trailer `Contract: <path> — <lý do>`.
- Thêm thư viện ngoài stack đã chốt mà chưa có ADR.
- Tick test [H] — chỉ người chạy `./mo hw-test` mới tick được.
- Merge vào `main` (constitution #9).

## Skill — không nhớ gì cả, gõ `/dev`

**`/dev` là cửa vào duy nhất.** Nó chạy `./mo next` để chẩn đoán đang ở bước nào
rồi gọi đúng skill tiếp theo. Không cần thuộc thứ tự 8 bước bên dưới.

**Vòng ngoài (SDD)** — `/brainstorm` (chưa rõ đường) → `./mo steer plan new` →
`/feature` → `/tech-plan` → `/spec-analyze`.

**Vòng trong (TDD)** — `/task <ID>` → ĐỎ (chứng minh) → XANH (tối thiểu) → GỌN
(refactor) → `./mo verify` → `/audit` → commit → `/pr`.

| Tình huống | Skill |
|---|---|
| **Không biết làm gì tiếp** | **`/dev`** |
| Chưa rõ nên làm theo cách nào | `/brainstorm` |
| Mở feature/milestone mới | `/feature` |
| Có spec+clarify, chưa bẻ task | `/tech-plan` |
| Vừa sửa spec/plan/tasks | `/spec-analyze` |
| Bắt đầu một test ID | `/task <ID>` |
| **Test đỏ không rõ vì sao** | `troubleshoot` — tái hiện trước, sửa sau |
| **Phát hiện bug** | `bug-to-test` — thêm test ID mới TRƯỚC khi sửa |
| **Vứt bỏ một hướng / giả định sai** | `steering` — ghi `.steering/` ngay lúc đổi hướng |
| Trước khi commit | `/audit` |
| Sẵn sàng mở PR | `/pr` |
| Hết giờ / phiên dài | `/handoff` |

Tự nạp khi chạm file tương ứng: `contract-guard` (`specs/`), `go-conventions`
(`*.go`), `test-evidence` (`*_test.go`), `security-guard` (cert/ACL/token/PTY/digest),
`feature-spec` (`.steering/plans/`). Rule trong `.claude/rules/` tự nạp theo thư mục.

## Quy ước Go (chi tiết: skill `go-conventions`)

- `slog` cho mọi log, kèm `deviceId`/`agentId`/`cmdId`/`deploymentId` khi có ngữ cảnh
- Lỗi wrap `fmt.Errorf("ngữ cảnh: %w", err)` — không nuốt, không log-rồi-return-nil
- SQL qua sqlc trong `server/queries/*.sql`, không có query string trong `.go`
- `context.Context` là tham số đầu của mọi hàm chạm network/DB
