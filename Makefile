.PHONY: verify lint gen test-integration hw-test status progress trace fmt-dirty

# Makefile định nghĩa VIỆC. `./mo` quyết định việc đó chạy ở đâu (container hay host).
# Gọi thẳng `make` chỉ đúng khi máy đã có go+python3+make — trên máy dev Windows thì không (ADR 0010).

# Repo multi-module (go.work) — go test ./... ở root không quét module con.
# Workspace mode (Go >= 1.18) resolve pattern theo thư mục nên phải liệt kê tường minh.
GO_PKGS := ./agent/... ./protocol/... ./server/...

# Pipe go test | track.py cần pipefail — /bin/sh mặc định nuốt exit code vế trái.
SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -ec

gen: ## sinh protocol/types.gen.go từ specs/schemas + validate testvectors
	@echo "TODO(M0): go-jsonschema specs/schemas/*.schema.json -> protocol/types.gen.go"
	python3 tools/gen/validate_vectors.py

lint: ## golangci-lint — cưỡng chế constitution #7 (depguard) và quy ước slog (forbidigo)
	@command -v golangci-lint >/dev/null || { echo "LỖI: thiếu golangci-lint. Chạy qua ./mo lint." >&2; exit 1; }
	@# Cùng lý do với GO_PKGS ở trên: `golangci-lint run` không có tham số sẽ dùng
	@# ./... và vỡ trong workspace mode. Phải liệt kê module tường minh.
	golangci-lint run $(GO_PKGS)

verify: gen lint
	@command -v go >/dev/null || { echo "LỖI: không có Go trong PATH — evidence sẽ rỗng. Chạy qua ./mo verify." >&2; exit 1; }
	@fmt_files=$$(gofmt -l .); if [ -n "$$fmt_files" ]; then echo "gofmt chưa chuẩn:" >&2; echo "$$fmt_files" >&2; exit 1; fi
	go vet $(GO_PKGS)
	go test -race -json $(GO_PKGS) | python3 tools/testtrack/track.py --go-json -

test-integration:
	@command -v go >/dev/null || { echo "LỖI: không có Go trong PATH." >&2; exit 1; }
	go test -race -json -tags=integration $(GO_PKGS) | python3 tools/testtrack/track.py --go-json -

hw-test:
	python3 tools/testtrack/hwtest.py $(ID) --tester $(TESTER) --hardware "$(HW)"

status:
	python3 tools/testtrack/track.py --render && head -6 docs/test-status.md | tail -3

progress: ## sinh docs/PROGRESS.md (burndown + velocity + việc tiếp theo)
	python3 tools/report/progress.py

trace: ## test ID mồ côi + skill<->ADR sync + milestone khớp catalog
	python3 tools/trace/trace.py

fmt-dirty: ## gofmt sau khi agent sửa file .go (hook Stop gọi)
	@# Format cả repo thay vì từng file: đường dẫn trong cache là path của HOST,
	@# không resolve được bên trong container. Repo nhỏ nên gofmt toàn bộ vẫn tức thì.
	gofmt -w .
