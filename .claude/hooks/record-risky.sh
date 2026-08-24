#!/usr/bin/env bash
# PreToolUse(Bash): ghi nhật ký .steering/ khi agent định chạy lệnh có sức phá hoại.
#
# KHÔNG chặn — chỉ ghi. Chặn thì agent sẽ tìm đường vòng; ghi thì hành động vẫn
# xảy ra nhưng để lại dấu vết. Đây là loại hành động đáng truy vết nhất và cũng là
# loại agent ít tự nguyện khai nhất, nên nó không được để cho tự thuật.
#
# Chạy trên MỌI lệnh Bash nên phải rẻ: khớp mẫu bằng bash thuần, chỉ khi trúng
# mới vào container.
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
. "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/_lib.sh"

cmd=$(cat | json_str command)
[ -z "$cmd" ] && exit 0

# Ghi ý định, không ghi kết quả — PostToolUse chỉ chạy khi lệnh THÀNH CÔNG, mà
# lệnh phá hoại thất bại cũng đáng biết.
# Khớp theo CỜ nguy hiểm, không theo cụm hai từ: `git commit --amend` và
# `git commit -q --amend` là cùng một hành động, nhưng mẫu "commit --amend"
# chỉ bắt được cái đầu. Chèn một cờ vào giữa là lách — đã dính đúng lỗi này.
risky=0
for pat in -- --amend --no-verify --hard --force --force-with-lease \
           "rm -rf" "stash drop" "stash clear" "git clean" "git restore" \
           "git rebase" "down -v" "volume rm" "DROP TABLE" "TRUNCATE"; do
  [ "$pat" = "--" ] && continue
  case "$cmd" in *"$pat"*) risky=1; break ;; esac
done
# `--force` cũng có trong `docker compose up --force-recreate` — vô hại, bỏ qua
# nếu đó là lần khớp duy nhất.
case "$cmd" in
  *--force-recreate*)
    case "$cmd" in
      *--amend*|*--no-verify*|*--hard*|*"rm -rf"*|*"volume rm"*|*"down -v"*) ;;
      *) risky=0 ;;
    esac ;;
esac
[ "$risky" = 1 ] || exit 0

# Tiêu đề gọn. Lệnh nhiều dòng: trong JSON xuống dòng là HAI ký tự `\` + `n`,
# nên phải thay chuỗi đó chứ `tr '\n'` không bắt được. Lệnh đầy đủ vẫn nằm ở
# mục "## Lệnh" của bản tin, đây chỉ là nhãn để đọc lướt trong INDEX.
title=$(printf '%s' "$cmd" | sed 's/\\n/ ; /g' | tr -s ' ' \
        | cut -c1-70 | tr -d '"' | sed 's/:/ /g')

sid=$(bash ./mo steer new --kind risky --area infra --source hook \
  --title "$title" --command "$cmd" --outcome open \
  --context "Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại." \
  2>/dev/null | awk '{print $1}') || true
[ -z "${sid:-}" ] && sid="mục risky vừa mở"

# Nhắc agent đóng mục — nhắc, không ép.
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Lệnh này có sức phá hoại nên đã được ghi vào .steering/ (%s, outcome: open). Sau khi chạy xong, đóng bằng: ./mo steer close %s --outcome kept|reverted --why \\"<chuyện gì đã xảy ra>\\" --promoted \\"<test ID / ADR / dòng skill / none>\\""}}\n' \
  "$sid" "$sid"
exit 0
