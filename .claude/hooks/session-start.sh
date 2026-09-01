#!/usr/bin/env bash
# SessionStart: dựng container dev ở nền + nạp trạng thái tiến độ vào context.
#
# Đọc thẳng docs/test-status.md bằng bash (không cần python/docker) — context phải
# có mặt kể cả khi Docker Desktop chưa khởi động xong.
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# Git hook KHÔNG đi theo `git clone`: mặc định git nhìn .git/hooks/, mà .git/ không
# versioned được — đó là chốt chặn cố ý của git (nếu clone mang theo mã tự chạy thì
# clone một repo lạ = cho nó chạy code trên máy mình). Nên mỗi clone phải bật công
# tắc một lần, và không có gì trong repo tự làm được việc đó.
#
# Bật LUÔN thay vì chỉ cảnh báo: đúng người cần cảnh báo nhất — dev mới chưa đọc
# CLAUDE.md — là người sẽ lướt qua nó. Hai lệnh này chỉ ghi vài dòng vào .git/config
# của chính clone đang mở: không cài gói, không tải gì, không chạm ngoài thư mục repo.
hookwarn=""
if [ "$(git config core.hooksPath 2>/dev/null)" != ".githooks" ]; then
  git config core.hooksPath .githooks 2>/dev/null
  git config merge.ours.driver true 2>/dev/null
  hookwarn="
- ⚠️ Clone này CHƯA cài git hook — vừa tự bật (core.hooksPath + merge driver ours).
  Trước đó: commit-msg không kiểm \`Implements:\`, và merge trộn cả file máy sinh."
  printf '\033[33mMechOps: git hook chưa cài trong clone này — đã tự bật.\033[0m\n' >&2
elif [ "$(git config merge.ours.driver 2>/dev/null)" != "true" ]; then
  git config merge.ours.driver true 2>/dev/null
  hookwarn="
- ⚠️ Thiếu merge driver \`ours\` — vừa đặt. Không có nó git BỎ QUA
  .gitattributes và trộn file máy sinh như văn bản thường."
fi

# Làm ấm container ở nền; phiên không phải chờ.
( bash ./mo up >/dev/null 2>&1 & ) 2>/dev/null

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
tracker=$(grep -m1 '^> Cập nhật' docs/test-status.md 2>/dev/null | sed 's/^> //')
mstone=$(grep -m1 'Milestone đang mở' docs/test-status.md 2>/dev/null | sed 's/^> //; s/\*\*//g')
# grep -c in ra "0" rồi vẫn exit 1 khi không khớp — dùng `|| echo 0` sẽ ra hai dòng.
fails=$(grep -c '^| ❌' docs/test-status.md 2>/dev/null | head -1)
fails=${fails:-0}
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

# Plan đang treo: đọc CACHE, không gọi python — context phải có mặt kể cả khi
# Docker chưa lên. Cache do `./mo status` / post-merge / post-checkout ghi.
triage=""
if [ -s .claude/cache/triage.txt ]; then
  triage=$(printf '\n- ⚠️ CẦN NGƯỜI QUYẾT (%s mục, có thể hơi cũ — `./mo steer plan triage` để chắc):\n%s' \
    "$(wc -l < .claude/cache/triage.txt | tr -d ' ')" \
    "$(sed 's/^/  · /' .claude/cache/triage.txt)")
fi
# Làm mới cache ở nền cho phiên sau; phiên này không chờ.
( bash ./mo steer plan triage --cache .claude/cache/triage.txt --quiet >/dev/null 2>&1 & ) 2>/dev/null

ctx="Trạng thái MechOps đầu phiên (hook SessionStart nạp, không phải người gõ):${hookwarn}
- Nhánh: ${branch} · ${dirty} file chưa commit${triage}
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
