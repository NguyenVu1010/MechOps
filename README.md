# MechOps

Hạ tầng vận hành robot, PLC và Industrial IoT.
Go · MQTT/EMQX · PostgreSQL+TimescaleDB · Next.js · Docker Compose.

## Vừa clone về?

```bash
./mo doctor    # máy chỉ cần Docker Desktop — Go/Python/lint nằm trong container
./mo up        # dựng container dev (lần đầu vài phút)
./mo status    # tracker + PROGRESS.md + plan đang treo
```

Rồi mở **`docs/product/html/dev-flow.html`** bằng trình duyệt — giải phẫu toàn bộ bộ
máy từ một test ID tới CI, kèm 5 lưu đồ. Đọc một lượt khoảng 25 phút, và sau đó không
phải đoán gì nữa. (GitHub không render HTML trong repo, nên phải mở file sau khi clone.)

Không biết làm gì tiếp thì gõ **`/dev`** trong Claude Code — nó chẩn đoán đang ở bước
nào rồi gọi đúng skill. Không cần thuộc quy trình.

## Đọc gì, khi nào

| File | Trả lời câu hỏi | Cho ai |
|---|---|---|
| `docs/product/html/dev-flow.html` | Bộ máy này hoạt động thế nào? | dev mới, ngày đầu |
| `docs/DEVELOPMENT.md` | Hằng ngày gõ gì? Bị chặn thì làm sao? | dev, tra cứu |
| `CLAUDE.md` | Luật làm việc và vòng lặp chuẩn | agent AI (tự nạp) + dev |
| `constitution.md` | 9 nguyên tắc không thương lượng | tất cả |
| `docs/test-status.md` | Việc tiếp theo là gì? | tất cả, mỗi ngày |
| `docs/adr/` | Vì sao lại làm thế này? | khi định làm khác đi |
| `.steering/INDEX.md` | Đã thử gì rồi bỏ? | khi thấy một hướng "hiển nhiên" |
| `specs/` | Hợp đồng MQTT + Probe API | khi chạm giao thức |

## Ba điều biết trước thì đỡ mất thời gian

1. **Mọi lệnh đi qua `./mo`**, không phải `make` — toolchain nằm trong Docker (ADR-0010).
   Gõ `make` thẳng sẽ báo "command not found". PowerShell dùng `.\mo.ps1`.

2. **Không sửa tay** `docs/test-status.*`, `docs/PROGRESS.md`, `.steering/INDEX.md`.
   Máy ghi, hook chặn, CI kiểm lại. Bị chặn ở đó là chủ đích, không phải lỗi cần lách —
   thông báo luôn kèm lệnh đúng phải dùng.

3. **Commit phải có dòng `Implements: <test-ID>`**, hoặc `Implements: none` cho commit
   không gắn test nào. Git hook tự bật khi mở phiên Claude Code; làm việc ngoài Claude
   Code thì chạy `./mo hooks-install` một lần.

## Trạng thái và truy vết

- `docs/test-status.md` — tick tự động kèm evidence, dòng đầu nói luôn việc tiếp theo
- `docs/PROGRESS.md` — burndown từng milestone, nhịp độ
- `.steering/` — nhật ký quyết định, gồm cả hướng đã thử rồi bỏ
- `./mo next` — đang ở bước nào, làm gì tiếp

## Mã nguồn mở

`specs/` (AsyncAPI 3 + JSON Schema), `agent/`, `probe/`, `protocol/`.
