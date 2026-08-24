# MechOps — AI flow: toàn cảnh và chỗ cưỡng chế

> Bổ sung cho `06-spec-management.md`. Tài liệu 06 nói *nên* làm gì; tài liệu này
> nói cái đó *đang được ép bằng gì*, và ở đâu trong repo.
> Quyết định nền: ADR-0010 (toolchain trong Docker), ADR-0011 (cưỡng chế bằng máy).

---

## 1. Toàn cảnh một feature

**Cửa vào duy nhất: `/dev`** — chạy `./mo next`, chẩn đoán đang ở bước nào rồi
chuyển tiếp. Sơ đồ dưới là thứ nó điều hướng, không phải thứ phải thuộc lòng.

```
/dev  ──►  ./mo next  ──►  chuyển tiếp tới đúng bước bên dưới
        (tracker · plans/*/status · mục steering open · nhánh git)

/brainstorm          (chỉ khi chưa rõ đường — kết bằng lựa chọn + ADR cần viết)
        │
        ▼            ┌─── GATE NGƯỜI ───┐
/feature <tên>       │                  │   .steering/plans/<mX-ten>/
   specify  ─► spec.md   (covers, requirements, adr)
   clarify  ─►│  clarify.md (DỪNG)      │  founder trả lời từng câu hỏi
   plan     ─►│  plan.md                │  ~15 phút/feature
   tasks    ─►│  tasks.md               │
   analyze  ─►┴──────────────────────────┘  spec ↔ plan ↔ tasks ↔ catalog
        │
        ▼  vòng trong, mỗi test ID một phiên
/task <ID>
   ĐỎ ──► XANH ──► GỌN ──► ./mo verify ──► /audit ──► commit
   │                           │              │           │
   chứng minh đỏ thật     tracker+evidence    │      commit-msg hook
   (không phải compile lỗi)              spec-guardian
                                         test-auditor
        │  ├─ đỏ không rõ vì sao ──► troubleshoot (tái hiện trước, sửa sau)
        │  ├─ là bug thật ─────────► bug-to-test  (test ID mới TRƯỚC khi sửa)
        │  └─ bỏ một hướng ────────► steering --plan <mX-ten> ──┐
        │                                                       ▼
        │                              .steering/plans/<mX-ten>/JOURNAL.md
        ▼
/pr ──► ./mo verify · trace · /audit · /code-review · digest ──► gh pr create
        │
        ▼            ┌─── GATE NGƯỜI ───┐
   CI (pr.yml) ──────┤ founder duyệt    │  ~5 phút: tick mới, 1 link evidence,
   6 chốt chặn       │ và merge         │  kết luận 2 kiểm toán viên
                     └──────────────────┘
        │
        ▼            ┌─── GATE NGƯỜI ───┐
   test [H]  ────────┤ ./mo hw-test     │  chỉ người tick được
                     └──────────────────┘
```

Ba gate người là ba chỗ **cố tình không tự động hoá** (constitution #9). Mọi thứ
giữa chúng nên tự chạy.

---

## 2. Mỗi luật được cưỡng chế ở đâu

Bảng này là để trả lời câu "cái gì bắt lỗi này?" mà không phải đi đọc code.

| Luật | Nguồn | Chốt chặn | Chạy lúc nào |
|---|---|---|---|
| Test đỏ trước khi code | constitution #1 | `test-auditor` (test rỗng-mà-pass), người | `/audit` |
| Tick chỉ do máy | constitution #2 | hook `PreToolUse` + CI render lại `.md` từ `.json` rồi `git diff --exit-code` | mỗi Edit · mỗi PR |
| Ghi state trước hành động | constitution #3 | `.claude/rules/agent-ota.md` + `REVIEW.md` (🔴) | khi chạm `agent/` |
| Spec thắng code | constitution #4 | `spec-guardian`, `./mo gen` (validate testvectors) | `/audit` · mỗi PR |
| Một công nghệ mỗi lớp | constitution #5 | `./mo trace` (skill ↔ ADR), review người | mỗi PR |
| Tự xây phải có ADR | constitution #6 | `./mo trace`, checklist PR template | mỗi PR |
| agent không import server | constitution #7 | `golangci-lint` rule `depguard` | mỗi lint |
| Quyết định ghi bằng ADR | constitution #8 | `./mo trace` (ADR supersede mà skill chưa đổi = LỖI) | mỗi PR |
| Không tự động merge/[H]/specs | constitution #9 | không có tự động hoá nào làm được — theo thiết kế | — |
| Mỗi commit khai test ID | catalog #1 | `.githooks/commit-msg` + CI quét dải commit | mỗi commit · mỗi PR |
| [H] có biên bản ký tên | catalog #2 | `./mo hw-test` sinh biên bản; Claude không tick được [H] | khi người chạy |
| Bug mới → test ID mới trước | catalog #3 | skill `bug-to-test` (tự trigger theo từ khoá "bug/lỗi/fix") | khi gặp bug |
| Release = [U][I] xanh | catalog #4 | CI `pr.yml` + nightly | mỗi PR · hằng đêm |
| slog, không `fmt.Print` | go-conventions | `golangci-lint` rule `forbidigo` | mỗi lint |
| Không nuốt lỗi | go-conventions | `errcheck`, `errorlint` | mỗi lint |
| Milestone khớp catalog | (mới) | `./mo trace` đối chiếu `track.py` ↔ `05-test-catalog.md` | mỗi PR |
| Frontmatter skill/rule hợp lệ | (mới) | `./mo trace` — YAML hỏng, key lạ, rule thiếu `paths` | mỗi PR |
| Lệnh phá hoại để lại dấu vết | (mới) | hook `PreToolUse(Bash)` ghi `.steering/` `kind: risky` | mỗi lệnh Bash |
| Nhật ký truy vết được | (mới) | `./mo trace` — INDEX khớp entries, `test_ids` có thật | mỗi PR |
| Plan nối đúng lên/xuống | (mới) | `./mo trace` — `covers`→catalog, `adr`→ADR chưa supersede, tasks⊆covers | mỗi PR |

Nguyên tắc phân tuyến (ADR-0011): **luật xác định được bằng cú pháp thì máy kiểm;
luật cần phán đoán thì subagent hoặc người.** Không dùng LLM để làm việc của `grep`.

---

## 3. Bộ skill

Skill là "điều repo này làm KHÁC mặc định", không phải giáo trình.

**Vòng ngoài — SDD**

| Skill | Kiểu nạp | Vai trò |
|---|---|---|
| **`dev`** | **`/dev`** | **cửa vào duy nhất — `./mo next` chẩn đoán rồi chuyển tiếp** |
| `brainstorm` | tự động / `/brainstorm` | mở không gian phương án, kết bằng lựa chọn + ADR cần viết |
| `feature` | `/feature` | `./mo steer plan new` rồi dẫn chuỗi specify → clarify → plan → tasks → analyze |
| `feature-spec` | tự động (`.steering/plans/**`) | cấu trúc 4 file của một feature |
| `tech-plan` | `/tech-plan` | `plan.md`: delta hợp đồng, state machine, ma trận thất bại, chia tầng |
| `spec-analyze` | `/spec-analyze` | đối chiếu chéo spec ↔ plan ↔ tasks ↔ catalog |
| `adr` | tự động (từ khoá) | khi nào viết ADR, luật supersede |

**Vòng trong — TDD**

| Skill | Kiểu nạp | Vai trò |
|---|---|---|
| `task` | `/task <ID>` | một phiên một test ID; đỏ (chứng minh) → xanh → gọn |
| `test-evidence` | tự động (`**/*_test.go`) | naming, tier, cách tick · `reference.md` cho quy trình [U]/[I]/[H] |
| `go-conventions` | tự động (`**/*.go`) | quy ước Go của repo |
| `contract-guard` | tự động (`specs/**`, `protocol/**`) | luật sửa hợp đồng |
| `troubleshoot` | tự động (từ khoá) | khoanh tầng, đọc evidence, tái hiện trước khi sửa |
| `bug-to-test` | tự động (từ khoá) | bug → test ID mới TRƯỚC khi sửa |

**Review · bảo mật · kết phiên**

| Skill | Kiểu nạp | Vai trò |
|---|---|---|
| `audit` | `/audit` | hai kiểm toán viên độc lập trước commit |
| `pr` | `/pr` | dựng PR duyệt được trong 5 phút |
| `security-guard` | tự động (`agent/`, `server/`, `deploy/`, từ khoá) | bất biến về cert/ACL/tenant/digest/PTY |
| `steering` | tự động (từ khoá đổi hướng) | ghi `.steering/`: cái đã thử và bỏ |
| `handoff` | `/handoff` | kết phiên sạch, đẩy trạng thái ra khỏi hội thoại |

### Hồ sơ — mỗi thứ một nhà

Mọi hệ trước `.steering/` chỉ ghi **thứ sống sót**. `.steering/` ghi phần còn lại.

| Hệ | Ghi cái gì | Ai ghi | Sửa được không |
|---|---|---|---|
| `git` | mã còn lại sau khi đã vứt bỏ | người / agent | lịch sử bất biến |
| `specs/` | **hợp đồng** máy-đọc-được (AsyncAPI + Schema + vector) | người | breaking change = quyết định founder |
| `docs/evidence/` | kết quả `go test -json` thô | `track.py` | không |
| `docs/test-status.*` · `PROGRESS.md` | trạng thái hiện tại | `track.py` · `progress.py` | không (hook chặn) |
| `docs/adr/` | quyết định kiến trúc | người | không (supersede) |
| **`.steering/plans/`** | **định làm gì**: spec · clarify · plan · tasks | agent + người | được, tới khi `freeze` |
| **`.steering/entries/`** | **đã xảy ra gì**, kể cả thứ bị vứt bỏ | agent + hook | không (mục mới `supersedes`) |

Quy tắc phân nhà: một sự kiện chỉ có **một** nhà.

**Plan của feature nằm ở `.steering/plans/`, không ở `specs/`.** `specs/` trở lại
đúng một vai — hợp đồng máy-đọc-được, phần open source đi kèm `agent/`, `protocol/`,
`probe/`. Plan là quá trình nội bộ, và nó thuộc về cùng chỗ với nhật ký: mở thư mục
plan ra là thấy cả thứ đã định làm (`plan.md`) lẫn thứ đã thử rồi bỏ (`JOURNAL.md`,
máy sinh từ các mục có `plan: <tên>`). Tách hai thứ đó ra thì phải nhảy hai thư mục
mới truy vết được một hành động.

Chuỗi truy vết đầy đủ, kéo đầu nào cũng lần ra:

```
docs/product/ (requirement) → docs/adr/ → plans/<x>/plan.md → tasks.md
                                   ↓                              ↓
                            JOURNAL.md (đã thử & bỏ)         test ID → evidence
```

`spec.md` của mỗi plan khai `requirements:` (trỏ ngược lên) và `covers:` (trỏ xuống);
`./mo trace` kiểm cả hai đầu, cộng với `adr:` phải tồn tại và chưa bị supersede.

Format bản tin đầy đủ: `.steering/README.md` (không chép lại ở đây — đúng cái lỗi
hai-nguồn-sự-thật mà cả tài liệu này đang chống). Ba điểm thiết kế đáng nêu:

- **`id: S0007`** cùng quy ước với ADR, để tham chiếu được trong hội thoại, trong
  commit, và trong mục khác qua `supersedes: [S0003]`.
- **`promoted_to` bắt buộc khi đóng**, kể cả bằng `none`. Nhật ký ghi lại quá khứ;
  nó **không ngăn được lần sau**. Thứ ngăn được là một test ID, một ADR, hay một
  dòng trong skill — ô này buộc phải trả lời câu "vậy lần sau thì sao". Đây là chỗ
  nhật ký nối vào phần còn lại của quy trình thay vì trở thành nghĩa địa ghi chép.
- **Trần 30 dòng thân.** Dài hơn nghĩa là nó không phải nhật ký: quyết định thì viết
  ADR, hành vi cần canh thì viết test. `./mo trace` cảnh báo khi vượt.

Loại `risky` do **hook ghi tự động**, không do agent tự khai: lệnh phá hoại
(`git reset --hard`, `--no-verify`, `rm -rf`, `--force`…) là loại hành động đáng
truy vết nhất và cũng là loại ít được tự nguyện khai nhất. Hook **không chặn** —
chặn thì agent tìm đường vòng; ghi thì hành động vẫn xảy ra nhưng để lại dấu vết.

Skill có side effect (`feature`, `tech-plan`, `spec-analyze`, `task`, `audit`, `pr`,
`handoff`) đặt
`disable-model-invocation: true` — chỉ người gõ mới chạy. Không để agent tự quyết
định "code trông xong rồi, mở PR thôi".

`.claude/rules/` nạp theo thư mục đang chạm: `agent-ota.md` (agent/),
`server-data.md` (server/). Rule khác skill ở chỗ nó vào context tự động và
không cần lý do — đúng cho thứ luôn đúng trong một thư mục.

**Vẫn đúng 2 subagent** (`spec-guardian`, `test-auditor`) như 06 đã chốt. Nhu cầu
mới giải bằng skill, không đẻ thêm subagent.

---

## 4. Nhìn thấy tiến độ ở đâu

| Chỗ | Nội dung | Sinh bởi |
|---|---|---|
| statusline Claude Code | `M1 0/16 · next PRV-01 · tổng 0/49 · <nhánh>` | `.claude/statusline.sh` đọc cache |
| context đầu phiên | milestone đang mở, ID tiếp theo, số test đỏ, file chưa commit | hook `SessionStart` |
| `docs/test-status.md` | dòng "Milestone đang mở" + bảng từng nhóm | `track.py` |
| `docs/PROGRESS.md` | burndown từng milestone, nhịp độ tick/tuần, ETA thô | `progress.py` |
| comment PR | tick mới, evidence, ID khai vs ID xanh, specs đã đổi | `pr_digest.py` |

Cả năm chỗ đọc từ **một nguồn**: `docs/test-status.json`, do `track.py` ghi.
Không có chỗ nào cho người gõ tay vào.

---

## 5. Nguồn tham chiếu

Thiết kế trên không tự nghĩ ra; đây là chỗ tra lại khi cần xét lại một lựa chọn.

| Vấn đề | Nguồn | Lấy gì |
|---|---|---|
| Cấu trúc skill, frontmatter | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) | `paths`, `allowed-tools`, `disable-model-invocation`, `context: fork`; "custom commands đã gộp vào skills" |
| Viết skill cho tốt | [Anthropic — Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | progressive disclosure; chỉ đưa vào skill thứ đẩy Claude ra khỏi mặc định |
| Hook | [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) | `SessionStart.additionalContext`, `PreToolUse.permissionDecision`, `PreCompact`; ngữ nghĩa exit code |
| Rule theo thư mục, cỡ CLAUDE.md | [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) | `.claude/rules/` với `paths:`; CLAUDE.md nên dưới 200 dòng |
| Subagent | [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents) | cô lập context; khi nào KHÔNG nên tách subagent |
| Review tự động | [code.claude.com/docs/en/code-review](https://code.claude.com/docs/en/code-review) | `REVIEW.md`: hiệu chỉnh severity, cap nit, yêu cầu bằng chứng `file:dòng` |
| Vòng ngoài | [github/spec-kit](https://github.com/github/spec-kit) | `constitution → specify → clarify → plan → tasks → analyze → implement`; bước **analyze** |
| ADR | [MADR](https://adr.github.io/madr/) | Context → Options → Decision → Consequences; luật bất biến + supersede |
| Linter Go | [golangci-lint](https://golangci-lint.run/docs/linters/) | bộ linter; `depguard` để ép chiều phụ thuộc |

---

## 6. Nhịp bảo trì

- **Cuối mỗi milestone, 30 phút:** đọc lại toàn bộ skill và rule. Xoá dòng đã lỗi
  thời, thêm bài học từ bug thật. Bug lặp hai lần = thiếu một dòng ở đâu đó.
- **Chốt chặn gây phiền nhiều hơn giúp** thì sửa hoặc bỏ nó — kèm ADR. Chốt chặn bị
  vô hiệu hoá âm thầm (`--no-verify` thành thói quen) tệ hơn không có chốt chặn.
- **Không thêm chốt chặn cho luật chưa từng bị vi phạm.** Bộ này sinh ra từ lỗ hổng
  quan sát được, không từ dự đoán.
