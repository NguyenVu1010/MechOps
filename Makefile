.PHONY: verify lint gen test-integration hw-test status progress trace fmt-dirty check-merge

# Makefile định nghĩa VIỆC. `./mo` quyết định việc đó chạy ở đâu (container hay host).
# Gọi thẳng `make` chỉ đúng khi máy đã có go+python3+make — trên máy dev Windows thì không (ADR 0010).

# Repo multi-module (go.work) — go test ./... ở root không quét module con.
# Workspace mode (Go >= 1.18) resolve pattern theo thư mục nên phải liệt kê tường minh.
# Repo chính (umbrella, ADR-0019) không có mã sản phẩm: mã nằm trong repos/<đội>.
# Các bước Go chạy ở repo của từng đội; ở đây chỉ còn kiểm sổ sách và E2E (sau này).
GO_PKGS :=

# Pipe go test | track.py cần pipefail — /bin/sh mặc định nuốt exit code vế trái.
SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -ec

gen: ## hợp đồng nằm ở repos/agent/specs, validate ở repo đó
	@true

lint: ## không có mã Go ở repo chính
	@true

check-merge: ## conflict marker lọt vào commit = file máy sinh vỡ im lặng
	@# Chỉ bắt `<<<<<<< ` và `>>>>>>> ` — chúng LUÔN có nhãn theo sau nên dấu cách là
	@# phần của mẫu. Cố tình KHÔNG bắt `=======` đứng một mình: đó cũng là cách gạch
	@# chân tiêu đề H1 của markdown, bắt nó là báo oan ngay trên docs/ của repo này.
	@if git grep -nE '^(<{7}|>{7}) ' -- . ; then \
		echo "" >&2; \
		echo "LỖI: còn conflict marker trong file đã tracked (liệt kê ở trên)." >&2; \
		echo "     Giải quyết merge cho xong rồi commit lại, đừng commit nửa vời." >&2; \
		echo "     Trong file máy sinh, marker làm track.py chết với JSONDecodeError" >&2; \
		echo "     trên đúng file mà người ta bị CẤM sửa tay." >&2; \
		exit 1; fi

verify: check-merge gen lint
	@echo "verify: repo chính không có test đơn vị; E2E nằm ở e2e/ (chưa có test)"

test-integration:
	@echo "E2E chưa có test — xem e2e/README.md"

hw-test:
	python3 tools/testtrack/hwtest.py $(ID) --tester $(TESTER) --hardware "$(HW)"

status:
	python3 tools/testtrack/track.py --render && head -6 docs/test-status.md | tail -3

progress: ## sinh docs/PROGRESS.md (burndown + velocity + việc tiếp theo)
	python3 tools/report/progress.py

trace: ## test ID mồ côi + skill<->ADR sync + milestone khớp catalog
	python3 tools/trace/trace.py

fmt-dirty:
	@true
