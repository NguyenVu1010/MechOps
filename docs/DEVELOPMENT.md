# Hướng dẫn phát triển (cho người)

> Agent đọc CLAUDE.md — file này dành cho dev. Nội dung trùng nhau chỉ có MỘT nhà:
> vòng lặp & luật ở CLAUDE.md · nguyên tắc bất biến ở constitution.md · "vì sao" ở docs/adr/
> · toàn cảnh flow và bảng "luật nào chặn ở đâu" ở docs/product/07-ai-flow.md.

**Chưa từng làm việc trong repo này?** Đọc `docs/product/html/dev-flow.html` trước
(mở bằng trình duyệt) — giải phẫu bộ máy từ một test ID tới CI, kèm lưu đồ, khoảng
25 phút. File bạn đang đọc là bản tra cứu hằng ngày, không phải bản nhập môn.

## Cài đặt

Máy chỉ cần **Docker Desktop + git + Claude Code**. Go, Python, make, golangci-lint
nằm trong container (ADR-0010) — không cài gì lên máy.

```bash
./mo up              # dựng container dev (lần đầu vài phút)
./mo hooks-install   # bật git hook — Claude Code tự bật giúp ở SessionStart,
                     # cần gõ tay nếu bạn làm việc ngoài Claude Code
./mo doctor          # xác nhận môi trường đủ
./mo status          # sinh tracker, thấy 49 test ⬜
```

Trên PowerShell dùng `.\mo.ps1` thay cho `./mo`.

## Quy trình 1 feature — vai trò của bạn ở 3 gate

| Gate | Việc của bạn | Thời gian |
|---|---|---|
| 1. Clarify | Agent chạy `/feature <tên>` xong sẽ dừng ở `clarify.md` — trả lời từng câu hỏi thẳng vào file. Giả định sai bị giết ở đây rẻ hơn trong code. | ~15 phút/feature |
| 2. Review PR | Bot đã đăng "PR digest" ở comment đầu: tick mới, link evidence, ID khai vs ID thật xanh, `specs/` đã đổi. Bạn nhìn 3 thứ: **mở 1 link evidence** · **đọc kết luận 2 kiểm toán viên** · **liếc `specs/` nếu có đổi**. Không cần đọc từng dòng code — evidence tồn tại để bạn không phải làm vậy. | ~5 phút/PR |
| 3. Hardware | Test [H] chỉ người tick: `./mo hw-test ID=OTA-04 TESTER=<tên> HW="Jetson Orin"` — trả lời checklist, biên bản tự sinh vào `docs/evidence/hw/`. | theo catalog |

Giữa các gate, agent tự chạy: `/task <ID>` → plan → contract → test đỏ → code →
`./mo verify` → `/audit` → commit → `/pr`.

## Lệnh hằng ngày

Trong Claude Code: **`/dev`** trước tiên — nó chẩn đoán và chỉ bước tiếp theo.
Còn lại: `/feature` · `/tech-plan` · `/spec-analyze` · `/task <ID>` · `/audit` · `/pr` · `/handoff`

Trong terminal:

| Lệnh | Làm gì |
|---|---|
| `./mo verify` | check-merge + gen + lint + gofmt + vet + `go test -race` + cập nhật tracker |
| `./mo status` | render tracker + sinh `docs/PROGRESS.md` |
| `./mo trace` | ID mồ côi, skill lệch ADR, milestone lệch catalog |
| `./mo lint` | golangci-lint (gồm `depguard` ép constitution #7) |
| `./mo next` | **đang ở bước nào, làm gì tiếp** (skill `/dev` chạy lệnh này) |
| `./mo digest` | dựng phần thân PR |
| `./mo steer list --open` | mục nhật ký `.steering/` còn treo |
| `./mo doctor` | môi trường thiếu gì |
| `./mo shell` | vào thẳng container |

1 phiên = 1 task = 1 nhánh `feat/<ID>-mô-tả`. Task song song → `git worktree`.

## Nhìn tiến độ ở đâu

- **`docs/PROGRESS.md`** — burndown từng milestone, nhịp tick/tuần, ETA thô, việc tiếp theo.
- **`docs/test-status.md`** — dòng đầu đã ghi "Milestone đang mở … Việc tiếp theo: …".
- **Statusline Claude Code** — `M1 0/16 · next PRV-01 · tổng 0/49 · <nhánh>`.

Cả ba đọc từ `docs/test-status.json`. Không sửa tay file nào trong số đó — hook chặn,
và CI sẽ bắt được nếu ai đó lách hook.

## Truy vết "sao lại thành ra thế này"

`git log` chỉ trả lời được thứ **sống sót**. Khi câu hỏi là "sao không làm theo cách
kia", "cái này đã từng thử chưa", hay "feature này định làm gì", đọc `.steering/`:

```bash
cat .steering/INDEX.md                    # plan trước, nhật ký sau
cat .steering/plans/m3-ota-v1/plan.md     # định làm thế nào
cat .steering/plans/m3-ota-v1/JOURNAL.md  # đã thử gì và bỏ gì  (máy sinh)

./mo steer plan list              # feature nào đang mở, cover ID nào
./mo steer list --id OTA-07       # mọi thứ từng làm quanh một test ID
./mo steer list --kind risky      # lệnh phá hoại đã chạy, hook ghi tự động
./mo steer list --open            # mục còn treo — nợ chưa trả
```

Plan của feature nằm ở `.steering/plans/`, **không** ở `specs/`. `specs/` chỉ giữ
hợp đồng máy-đọc-được (AsyncAPI + Schema + test vector) — phần open source. Nhờ vậy
mở thư mục plan ra là thấy cả thứ đã định làm lẫn thứ đã thử rồi bỏ, không phải nhảy
hai chỗ.

Hai vòng đời khác nhau: `plans/<x>/` sửa được tới khi `./mo steer plan freeze <x>`;
mục trong `entries/` bất biến ngay khi đóng — sai thì viết mục mới trỏ ngược về mục
cũ. Nhật ký sửa được là nhật ký hết đáng tin. Luật đầy đủ: `.steering/README.md`.

## Đọc evidence khi nghi ngờ một tick ✅

1. Mở `docs/test-status.md` → click link evidence của ID
2. Raw log là output `go test -json` nguyên bản, kèm commit hash trong tên thư mục
3. Tự chạy lại: `./mo shell` rồi `go test -run Test<ID bỏ gạch> ./...`
4. Muốn xem agent đã đi đường nào đến tick đó: transcript JSONL của phiên

## Khi commit bị chặn

- `Commit bị từ chối: thiếu dòng Implements:` → thêm `Implements: OTA-07`, hoặc
  `Implements: none` nếu commit thật sự không gắn test ID nào. Không có đường vượt im lặng.
- `BLOCKED: docs/test-status.*` → đúng thiết kế. Chạy `./mo verify` thay vì sửa tay.
- `depguard: import ... is not allowed` → thiết kế đang sai chiều phụ thuộc, không phải
  lint khó tính. Cần dùng chung thì đưa vào `protocol/`.

## Khi nào viết ADR / sửa skill

- Chọn giữa ≥2 phương án có hệ quả dài hạn → ADR mới (template: `docs/adr/TEMPLATE.md`)
- Bug lặp ≥2 lần → thêm 1 dòng vào skill liên quan TRƯỚC khi quên
- Cuối mỗi milestone: 30 phút đọc lại skill + rule, xoá dòng lỗi thời
