# Hàm chung cho hook. KHÔNG phụ thuộc python/jq — máy dev có thể trắng toolchain.
#
# Trích một field string từ JSON hook input.
#
# Mẫu cũ dùng `"[^"]*"` nên nó dừng ở dấu `"` ĐẦU TIÊN, kể cả dấu đã escape. Với
# `file_path` thì vô hại (đường dẫn không có ngoặc kép), nhưng với `command` thì
# đó là một lỗ thật: `git commit -m "fix" --amend` bị cắt thành `git commit -m `,
# và cờ `--amend` phía sau không bao giờ được thấy. Chốt chặn bỏ sót im lặng còn
# tệ hơn không có chốt chặn.
json_str() { # $1=tên field, stdin=json
  local raw
  raw=$(grep -oE "\"$1\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*\"" | head -1)
  [ -z "$raw" ] && return 0
  raw=${raw#*:}          # bỏ '"field":'  — tên field không chứa dấu ':'
  raw=${raw#*\"}         # bỏ dấu " mở
  raw=${raw%\"}          # bỏ dấu " đóng
  printf '%s' "${raw//\\\"/\"}"
}
proj() { printf '%s' "${CLAUDE_PROJECT_DIR:-.}"; }
