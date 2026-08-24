#!/usr/bin/env bash
# PreToolUse(Edit|Write|MultiEdit): chặn ghi tay vào docs/test-status.* — constitution #2.
# Chỉ soi tool_input.file_path, KHÔNG soi nội dung (tránh chặn nhầm file chỉ nhắc tới tên đó).
set -u
. "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/_lib.sh"

input=$(cat)
fp=$(printf '%s' "$input" | json_str file_path)

case "$fp" in
  *test-status.md|*test-status.json)
    cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"docs/test-status.* chỉ do tools/testtrack/track.py ghi (constitution #2 — tick chỉ do máy). Muốn cập nhật: ./mo verify"}}
JSON
    ;;
esac
exit 0
