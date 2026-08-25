#!/usr/bin/env bash
# PreToolUse(Edit|Write|MultiEdit): chặn ghi tay vào những file MÁY ghi.
#
# Chỉ soi tool_input.file_path, KHÔNG soi nội dung (tránh chặn nhầm một file chỉ
# nhắc tới tên đó — lỗi này đã từng làm hook chặn mọi Edit trong repo).
#
# CLAUDE.md cấm bằng văn bản; đây là chỗ cái cấm đó thành thật. Luật chỉ nằm
# trong văn bản là luật agent sẽ lách khi bí (ADR 0011).
set -u
. "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/_lib.sh"

input=$(cat)
fp=$(printf '%s' "$input" | json_str file_path)
# Windows đưa đường dẫn kèm `\` — chuẩn hoá một lần để mẫu dưới chỉ cần viết `/`.
fp=${fp//\\//}

deny() {
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
  exit 0
}

case "$fp" in
  *test-status.md|*test-status.json)
    deny "docs/test-status.* chỉ do tools/testtrack/track.py ghi (constitution #2 — tick chỉ do máy). Muốn cập nhật: ./mo verify" ;;
  */docs/PROGRESS.md)
    deny "docs/PROGRESS.md do tools/report/progress.py sinh. Muốn cập nhật: ./mo status" ;;
  */.steering/INDEX.md|*/.steering/HISTORY.md)
    deny "file này do tools/steering/steer.py sinh (INDEX = trạng thái, HISTORY = dòng thời gian). Muốn cập nhật: ./mo steer index" ;;
  */.steering/plans/*/STATUS.md|*/.steering/plans/*/JOURNAL.md)
    deny "STATUS.md và JOURNAL.md do steer.py sinh từ tracker + các mục nhật ký. Muốn cập nhật: ./mo steer plan sync" ;;
esac

# Mục nhật ký đã đóng thì bất biến như ADR — sai thì viết mục mới `--supersedes`.
# Đọc `outcome:` trong frontmatter mới biết được, nên không thể quyết bằng tên file.
case "$fp" in
  */.steering/entries/*.md)
    if [ -f "$fp" ] && grep -q '^outcome:' "$fp" && ! grep -q '^outcome: open' "$fp"; then
      deny "mục nhật ký này đã đóng — bất biến như ADR. Sai thì mở mục mới: ./mo steer new --supersedes $(basename "$fp" | sed 's/.*-\(S[0-9]\{4\}\)-.*/\1/')"
    fi ;;
esac
exit 0
