#!/usr/bin/env bash
# mo — entrypoint DUY NHẤT của MechOps. Thay cho `make` trên máy không có toolchain.
#
#   ./mo verify              chạy trong container dev (mặc định)
#   ./mo --native verify     chạy thẳng trên host (CI dùng cái này)
#
# Vì sao không gọi make trực tiếp: máy dev Windows không có go/python/make (ADR 0010).
# Makefile vẫn là nơi định nghĩa việc — mo chỉ quyết định việc đó chạy Ở ĐÂU.
set -euo pipefail

cd "$(dirname "$0")"
COMPOSE=(docker compose -f docker-compose.dev.yml)
SVC=dev
NATIVE=0

if [ "${1:-}" = "--native" ]; then NATIVE=1; shift; fi

die() { printf '\033[31mLỖI:\033[0m %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m%s\033[0m\n' "$*" >&2; }

have() { command -v "$1" >/dev/null 2>&1; }

container_up() {
  [ -n "$("${COMPOSE[@]}" ps -q "$SVC" 2>/dev/null)" ] || return 1
  [ "$("${COMPOSE[@]}" ps --format '{{.State}}' "$SVC" 2>/dev/null | head -1)" = "running" ]
}

# Chạy một lệnh trong môi trường có toolchain.
run() {
  if [ "$NATIVE" = 1 ]; then
    "$@"
    return
  fi
  have docker || die "không có docker. ./mo cần Docker Desktop, hoặc dùng ./mo --native nếu máy đã có Go+Python+make."
  if container_up; then
    "${COMPOSE[@]}" exec -T "$SVC" "$@"
  else
    info "container dev chưa chạy — dựng tạm (chậm hơn). Chạy './mo up' để giữ ấm."
    "${COMPOSE[@]}" run --rm -T "$SVC" "$@"
  fi
}

mk() { run make "$@"; }

cmd="${1:-help}"; shift || true

case "$cmd" in
  up)
    have docker || die "không có docker."
    "${COMPOSE[@]}" up -d --build "$SVC"
    ;;
  down)
    "${COMPOSE[@]}" down
    ;;
  shell)
    "${COMPOSE[@]}" exec "$SVC" bash
    ;;

  # --- việc thật, uỷ quyền cho Makefile ---
  gen|lint|verify|test-integration|trace|fmt-dirty)
    mk "$cmd"
    ;;
  status)
    mk status
    run python3 tools/report/progress.py --cache .claude/cache/progress.txt
    # tasks.md + STATUS.md của plan suy từ tracker — sync ở đây để không bao giờ cũ
    run python3 tools/steering/steer.py plan sync
    run python3 tools/steering/steer.py plan triage --cache .claude/cache/triage.txt
    ;;
  progress)
    if [ "${1:-}" = "--cache-only" ]; then
      run python3 tools/report/progress.py --cache .claude/cache/progress.txt --quiet
    else
      run python3 tools/report/progress.py --cache .claude/cache/progress.txt
    fi
    ;;
  hw-test)
    mk hw-test "$@"
    ;;
  digest)
    run python3 tools/report/pr_digest.py "$@"
    ;;
  check-commit)
    run python3 tools/checks/commit_msg.py "$@"
    ;;
  check-contract)
    run python3 tools/checks/contract_touch.py "$@"
    ;;
  next)
    run python3 tools/report/next.py
    ;;
  steer)
    run python3 tools/steering/steer.py "$@"
    ;;

  hooks-install)
    git config core.hooksPath .githooks
    chmod +x .githooks/* 2>/dev/null || true
    # `merge=ours` trong .gitattributes chỉ có tác dụng khi driver được khai báo.
    # Thiếu dòng này thì git im lặng bỏ qua thuộc tính và trộn file máy sinh như
    # file thường — đúng thứ nó sinh ra để tránh.
    git config merge.ours.driver true
    info "git hooks đã trỏ vào .githooks/ — commit-msg kiểm 'Implements:',"
    info "post-merge sinh lại .steering/, post-checkout báo plan đang treo."
    ;;

  doctor)
    ok=0
    printf 'docker CLI        : '; if have docker; then docker --version; else printf 'THIẾU\n'; ok=1; fi
    # `have docker` chỉ nói CLI có trong PATH. Daemon chết thì mọi lệnh sau đều
    # hỏng, mà doctor lại đi khuyên "chạy ./mo up" — lời khuyên tự tin và sai hướng.
    printf 'docker daemon     : '
    if docker version --format '{{.Server.Version}}' >/dev/null 2>&1; then
      printf 'trả lời (server %s)\n' "$(docker version --format '{{.Server.Version}}' 2>/dev/null)"
      printf 'container dev     : '; if container_up; then printf 'đang chạy\n'; else printf 'chưa chạy (./mo up)\n'; fi
    else
      printf 'KHÔNG TRẢ LỜI — mở Docker Desktop rồi đợi nó xanh.\n'
      printf '                    Mọi lệnh ./mo khác sẽ hỏng cho tới lúc đó.\n'
      ok=1
    fi
    printf 'git hooksPath     : '; git config core.hooksPath 2>/dev/null || { printf 'chưa cài (./mo hooks-install)\n'; ok=1; }
    if container_up; then
      printf 'go trong container : '; "${COMPOSE[@]}" exec -T "$SVC" go version 2>/dev/null || printf 'THIẾU\n'
      printf 'python3           : '; "${COMPOSE[@]}" exec -T "$SVC" python3 --version 2>/dev/null || printf 'THIẾU\n'
      printf 'golangci-lint     : '; "${COMPOSE[@]}" exec -T "$SVC" golangci-lint --version 2>/dev/null || printf 'THIẾU\n'
    fi
    printf '\nhost native (chỉ CI cần, máy dev không cần): '
    # Không dùng `command -v`: trên Windows, `python3` là app-execution alias của
    # Microsoft Store — có trong PATH nhưng chạy vào là hiện quảng cáo cài đặt.
    # Phải gọi thật mới biết nó có tồn tại hay không.
    for t in go python3 make; do
      if "$t" --version >/dev/null 2>&1; then printf '%s ✓ ' "$t"; else printf '%s ✗ ' "$t"; fi
    done; echo
    exit $ok
    ;;

  help|-h|--help)
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    echo
    echo "Lệnh: up down shell doctor hooks-install"
    echo "      gen lint verify test-integration trace"
    echo "      status progress digest check-commit steer hw-test fmt-dirty"
    echo
    echo "Steering: ./mo steer plan triage        plan/quyết định đang treo"
    echo "          ./mo steer plan keep <x>      trả lời: vẫn làm tiếp"
    echo "          ./mo steer plan abandon <x>   bỏ, KHÔNG xoá thư mục"
    echo "          ./mo steer renumber <mốc>     gỡ trùng id sau merge"
    ;;
  *)
    die "lệnh không biết: $cmd (thử ./mo help)"
    ;;
esac
