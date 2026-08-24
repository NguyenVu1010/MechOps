#!/usr/bin/env bash
# PreCompact: chụp lại trạng thái làm việc trước khi nén context.
# Trạng thái THẬT nằm ở tracker + git; file này chỉ để người đọc lại khi phiên đứt.
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
mkdir -p .claude/cache
{
  echo "# Handoff — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "## Nhánh"; git rev-parse --abbrev-ref HEAD 2>/dev/null
  echo; echo "## File đang sửa (chưa commit)"; git status --porcelain 2>/dev/null
  echo; echo "## Commit gần nhất"; git log --oneline -5 2>/dev/null
  echo; echo "## Tracker"; grep -m3 '^>' docs/test-status.md 2>/dev/null
} > .claude/cache/handoff.md
exit 0
