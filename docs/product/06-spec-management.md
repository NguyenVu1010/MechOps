# MechOps — Spec Management & Agent Workflow Plan

> Bổ sung cho AUTOMATION-PLAN.md. Trả lời 3 câu: quản lý spec theo chuẩn nào, workflow agent chạy ra sao, bộ skill quản trị thế nào.
> Nguyên tắc chọn: mượn pattern open-source đã được kiểm chứng, chỉ tự chế phần không ai làm sẵn.

---

## Phần 1 — Quản lý spec: mô hình 4 lớp

Vấn đề của bộ docs hiện tại: 6 file markdown là **narrative** — người đọc tốt, máy đọc kém, và không có cơ chế chống trôi (spec nói A, code làm B, không ai phát hiện). Chuẩn hóa thành 4 lớp, mỗi lớp mượn một pattern có sẵn:

### Lớp 0 — Constitution (pattern: GitHub Spec Kit)
File `constitution.md` — các nguyên tắc **bất khả thương lượng**, viết một lần, sửa cực hiếm:
- TDD bắt buộc: không code trước khi test đỏ tồn tại
- Rollback quyết định tại agent · state ghi trước hành động · pull theo digest
- Một công nghệ mỗi lớp · mọi "tự xây" phải trả lời "vì sao không dùng OSS"
- Tick chỉ do máy · mọi ✅ có evidence

Nội dung này đang rải rác trong CLAUDE.md + README — gom về một file, CLAUDE.md chỉ trỏ tới. Spec Kit gọi đây là gốc của mọi phase sau; với agent, constitution là thứ được nạp vào MỌI phiên.

### Lớp 1 — ADR: Architecture Decision Records (pattern: MADR)
Mỗi quyết định = 1 file bất biến trong `docs/adr/`, format MADR tối giản:

```
docs/adr/0001-mqtt-over-custom-tcp.md
docs/adr/0002-open-core-apache2-agent.md
docs/adr/0003-emqx-over-mosquitto.md
docs/adr/0004-probe-api-unix-socket.md
docs/adr/0005-ota-rollback-at-agent.md
...
```

Mỗi file: Context → Options đã cân nhắc → Decision → Consequences. Các cuộc thảo luận ta đã chốt (TCP vs MQTT, open-core, EMQX, OTA 2 tầng...) chính là nội dung ADR — chuyển lời thoại thành hồ sơ.

**Luật ADR:** không sửa ADR cũ; đổi ý → viết ADR mới đánh dấu `supersedes #NNNN`. Lợi ích với agent: khi Claude Code hỏi "sao không dùng X", câu trả lời nằm trong repo, không nằm trong trí nhớ founder. Đây là chỗ chặn đúng cám dỗ "tự mở lại tranh luận cũ lúc mệt".

### Lớp 2 — Contract máy-đọc-được (pattern: AsyncAPI 3 + JSON Schema)
Đây là nâng cấp quan trọng nhất so với plan cũ. Protocol spec v0.1 hiện là markdown — chuyển phần contract sang chuẩn công nghiệp:

```
specs/
├── asyncapi.yaml            ← channels (topic MQTT), operations, bindings mqtt5,
│                               message → $ref sang schemas/
├── schemas/*.schema.json    ← JSON Schema từng payload (nguồn sự thật DUY NHẤT)
├── testvectors/             ← payload hợp lệ/không hợp lệ (đã plan ở M0)
├── openapi.yaml             ← REST API của server (Phase 0 nhỏ, có từ đầu)
└── probe-api.md             ← Probe API giữ markdown + JSON Schema cho message
```

Vì sao AsyncAPI: nó là chuẩn Linux Foundation cho event-driven API, hỗ trợ MQTT binding chính thức, và quan trọng nhất — **sinh được từ nó**: docs HTML đẹp cho vendor (protocol là phần open source, docs đẹp = marketing), Go types, validator. Chuỗi codegen Phase 0:

```
schemas/*.schema.json ──go-jsonschema──> /protocol/types.gen.go  (struct Go)
                      ──ajv/CI────────> validate testvectors     (TEL-01)
asyncapi.yaml         ──asyncapi cli──> docs HTML cho vendor
```

Lưu ý tỉnh táo: asyncapi-codegen của Go mạnh nhất với NATS/Kafka; với MQTT chỉ nên **sinh types + docs**, phần client MQTT vẫn viết tay quanh paho (mỏng, đã plan). Đừng ép codegen làm quá vai.

Markdown protocol spec v0.1 **không vứt** — nó thành narrative giải thích state machine, hành vi offline, luật cứng; phần bảng payload thay bằng link sang schema. Chuyển đổi này làm trong M0, công sức ~1-2 ngày vì nội dung đã có.

### Lớp 3 — Traceability (pattern: requirement traceability tối giản)
Sợi chỉ xuyên suốt đã có sẵn — test ID. Bổ sung 2 mối nối:
- Mỗi schema/ADR ghi các test ID liên quan ở frontmatter (`covers: [OTA-04, OTA-05]`)
- CI thêm check `trace`: mỗi ID trong catalog phải xuất hiện ở ≥1 file spec và ≥1 file test — ID mồ côi = cảnh báo. Script ~50 dòng, cùng họ track.py.

Kết quả: sợi xích `constitution → ADR → contract → test ID → evidence` — kéo đầu nào cũng lần ra toàn chuỗi.

---

## Phần 2 — Agent workflow: vòng ngoài Spec Kit, vòng trong TDD-evidence

### Cấu trúc 2 vòng

**Vòng ngoài — mỗi feature/milestone (mượn Spec Kit):**
Spec Kit chuẩn hóa flow `constitution → specify → clarify → plan → tasks → implement`, tích hợp Claude Code qua skills mode. Với MechOps, docs 01–05 đã LÀ output của specify/plan cấp dự án — thứ còn thiếu là cấp **feature**: trước mỗi cụm việc (ví dụ "OTA v1" của M3), chạy một lượt:

1. `specify`: mini-spec 1 trang cho feature — hành vi, ngoài scope, test ID nào cover (lấy từ catalog)
2. `clarify`: agent liệt kê điểm mờ → founder trả lời → ghi vào mini-spec (đây là bước người-trong-vòng-lặp quan trọng nhất)
3. `tasks`: bẻ thành task ≤ nửa ngày, mỗi task gắn ≥1 test ID
4. `implement`: vòng trong

Dùng Spec Kit thật (`specify init --integration claude --skills`) hay tự chế 3 template markdown? **Khuyến nghị: tự chế template theo đúng cấu trúc trên.** Spec Kit đầy đủ hơi nặng cho team 1-2 người và ta đã có constitution + test catalog riêng; giá trị nằm ở *cấu trúc flow*, không ở tooling. Xét lại khi team ≥ 3.

**Vòng trong — mỗi task (đã có trong automation kit, giữ nguyên):**
chọn test ID ⬜ → test đỏ → implement → `make verify` → tick ✅ + evidence → commit `Implements: <ID>`.

### Subagents (.claude/agents/) — đúng 2, không hơn

| Subagent | Vai trò | Vì sao tách |
|---|---|---|
| `spec-guardian` | Review diff trước commit: có lệch asyncapi/schema/ADR không, có đổi nghĩa field không, topic có hardcode không | Context riêng, chỉ đọc spec + diff — không bị "quen tay" theo code vừa viết. Người review lạnh. |
| `test-auditor` | Sau `make verify`: soi test vừa viết có assert thật không (chống test rỗng pass), có `t.Skip` lén không, evidence có khớp ID khai báo không | Kiểm toán viên tách khỏi người làm — cùng một agent tự viết tự duyệt là điểm mù kinh điển |

Main agent (implementer) làm mọi thứ còn lại. Không tạo subagent "planner/architect" — việc đó là vòng ngoài có founder tham gia, không ủy quyền.

### Kỷ luật phiên
- **1 phiên = 1 task = 1 nhánh** `feat/<ID>-mô-tả`. Task song song → git worktree, không trộn context.
- Bắt đầu phiên bằng plan mode; agent nêu kế hoạch + test ID trước khi sửa file.
- Phiên dài quá ~60% context → `/compact` hoặc kết phiên, ghi handoff vào task file. Trạng thái thật nằm trong tracker + git, không nằm trong hội thoại — thiết kế này cho phép vứt phiên bất kỳ lúc nào không mất gì.
- Toolkit JSONL monitoring sẵn có của anh gắn vào hooks → mỗi phiên có transcript đối chiếu được với evidence.

### Nấc tự động hóa (đi từng nấc, không nhảy cóc)
1. **Bây giờ:** interactive, founder review mỗi commit
2. **Khi tin cậy (≈ cuối M2):** headless `claude -p` chạy task đơn lẻ qua CI label trên issue — mỗi test ID ⬜ là một issue, gắn label `agent-ok` là agent tự làm PR
3. **Không bao giờ tự động:** merge vào main, sửa specs/, tick [H], release

---

## Phần 3 — Quản trị bộ skill

### Nguyên tắc (theo best practice skill của Anthropic + Spec Kit skills mode)
- **SKILL.md ngắn** (< ~80 dòng), phần dày đẩy sang `reference.md` cùng thư mục — progressive disclosure: agent chỉ nạp chi tiết khi cần
- **Description quyết định 80% giá trị**: phải chứa từ khóa trigger cụ thể (tên file, tên khái niệm, động từ) — skill không được trigger = skill không tồn tại
- **1 skill = 1 mối quan tâm**; skill là "điều repo này làm KHÁC đời", không phải giáo trình

### Bộ skill mục tiêu (tiến hóa từ kit hiện tại)

| Skill | Trạng thái | Nội dung |
|---|---|---|
| `contract-guard` | nâng cấp từ protocol-guard | Sửa `specs/` → chạy validate + codegen lại types + testvectors; đổi nghĩa field → dừng hỏi người; kèm reference.md về AsyncAPI layout |
| `test-evidence` | giữ | như kit |
| `go-conventions` | giữ | như kit |
| `adr` | mới | Khi nào viết ADR (mọi lựa chọn giữa ≥2 phương án có hệ quả dài hạn), template MADR, luật supersede, cập nhật skill liên quan cùng PR |
| `feature-spec` | mới | Template mini-spec/clarify/tasks của vòng ngoài + checklist "task hợp lệ phải có test ID" |

### Luật đồng bộ skill ↔ ADR (chống thối rữa)
Skill mô tả *cách làm hiện hành*; ADR ghi *vì sao*. Mỗi skill ghi frontmatter `adr: [0003, 0005]`. **ADR bị supersede → PR đó bắt buộc cập nhật skill trỏ tới nó** — CI check bằng grep, 20 dòng script. Đây là cơ chế duy nhất giữ skill không nói dối sau 6 tháng.

### Nhịp bảo trì
Mỗi cuối milestone, 30 phút: đọc lại 5 skill, xóa dòng đã thành lỗi thời, thêm bài học từ bug thật của milestone (bug lặp lại 2 lần = thiếu 1 dòng trong skill nào đó). Skill tốt được nuôi bằng sự cố, không bằng dự đoán.

---

## Thứ tự triển khai (chèn vào M0, +2–3 ngày so với plan cũ)

1. `constitution.md` — gom từ CLAUDE.md/README (1 giờ)
2. `docs/adr/0001..0008` — chuyển các quyết định đã chốt thành ADR (nửa ngày, Claude Code làm được từ transcript các buổi thảo luận)
3. `specs/asyncapi.yaml` + JSON Schema hóa payload từ protocol spec v0.1 (1 ngày)
4. Codegen pipeline: go-jsonschema + validate testvectors vào `make verify` (nửa ngày)
5. Skill `adr` + `feature-spec` + nâng `protocol-guard` → `contract-guard` (nửa ngày)
6. 2 subagents + script `trace` CI (nửa ngày)

Đầu tư này hoàn vốn ở M3: OTA là feature phức tạp đầu tiên, và là nơi spec-drift bắt đầu đắt.
