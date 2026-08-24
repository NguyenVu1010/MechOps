# Hàm chung cho hook. KHÔNG phụ thuộc python/jq — máy dev có thể trắng toolchain.
# Trích một field string từ JSON hook input. Dùng cho file_path, prompt... (path không chứa dấu ")
json_str() { # $1=tên field, stdin=json
  grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:[[:space:]]*"//; s/"$//'
}
proj() { printf '%s' "${CLAUDE_PROJECT_DIR:-.}"; }
