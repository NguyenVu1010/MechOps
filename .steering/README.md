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
├── INDEX.md               BÂY GIỜ THẾ NÀO — plan đang mở, plan đã đóng, nhật ký
├── HISTORY.md             ĐÃ ĐI QUA GÌ — một dòng thời gian: plan, cổng chốt,
│                          mục nhật ký, ADR. Máy sinh, mới nhất trên đầu.
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
    └── 2026-08-23T063715Z-S0007-…md   mục nhật ký, bất biến sau khi đóng
```

**Hai vòng đời khác nhau, đừng lẫn:**

| | Sửa được khi nào | Đóng băng bằng |
|---|---|---|
| `plans/<x>/<artifact>.md` | `status: draft` — bản nháp | `./mo steer plan lock <x> <artifact>` → `locked` |
| `plans/<x>/` cả cụm | tới khi feature xong | `./mo steer plan freeze <x>` → `frozen`, bất biến |
| `entries/S000N` | `outcome: open` — bản nháp | `./mo steer close` → bất biến, sai thì mục mới `supersedes` |

`freeze` từ chối chạy nếu feature còn mục nhật ký `open` — đóng băng kèm nợ là
đóng băng một nửa sự thật.

### Plan bỏ giữa đường: `abandon`, không phải `rm -rf`

`draft → locked → frozen` chỉ mô tả plan **đi tới cùng**. Plan bị vứt bỏ cũng cần
một cửa ra, nếu không thì cửa duy nhất là xoá thư mục — và thư mục xoá không để
lại gì, kể cả trong git nếu chưa từng commit. Đã mất một plan đúng theo kiểu đó
(xem `S0007`), nên giờ có:

```
./mo steer plan abandon <x> --why "vì sao dừng" [--next <plan/ADR/test ID>]
```

Nó **không xoá gì**: 5 artifact chuyển `status: abandoned`, `spec.md` nhận
`closed`/`closed_as`/`why_closed`, và một mục nhật ký được mở-rồi-đóng ngay để lý
do nằm trong `JOURNAL.md` của chính plan đó. `--why` là bắt buộc — người sau chỉ
còn ô đó để hiểu vì sao dừng, và `./mo trace` báo lỗi nếu nó rỗng.

Plan làm lại hướng cũ thì khai `--supersedes <plan cũ>` lúc `plan new`. Chuỗi chỉ
ghi **một chiều** (plan mới trỏ plan cũ); chiều ngược INDEX tự suy — vì plan cũ có
thể đã `frozen`, mà `frozen` nghĩa là không sửa được nữa. `./mo trace` chặn nếu
`supersedes` trỏ vào một plan không còn tồn tại: đó chính là dấu hiệu có người xoá.

**Không có plan nào bị xoá.** Cả plan sai, plan bỏ, plan chỉ viết được nửa spec —
tất cả nằm nguyên trong `plans/`, gắn nhãn `abandoned`, và hiện ở bảng "Plan đã
đóng" của `INDEX.md`.

---

## `contract:` — plan nối vào hợp đồng bằng thứ máy kiểm được

`plan.md` mục 1 ("Delta hợp đồng") là **văn xuôi**: không gì kiểm được rằng file
`specs/` vừa đổi đã từng nằm trong kế hoạch. Đó là đúng cách spec-drift bắt đầu —
một field thêm vào giữa lúc implement, không ai duyệt, sáu tháng sau không ai biết
nó từ đâu ra.

`contract:` khai trước, ở `spec.md`. Nhận **file** (`specs/asyncapi.yaml`) hoặc
**thư mục** kết thúc bằng `/` (`specs/schemas/` — cho file plan sẽ TẠO). Chỉ đường
dẫn trong `specs/`: cho khai ngoài đó thì field này thành "danh sách file tôi sẽ
sửa", mà đó là việc của `git diff`.

`tools/checks/contract_touch.py` (bước trong CI) đối chiếu `git diff --name-only ...
-- specs` với `contract:` của mọi plan chưa `abandoned`. File không ai khai → **đỏ**,
kèm hai cách xử lý.

**Cổng tự bật.** Chưa plan nào khai `contract:` thì bỏ qua — M0 đang dựng `specs/`
từ đầu, chặn lúc này thì chốt chặn bị tắt trước khi nó kịp có ích. Có plan đầu tiên
khai là cổng có hiệu lực.

**Mở rộng scope được, nhưng không im lặng.** Lúc implement mới thấy phải sửa thêm
một schema là chuyện thật:

```
./mo steer plan contract <x> --add specs/schemas/alert.schema.json --why "..."
```

`spec.md` còn `draft` thì chỉ thêm vào field. Đã `locked` thì `--why` là **bắt buộc**
và lệnh sinh một mục nhật ký — mở rộng hợp đồng sau khi chốt spec là quyết định.

**Cửa thứ hai: trailer `Contract:`** — cho thay đổi hợp đồng không thuộc feature nào
(dọn scaffolding cũ, đổi tổ chức thư mục, dọn sau một ADR). Bắt những việc đó mượn
một plan thì `contract:` của plan thành nói dối về scope của nó.

```
Contract: specs/features/ — plan chuyển sang .steering/plans/, thư mục này
không còn là hợp đồng (ADR-0011)
```

Trailer nằm ở commit message nào cũng được trong range của PR, khớp theo đường dẫn
hoặc tiền tố (`specs/abc/`). Nó không im lặng: nằm trong `git log` vĩnh viễn, người
duyệt PR đọc thấy, và buộc nêu lý do ngay cạnh đường dẫn.

## Plan đi lạc: `triage` hỏi, người trả lời

Plan không bị xoá cũng chưa chắc còn sống. Nó **im lặng trôi ra khỏi tầm nhìn** —
không ai đóng, không ai làm, tới lúc có người mở lại nhánh cũ thì plan bỏ giữa
đường trông hệt plan đang làm dở. `./mo steer plan triage` đi tìm đúng loại im
lặng đó:

| Dấu hiệu | Ngưỡng | Nghĩa là |
|---|---|---|
| nhánh trong `branch:` không còn | ngay | plan mồ côi — nhánh đã merge hoặc đã xoá |
| mọi ID trong `covers` đã xanh mà plan chưa đóng | ngay | việc xong ở chỗ khác, plan **bị vượt** |
| `milestone` của plan thấp hơn milestone đang mở | ngay | plan quá hạn, milestone đã đi qua |
| `clarify` còn `open` | 7 ngày | treo ở gate người — founder chưa trả lời |
| không chốt cổng nào, không mục nhật ký nào | 14 ngày | **lạc** |
| mục có `revisit` tới hạn | ngày đã hẹn | quyết định tạm cần quyết lại |
| hai mục cùng `id` | ngay | merge hai nhánh — `./mo steer renumber` |

Mỗi mục treo đi kèm **hai lệnh để chọn**, không phải một lời than:

```
./mo steer plan abandon <x> --why "..."      # bỏ, giữ nguyên thư mục
./mo steer plan keep    <x> --why "..."      # vẫn làm tiếp
```

`keep` đóng vòng lặp: nó stamp `reviewed:` + `reviewed_why:` và cập nhật `branch:`
sang nhánh hiện tại, nên triage im trong 14 ngày nữa. Không có nó thì triage hỏi
lại đúng câu ấy mỗi phiên cho tới khi người ta thôi đọc — và một cảnh báo bị bỏ
qua thì tệ hơn không có cảnh báo.

**Nó hiện ra ở bốn chỗ**, không phải chờ ai gõ lệnh: `SessionStart` (đọc cache
`.claude/cache/triage.txt`), `post-checkout` (đổi nhánh là báo ngay), `./mo next` →
`CẦN NGƯỜI QUYẾT` (đứng trước mọi việc mới), và một bước thông tin trong CI.

## Nhiều nhánh, nhiều người

Ba chỗ vỡ khi hai nhánh chạy song song, và cách xử lý từng chỗ:

**1. Trùng `id`.** `next_id()` quét `git log --all` — mọi nhánh, kể cả remote đã
fetch và mục về sau bị xoá — nên nhánh mở sau không cấp lại số của nhánh mở trước.
Trường hợp thật sự đồng thời (hai nhánh cùng cấp `S0008` mà chưa thấy nhau) thì
`trace` chặn lúc merge, `triage` nêu tên, và `./mo steer renumber <mốc thời gian>`
gỡ: đổi số, **giữ nguyên mốc** (mốc là lúc sự việc xảy ra, không phải lúc đánh số
lại), sinh một mục nhật ký ghi việc đổi — đây là ngoại lệ duy nhất của luật "mục đã
đóng thì bất biến", nên nó không được im lặng.

Mục khác đang trỏ `supersedes: [S0008]` thì máy **không tự sửa**, chỉ in ra để người
kiểm: sau merge có hai mục từng mang số đó, nên đoán sai còn tệ hơn hỏi.

**2. Conflict ở file máy sinh.** `INDEX.md`, `HISTORY.md`, `STATUS.md`, `JOURNAL.md`
là **hàm** của `entries/` + `plans/`. Trộn hai nửa bảng markdown chỉ cho ra một bảng
sai mà không ai thấy. Nên `.gitattributes` đặt `merge=ours` (driver bật trong
`./mo hooks-install`), hook `post-merge` sinh lại từ nguồn, và CI có chốt chặn
`.steering không lệch` cho trường hợp hook không chạy.

**3. Không biết nhánh này đang làm plan nào.** `spec.md` khai `branch:` lúc `plan
new`; `post-checkout` in ngay danh sách treo của nhánh vừa vào.

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
status: draft                         # của TỪNG artifact: draft|locked|frozen|abandoned
created: 2026-08-24T18:30:03Z         # mốc UTC, máy
covers: [OTA-01, OTA-02, OTA-07]      # BẮT BUỘC — trace kiểm với catalog
adr: [0005]                           # ADR làm căn cứ; trace kiểm tồn tại + chưa supersede
requirements:                         # truy ngược lên yêu cầu gốc
  - docs/product/01-spec-v2.md#ota
---
```

Bốn field dưới đây **chỉ có ở `spec.md`** — vòng đời của cả plan khai một chỗ, khai
năm chỗ thì có năm phiên bản sự thật về việc plan này còn sống hay đã chết:

```yaml
contract: [specs/asyncapi.yaml, specs/schemas/]   # file specs/ plan sẽ chạm
supersedes: [m3-ota-v0]               # plan này thay cho plan nào (một chiều)
branch: feat/OTA-07-digest            # nhánh mở plan; triage báo nếu nhánh mất
reviewed: 2026-08-25T18:43:20Z        # lần cuối trả lời triage bằng `plan keep`
reviewed_why: "còn chờ founder"       # ...và vì sao vẫn giữ
closed: 2026-08-25T18:28:07Z          # mốc đóng; rỗng = còn đang làm
closed_as: abandoned                  # frozen (xong) | abandoned (bỏ)
why_closed: "chờ ADR về digest"       # BẮT BUỘC khi đã đóng — trace kiểm
```

Mỗi lần `plan lock` thành công, artifact đó nhận thêm `locked: <mốc UTC>`. Không có
mốc thì `status: locked` chỉ nói *đang thế nào*, không nói *đã đi qua những gì* —
và `HISTORY.md` dựng dòng thời gian từ đúng những mốc này.

Ba mối nối này là lý do plan tồn tại ở dạng máy đọc được, không phải văn xuôi:

| Nối | Đứt thì sao | Ai canh |
|---|---|---|
| `covers` → catalog | ID ma thì tracker không bao giờ tick — hỏng im lặng | `./mo trace` |
| `contract` → `specs/` | file hợp đồng đổi mà không ai kế hoạch trước — spec-drift | `contract_touch.py` (CI) |
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
2026-08-23T063715Z-S0007-wrong-golangci-lint-chay-duoc-voi-trong-gowork.md
└────────┬───────┘ └─┬─┘ └─┬─┘ └──────────────────┬──────────────────┘
    mốc UTC          id   kind          slug ASCII (không dấu)
```

**Mốc thời gian đứng trước** để `ls entries/` đọc ra được dòng thời gian của cả
quá trình mà không phải mở file nào, và để thứ tự file trên đĩa trùng thứ tự sự
việc. Dạng mốc y hệt `docs/evidence/ci/` — một quy ước cho mọi thứ có dấu thời
gian trong repo, không phải hai. Bỏ dấu `:` vì Windows cấm ký tự đó trong tên file.

Mốc và `date:` trong frontmatter do **cùng một lần gọi đồng hồ** sinh ra; `./mo trace`
chặn nếu hai chỗ lệch nhau — tên file lệch nghĩa là đã có người đổi tên bằng tay,
và tên đang nói dối về lúc sự việc xảy ra.

`id` tăng dần, bất biến, cùng quy ước với ADR (`0001-…`) để tham chiếu được trong
hội thoại, trong commit, và trong chính mục khác: *"xem S0007"* — tham chiếu vẫn
là `S0007`, không ai phải gõ lại mốc thời gian.

### Bốn field làm nên "bản tin quyết định"

Phần thân kể chuyện; bốn field này để **lọc và nhắc** — thứ văn xuôi không làm được:

| Field | Giá trị | Vì sao có |
|---|---|---|
| `decision` | một câu thể khẳng định | **Bắt buộc với `kind: decision`.** Không nói được đã quyết gì thì nó là ghi chép, không phải quyết định — `./mo trace` chặn. |
| `reversible` | `yes` · `costly` · `no` | Trả lời "có đáng tranh luận lại không". `no` thì tranh luận lại là vô nghĩa; `costly` thì phải cân trước khi đổi. |
| `deciders` | `agent` · `founder` · `agent+founder` · `hook` | `source` nói ai **ghi**; cái này nói ai **quyết**. Constitution #9 chỉ ràng buộc chuyện thứ hai. |
| `revisit` | `YYYY-MM-DD` | Quyết định **tạm**. Tới hạn thì `triage` nhắc — không có ô này thì "tạm" nghĩa là vĩnh viễn. |

Và một mục thân mới: **`## Đã cân nhắc`** — phương án khác đã nghĩ tới, kèm *vì sao
không chọn*. Đây là phần người sau cần nhất và cũng là phần biến mất đầu tiên: sáu
tháng sau, cái đã bị loại trông như cái chưa ai nghĩ tới, nên nó được thử lại.

### Frontmatter — máy đọc

```yaml
---
id: S0007                       # bất biến, do máy cấp — quét cả git log --all
date: 2026-08-23T06:37:15Z      # UTC, máy
decision: "..."                 # BẮT BUỘC với kind: decision
reversible: costly              # yes | costly | no
deciders: agent+founder         # ai QUYẾT (khác source: ai GHI)
revisit: 2026-09-30             # quyết định tạm; triage nhắc khi tới hạn
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
