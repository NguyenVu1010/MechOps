#!/usr/bin/env bash
# Ma trận ca cho record-risky.sh.   Chạy:  bash .claude/hooks/record-risky-cases.sh
#
# Hook này đã sai BA lần trong một phiên, cả ba đều cùng một họ: khớp mẫu trên một
# chuỗi lệnh thì luôn có cách viết lách được, hoặc cách viết bị bắt oan.
#   1. mẫu "commit --amend" bị lách bởi `git commit -q --amend`
#   2. `json_str` cắt ở dấu " đầu tiên -> cờ sau tham số có ngoặc kép bị bỏ sót
#   3. cụm nguy hiểm nằm trong văn xuôi (heredoc, rồi --why) -> báo oan
# Nên nó cần một ma trận chạy được, không phải một dòng "đã kiểm bằng mắt".
#
# Cách kiểm: cắt hook ở đoạn ghi (`sid=`), thay bằng `echo RISKY`, nên không mục
# nhật ký nào bị tạo ra.
cd "$(git rev-parse --show-toplevel)" || exit 1
export CLAUDE_PROJECT_DIR="$PWD"
H=.claude/hooks/record-risky.sh
T=$(mktemp)
trap 'rm -f "$T"' EXIT
sed '/^sid=/,$d' "$H" > "$T"
printf 'echo RISKY\n' >> "$T"

fail=0
check() { # $1 = GHI|BỎ mong đợi, $2 = nhãn, $3 = command (đã escape cho JSON)
  local got
  got=$(printf '{"tool_input":{"command":"%s"}}' "$3" | bash "$T" 2>/dev/null)
  [ "$got" = "RISKY" ] && got=GHI || got=BỎ
  if [ "$got" = "$1" ]; then
    printf 'PASS  %-4s %s\n' "$got" "$2"
  else
    printf 'FAIL  được %s, mong %s — %s\n' "$got" "$1" "$2"; fail=1
  fi
}

echo "--- phải GHI: lệnh phá hoại ---"
check GHI "commit --amend"            "git commit --amend"
check GHI "cờ chèn giữa"              "git commit -q --amend -m x"
check GHI "push --force"              "git push --force origin main"
check GHI "reset --hard"              "git reset --hard HEAD~1"
check GHI "xoá đệ quy"                "rm -rf build/"
check GHI "--no-verify"               "git commit -m x --no-verify"
check GHI "compose down -v"           "docker compose down -v"
check GHI "stash drop"                "git stash drop"
check GHI "git clean"                 "git clean -fd"
check GHI "git rebase"                "git rebase origin/main"
check GHI "volume rm"                 "docker volume rm mechops-dev_gocache"

echo "--- phải GHI: cờ nằm SAU tham số có ngoặc kép (lỗ json_str) ---"
check GHI "-m \"x\" rồi --amend"      "git commit -m \\\"fix\\\" --amend"
check GHI "-m \"x\" rồi --no-verify"  "git commit -m \\\"sua xong\\\" --no-verify"
check GHI "psql -c \"DROP TABLE\""    "psql -c \\\"DROP TABLE devices\\\""
check GHI "TRUNCATE trong -c"         "psql -c \\\"TRUNCATE telemetry\\\""

echo "--- phải BỎ QUA: lệnh thường ---"
check BỎ  "up --force-recreate"       "docker compose up -d --force-recreate"
check BỎ  "git status"                "git status --porcelain"
check BỎ  "go test"                   "go test -race ./..."
check BỎ  "mo verify"                 "bash ./mo verify"
check BỎ  "commit -m thường"          "git commit -m \\\"them test TEL-01\\\""

echo "--- phải BỎ QUA: cụm nguy hiểm chỉ là VĂN XUÔI ---"
check BỎ  "heredoc kể chuyện xoá"     "git commit -F - <<MSG\\ncua duy nhat la rm -rf thu muc\\nMSG"
check BỎ  "--why kể chuyện xoá"       "bash ./mo steer close S1 --why \\\"cua duy nhat la rm -rf\\\" --promoted none"
check BỎ  "--title nhắc --amend"      "bash ./mo steer new --kind wrong --title \\\"loi cua git commit --amend\\\""
echo "--- vẫn phải GHI khi có CẢ văn xuôi lẫn lệnh thật ---"
check GHI "heredoc + lệnh thật"       "rm -rf x ; git commit -F - <<MSG\\nx\\nMSG"
check GHI "--why + lệnh thật"         "rm -rf x && bash ./mo steer close S1 --why \\\"da xoa\\\""

[ "$fail" = 0 ] && echo "OK — toàn bộ ca đúng" || echo "CÓ CA SAI"
exit $fail
