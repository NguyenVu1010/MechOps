#!/usr/bin/env bash
# Stop: gofmt một lượt cho các file .go đã chạm + làm mới cache tiến độ cho statusline.
# Không bao giờ exit 2 (exit 2 ở Stop = chặn Claude kết thúc lượt).
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
msg=""

if [ -s .claude/cache/dirty-go.txt ]; then
  if bash ./mo fmt-dirty >/dev/null 2>&1; then
    : > .claude/cache/dirty-go.txt
  else
    msg="Không gofmt được file .go vừa sửa — môi trường dev chưa sẵn sàng. Chạy: ./mo doctor"
  fi
fi

bash ./mo progress --cache-only >/dev/null 2>&1 || true

[ -n "$msg" ] && printf '{"systemMessage":"%s"}\n' "$msg"
exit 0
