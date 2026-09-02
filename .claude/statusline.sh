#!/usr/bin/env bash
# Statusline: đọc cache, KHÔNG spawn Docker (chạy rất thường xuyên).
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "-")
if [ -s .claude/cache/progress.txt ]; then
  printf 'MechOps · %s · %s' "$(head -1 .claude/cache/progress.txt)" "$branch"
else
  printf 'MechOps · tiến độ chưa có cache (chạy ./mo status) · %s' "$branch"
fi
