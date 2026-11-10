# MechOps

Hạ tầng vận hành robot, PLC và Industrial IoT.

Đây là **repo chính**: quyết định, spec sản phẩm, kế hoạch, lịch sử và E2E. Mã nằm trong
ba repo đội, gắn vào bằng submodule ghim theo tag (ADR-0019):

| Thư mục | Repo | Nội dung |
|---|---|---|
| `repos/platform` | `mechops-platform` | server, dashboard, deploy |
| `repos/agent` | `mechops-agent` | agent, probe, sim, hợp đồng `specs/` (Apache 2.0) |
| `repos/mobile` | `mechops-mobile` | ứng dụng mobile |
| `repos/robotics-backend` | `mechops-robotics-backend` | điều phối giao thông, phân công nhiệm vụ, bản đồ (ADR-0020) |

```bash
git clone --recurse-submodules git@github.com:NguyenVu1010/MechOps.git
```

Kế hoạch tách và trạng thái: `docs/product/09-tach-repo.md`.

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
| `docs/product/html/master-plan.html` | Đang ở đâu, mốc nào tiếp, nghiệm thu bằng gì? | founder, mỗi tuần |
| `docs/DEVELOPMENT.md` | Hằng ngày gõ gì? Bị chặn thì làm sao? | dev, tra cứu |
| `CLAUDE.md` | Luật làm việc và vòng lặp chuẩn | agent AI (tự nạp) + dev |
| `constitution.md` | 9 nguyên tắc không thương lượng | tất cả |
| `docs/test-status.md` | Việc tiếp theo là gì? | tất cả, mỗi ngày |
| `docs/adr/` | Vì sao lại làm thế này? | khi định làm khác đi |
| `.steering/INDEX.md` | Đã thử gì rồi bỏ? | khi thấy một hướng "hiển nhiên" |
| `repos/agent/specs/` | Hợp đồng MQTT + Probe API | khi chạm giao thức |

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

Repo `mechops-agent`: `specs/` (AsyncAPI 3 + JSON Schema), `agent/`, `probe/`, `sim/`.
