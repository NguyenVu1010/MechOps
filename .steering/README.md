# .steering — plan và nhật ký hành động

Thư mục này giữ **quá trình**: định làm gì (`plans/`) và đã thật sự xảy ra gì
(`entries/`). Hai thứ đó của cùng một hành động nên nằm cạnh nhau — tách ra thì
phải nhảy qua lại mới truy vết được.

`specs/` không chứa plan nữa. Nó trở lại đúng một vai: **hợp đồng máy-đọc-được**
(AsyncAPI + JSON Schema + test vector), là phần open source đi kèm `agent/`,
`protocol/`, `probe/`. Plan là việc nội bộ, và nó ở đây.

```
.steering/
├── README.md              luật + format (file này)
├── INDEX.md               mục lục: plan trước, nhật ký sau — máy sinh
├── plans/
│   ├── TEMPLATE.md
│   └── m3-ota-v1/
│       ├── STATUS.md      MẶT TIỀN      ← máy sinh: cổng nào chốt, task mấy/mấy
│       ├── spec.md        CÁI GÌ        ← từ requirement trong docs/product/
│       ├── clarify.md     CHƯA RÕ GÌ    ← gate người, DỪNG ở đây
│       ├── plan.md        LÀM THẾ NÀO   ← từ ADR + spec
│       ├── testcases.md   LÀM SAO BIẾT XONG  ← thiết kế test từng ID
│       ├── tasks.md       THỨ TỰ        ← dấu tích do MÁY điền từ tracker
│       └── JOURNAL.md     ĐÃ XẢY RA GÌ  ← máy sinh, gom entries có plan: m3-ota-v1
└── entries/
    └── S0007-…md          mục nhật ký, bất biến sau khi đóng
```

**Hai vòng đời khác nhau, đừng lẫn:**

| | Sửa được khi nào | Đóng băng bằng |
|---|---|---|
| `plans/<x>/<artifact>.md` | `status: draft` — bản nháp | `./mo steer plan lock <x> <artifact>` → `locked` |
| `plans/<x>/` cả cụm | tới khi feature xong | `./mo steer plan freeze <x>` → `frozen`, bất biến |
| `entries/S000N` | `outcome: open` — bản nháp | `./mo steer close` → bất biến, sai thì mục mới `supersedes` |

`freeze` từ chối chạy nếu feature còn mục nhật ký `open` — đóng băng kèm nợ là
đóng băng một nửa sự thật.

---

## Năm hệ hồ sơ

Bốn hệ đầu chỉ ghi **thứ sống sót**:

| Hệ | Ghi cái gì | Ai ghi |
|---|---|---|
| `git` | mã còn lại sau khi đã vứt bỏ | người / agent |
| `docs/evidence/` | kết quả `go test -json` thô | `track.py` |
| `docs/test-status.*` · `PROGRESS.md` | trạng thái hiện tại | `track.py` · `progress.py` |
| `docs/adr/` | quyết định kiến trúc đã chốt | người |
| **`.steering/`** | **hành động và ý định — kể cả thứ đã bị vứt bỏ** | agent + hook |

Thư mục này giữ phần đắt nhất khi truy vết sáu tháng sau: **cái đã thử và bỏ, và
vì sao bỏ.** Không có nó, người sau — hoặc chính agent ở phiên khác — sẽ thử lại
đúng con đường đã hỏng và mất đúng số thời gian đó.

---

## Format plan

Bốn file bắt buộc, cùng một frontmatter (`plan new` sinh sẵn):

```yaml
---
plan: m3-ota-v1                       # trùng tên thư mục
milestone: M3
status: open                          # open | frozen
covers: [OTA-01, OTA-02, OTA-07]      # BẮT BUỘC — trace kiểm với catalog
adr: [0005]                           # ADR làm căn cứ; trace kiểm tồn tại + chưa supersede
requirements:                         # truy ngược lên yêu cầu gốc
  - docs/product/01-spec-v2.md#ota
---
```

Ba mối nối này là lý do plan tồn tại ở dạng máy đọc được, không phải văn xuôi:

| Nối | Đứt thì sao | Ai canh |
|---|---|---|
| `covers` → catalog | ID ma thì tracker không bao giờ tick — hỏng im lặng | `./mo trace` |
| `adr` → `docs/adr/` | plan dựa trên quyết định đã bị supersede mà không ai biết | `./mo trace` |
| `tasks.md` → `covers` | task ngoài scope đã thoả thuận | `./mo trace` (cảnh báo) |

`requirements:` trỏ ngược lên `docs/product/` để trả lời "yêu cầu nào đẻ ra feature
này"; `JOURNAL.md` trỏ xuống mọi thứ đã thử. Kéo đầu nào cũng lần ra được cả chuỗi:

```
requirement → ADR → plan → task → test ID → evidence
                     └──→ JOURNAL (cái đã thử và bỏ)
```

### Cổng chốt tuần tự

`status` là của **từng artifact**, không phải cả plan — chốt cả cụm một lần thì gate
tuần tự của SDD không tồn tại. Bẻ task từ plan chưa chốt là bẻ theo thứ còn đổi được.

```bash
./mo steer plan new m3-ota-v1 --milestone M3 --covers "OTA-01,OTA-07" --adr 0005
./mo steer plan lock m3-ota-v1 spec        # cần clarify đã `answered` (gate người)
./mo steer plan lock m3-ota-v1 plan        # cần spec locked
./mo steer plan lock m3-ota-v1 testcases   # cần đủ mục `## <ID>` cho mọi covers
./mo steer plan lock m3-ota-v1 tasks       # cần mọi task có ID trong covers
./mo steer plan sync                       # tick lại tasks.md từ tracker + sinh STATUS.md
./mo steer plan freeze m3-ota-v1           # feature đóng → bất biến
```

Mỗi `lock` kiểm cả nội dung: còn chỗ `<...>` thì chưa chốt được. `./mo trace` chặn
nếu ai lách thứ tự bằng cách sửa tay `status`.

### Dấu tích trong tasks.md do MÁY điền

Task xanh khi **mọi** test ID của nó đã pass trong tracker. Tick tay bị `./mo trace`
chặn: đó chính là cách `tasks.md` biến thành nguồn "đã xong" thứ hai rồi mâu thuẫn
với `docs/test-status.md` — đúng thứ constitution #2 sinh ra để chặn. `./mo status`
tự sync nên checkbox không bao giờ cũ.

### testcases.md giữ thiết kế, không giữ danh sách ID

Danh sách ID là `docs/product/05-test-catalog.md`. File này giữ thứ catalog không
chứa nổi: tiền đề · thao tác · mong đợi (quan sát được từ bên ngoài) · bằng chứng ·
tên test — cộng mục "ID đề xuất thêm" cho hành vi chưa có ID. Chi tiết: `plans/TEMPLATE.md`.

---

## Format bản tin

Một mục = một file trong `entries/`. Tên file:

```
S0007-wrong-golangci-lint-chay-duoc-voi-trong-gowork.md
└─┬─┘ └─┬─┘ └──────────────────┬──────────────────┘
  id   kind          slug ASCII (không dấu)
```

`id` tăng dần, bất biến, cùng quy ước với ADR (`0001-…`) để tham chiếu được trong
hội thoại, trong commit, và trong chính mục khác: *"xem S0007"*.

### Frontmatter — máy đọc

```yaml
---
id: S0007                       # bất biến, do máy cấp
date: 2026-08-23T06:37:15Z      # UTC, máy
kind: wrong                     # attempt | wrong | discovery | decision | risky
outcome: reverted               # open | kept | reverted | superseded
title: "…"                      # LUÔN trích dẫn — dấu ':' không trích dẫn làm vỡ YAML
area: infra                     # agent|server|protocol|probe|dashboard|specs|infra|flow
plan: m3-ota-v1                 # gắn vào plan nào — JOURNAL.md của plan gom theo trường này
milestone: M1                   # milestone đang mở lúc ghi, máy lấy từ tracker
test_ids: [OTA-07]              # ID trong catalog; máy từ chối ID ma
supersedes: [S0003]             # mục này thay thế mục nào
branch: "feat/ota-07-digest"    # máy
commit: 9f5be49                 # máy
evidence: "docs/evidence/ci/…"  # máy, lần verify gần nhất
promoted_to: "OTA-13"           # BẮT BUỘC khi đóng — xem dưới
source: agent                   # agent | hook | human
---
```

Chỉ **năm** trường do người/agent nhập: `kind`, `title`, `area`, `test_ids`, `plan`.
Phần còn lại máy tự điền. Ghi một mục tốn một câu lệnh, không tốn một buổi.

### Thân — sáu mục, tối đa 30 dòng

```markdown
# S0007 · <tiêu đề>

## Vì sao đụng tới      ← cái gì dẫn tới hành động này (1–2 câu)
## Tin rằng             ← giả định, viết ở thì TIN-LÀ-ĐÚNG
## Đã làm               ← file / lệnh cụ thể, gạch đầu dòng
## Bằng chứng           ← quan sát đã kết luận: file:dòng, output, dòng log
## Kết luận             ← kept/reverted + một câu (máy điền lúc close)
## Đã nâng thành        ← test ID / ADR-00NN / dòng skill nào / none
```

Ba mục quyết định giá trị của cả bản tin:

- **Tin rằng** — viết ở thì tin-là-đúng: *"tưởng golangci-lint tự resolve module như
  go build"*. Đừng viết lại thành *"thử cách A"*: giả định sai chính là thứ người sau
  cần đọc, vì họ sắp tin đúng như thế.
- **Bằng chứng** — quan sát, không phải cảm nhận. *"typechecking error: pattern ./…
  does not contain modules listed in go.work"* chứ không phải *"cách đó không ổn"*.
- **Đã nâng thành** — bắt buộc trả lời khi đóng, kể cả bằng `none`. Nhật ký ghi lại
  quá khứ; nó **không ngăn được lần sau**. Thứ ngăn được là một test ID, một ADR,
  hay một dòng trong skill. Ô này buộc phải trả lời câu "vậy lần sau thì sao".

**Trần 30 dòng** là cố ý. Dài hơn nghĩa là nó không phải nhật ký: quyết định thì
viết ADR, hành vi cần canh thì viết test. `./mo trace` cảnh báo khi vượt.

### Năm `kind`

| kind | Dùng khi |
|---|---|
| `attempt` | thử một hướng chưa chắc — đóng bằng `kept` hoặc `reverted` |
| `wrong` | giả định đã tin là đúng, hoá ra sai (nhất là về EMQX, Docker, phần cứng) |
| `discovery` | phát hiện về hệ thống, chưa thành bug |
| `decision` | quyết định nhỏ chưa tới mức ADR |
| `risky` | lệnh có sức phá hoại — **hook ghi tự động**, agent không phải nhớ |

Cố ý không có `revert` (là `attempt` + `outcome: reverted`) và không có `fix`
(bug của chính mình thì nhà của nó là một test ID mới — skill `bug-to-test`).

---

## Luật

1. **Đóng rồi thì bất biến.** Mục đang `open` là bản nháp, sửa thoải mái. Đã đóng
   thì không sửa: viết mục mới với `supersedes: [S000N]`. Nhật ký sửa được là nhật
   ký hết đáng tin — `steer.py close` từ chối đóng lại một mục đã đóng.
2. **`INDEX.md` do máy sinh.** Không gõ tay. `./mo steer index`.
3. **Mục `open` là nợ.** `./mo steer list --open` trước khi kết phiên (skill `handoff` nhắc).
4. **Ghi cả cái sai.** Nhật ký chỉ toàn thành công là nhật ký đã nói dối bằng cách bỏ sót.

## Ghi cái gì

**PHẢI ghi** — hướng đã thử rồi bỏ (kể cả khi không commit dòng nào) · giả định hoá
ra sai · hành động ngoài vòng lặp chuẩn (đổi hạ tầng, sửa config) · quyết định nhỏ
mà người sau sẽ hỏi "sao lại thế".

**KHÔNG ghi** — commit thành công bình thường (`git log`) · kết quả test
(`docs/evidence/`) · quyết định kiến trúc (`docs/adr/`) · trạng thái test
(`docs/test-status.md`). Một sự kiện chỉ có **một** nhà.

## Dùng

```bash
./mo steer new --kind wrong --area infra --ids OTA-07 \
    --title "verify digest bang header cua registry" \
    --context "Dung buoc verify cua OTA-07" \
    --why "Tuong registry tra Docker-Content-Digest o moi response" \
    --did "agent/internal/ota/pull.go: doc header | ./mo verify" \
    --proof "header rong khi di qua proxy — pull.go:88 log digest='' "

./mo steer close --last --outcome reverted \
    --why "doi sang doc digest tu manifest da tai" \
    --promoted "OTA-13 (digest qua proxy)"

./mo steer list --open          # nợ chưa trả
./mo steer list --id OTA-07     # mọi thứ từng làm quanh một test ID
./mo steer list --area agent    # mọi thứ từng thử ở tầng agent
./mo steer list --plan m3-ota-v1  # nhật ký của một feature (= JOURNAL.md)
./mo steer show S0007
```
