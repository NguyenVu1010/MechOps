#!/usr/bin/env bash
# SessionStart: dựng container dev ở nền + nạp trạng thái tiến độ vào context.
#
# Đọc thẳng docs/test-status.md bằng bash (không cần python/docker) — context phải
# có mặt kể cả khi Docker Desktop chưa khởi động xong.
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# Làm ấm container ở nền; phiên không phải chờ.
( bash ./mo up >/dev/null 2>&1 & ) 2>/dev/null

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
tracker=$(grep -m1 '^> Cập nhật' docs/test-status.md 2>/dev/null | sed 's/^> //')
mstone=$(grep -m1 'Milestone đang mở' docs/test-status.md 2>/dev/null | sed 's/^> //; s/\*\*//g')
# grep -c in ra "0" rồi vẫn exit 1 khi không khớp — dùng `|| echo 0` sẽ ra hai dòng.
fails=$(grep -c '^| ❌' docs/test-status.md 2>/dev/null | head -1)
fails=${fails:-0}
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

ctx="Trạng thái MechOps đầu phiên (hook SessionStart nạp, không phải người gõ):
- Nhánh: ${branch} · ${dirty} file chưa commit
- Tracker: ${tracker:-chưa có}
- ${mstone:-Milestone: chưa xác định}
- Test đang đỏ: ${fails}
- Lệnh chạy mọi thứ là ./mo (KHÔNG phải make — toolchain nằm trong Docker, ADR 0010).
Vòng lặp chuẩn và luật cấm: CLAUDE.md. Nguyên tắc bất biến: constitution.md."

# Escape JSON bằng parameter expansion của bash — không phụ thuộc jq/python,
# và không vỡ khi nội dung có dấu / như sed.
esc=${ctx//\\/\\\\}
esc=${esc//\"/\\\"}
esc=${esc//$'\n'/\\n}

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
exit 0
