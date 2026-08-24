#!/usr/bin/env bash
# PostToolUse(Edit|Write|MultiEdit): ghi nhận file .go vừa sửa để hook Stop gofmt một lượt.
# Không gofmt tại đây: mỗi lần sẽ tốn một lần vào container.
set -u
. "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/_lib.sh"

fp=$(cat | json_str file_path)
case "$fp" in
  *.go)
    mkdir -p "$(proj)/.claude/cache"
    printf '%s\n' "$fp" >> "$(proj)/.claude/cache/dirty-go.txt"
    ;;
esac
exit 0
