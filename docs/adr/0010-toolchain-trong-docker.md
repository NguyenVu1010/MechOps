# ADR-0010: Toolchain dev nằm trong Docker, `./mo` là entrypoint duy nhất
- Status: accepted
- Date: 2026-08-23
- Covers: []

## Context

`CLAUDE.md` gọi `make verify` là "lệnh DUY NHẤT để cập nhật tracker", và constitution #2
nói "tick chỉ do máy". Cả hai giả định máy dev có Go, Python, make.

Kiểm tra thực tế trên máy founder (Windows 11, 2026-08-23): **không có `go`, `python`,
`make`, `gh`** — chỉ có Docker Desktop và Git Bash. `python` trong PATH là app-execution
alias của Microsoft Store, chạy vào là hiện quảng cáo cài đặt.

Hệ quả không phải "hơi bất tiện" mà là hỏng thầm lặng:

- `make verify` không chạy được → không tick được gì → constitution #2 trở thành khẩu hiệu.
- Hook `PreToolUse` trong `.claude/settings.json` viết dạng `python3 -c "..." || { echo BLOCKED; exit 2; }`.
  Vì `python3` không tồn tại, vế trái **luôn** fail, nên nhánh `exit 2` **luôn** chạy —
  hook chặn **mọi** thao tác Edit/Write trong repo, không riêng `test-status`.
  Nó trông như một hook đang bảo vệ repo, thực chất là một hook hỏng.
- Nếu người này cài Go 1.23 còn CI dùng 1.22, "xanh trên máy tôi" mất nghĩa.

Chọn giữa: tài liệu hoá cách cài toolchain, hay làm cho toolchain không cần cài.

## Options đã cân nhắc

1. **Cài native + `docs/SETUP-WINDOWS.md`.** Nhanh nhất hôm nay. Nhưng mỗi máy mới là
   một lần lệch phiên bản, và không có gì ngăn máy A khác máy B khác CI. Người thứ hai
   vào dự án lại trả lại chi phí này từ đầu.
2. **CI là nơi duy nhất verify.** Máy dev chỉ soạn code. Vòng phản hồi giãn từ vài giây
   lên vài phút, và TDD (constitution #1) chỉ sống được khi vòng đỏ→xanh ngắn. Bỏ.
3. **Toolchain trong Docker, gọi qua một script wrapper.** ← chọn

## Decision

Toolchain dev đóng gói trong `docker/dev.Dockerfile` (Go 1.22 + Python 3.11 + make +
golangci-lint pinned), chạy như service `dev` của `docker-compose.dev.yml`. Mọi lệnh
đi qua `./mo` ở root.

`Makefile` vẫn định nghĩa *việc*; `mo` chỉ quyết định việc đó chạy *ở đâu*. Không có
hai bản mô tả công việc song song để lệch nhau.

Ba chi tiết quyết định script này dùng được hay không:

1. **Container ấm.** `docker compose run --rm` tốn 1–2s mỗi lần — quá chậm cho hook chạy
   mỗi lượt. Service chạy nền với `sleep infinity`, `mo` dùng `exec` (~200ms), chỉ fallback
   sang `run --rm` khi container chưa lên.
2. **`./mo --native`** chạy thẳng không qua Docker. CI dùng đường này (runner đã có
   toolchain), nên CI và local chạy **cùng một Makefile**.
3. **`.gitattributes` ép `eol=lf`.** `core.autocrlf=true` trên Windows sinh CRLF ở
   working tree; `gofmt` trong container Linux coi mọi file `.go` là chưa format nên
   `verify` không bao giờ xanh. Nguy hiểm hơn: script bash có CRLF lỗi `\r: command not found`
   trong container. Đây là hệ quả trực tiếp của quyết định này, phải xử cùng chỗ.

Hook Claude Code viết lại thành script bash thuần trong `.claude/hooks/`, **không phụ thuộc
python/jq** — hook bảo vệ repo thì bản thân nó không được phụ thuộc thứ có thể vắng mặt.

## Consequences

+ Máy trắng chỉ cần Docker + git là làm việc được. Local và CI dùng chung Makefile, chung phiên bản Go.
+ Nâng Go/golangci-lint là sửa một dòng trong Dockerfile, cả team đổi cùng lúc.
+ Hook hết hỏng thầm lặng: `./mo doctor` in ra chính xác thiếu gì.
− Mỗi lệnh cộng ~200ms (container ấm) hoặc ~1.5s (container nguội).
− Lần dựng đầu tốn vài phút tải image; cần Docker Desktop chạy nền.
− `./mo` là bề mặt mới phải bảo trì. Đổi lại nó xoá được `docs/SETUP-*.md` cho từng OS.
