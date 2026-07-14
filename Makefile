.PHONY: verify test-integration hw-test status gen trace

# Repo multi-module (go.work) — go test ./... ở root không quét module con.
# Workspace mode (Go >= 1.18) resolve pattern theo thư mục nên phải liệt kê tường minh.
GO_PKGS := ./agent/... ./protocol/... ./server/...

# Pipe go test | track.py cần pipefail — /bin/sh mặc định nuốt exit code vế trái.
SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -ec

gen: ## sinh protocol/types.gen.go từ specs/schemas + validate testvectors
	@echo "TODO(M0): go-jsonschema specs/schemas/*.schema.json -> protocol/types.gen.go"
	python3 tools/gen/validate_vectors.py

verify: gen
	@command -v go >/dev/null || { echo "LỖI: không có Go trong PATH — evidence sẽ rỗng. Cài Go rồi chạy lại." >&2; exit 1; }
	@fmt_files=$$(gofmt -l .); if [ -n "$$fmt_files" ]; then echo "gofmt chưa chuẩn:" >&2; echo "$$fmt_files" >&2; exit 1; fi
	go vet $(GO_PKGS)
	go test -json $(GO_PKGS) | python3 tools/testtrack/track.py --go-json -

test-integration:
	@command -v go >/dev/null || { echo "LỖI: không có Go trong PATH." >&2; exit 1; }
	go test -json -tags=integration $(GO_PKGS) | python3 tools/testtrack/track.py --go-json -

hw-test:
	python3 tools/testtrack/hwtest.py $(ID) --tester $(TESTER) --hardware "$(HW)"

status:
	python3 tools/testtrack/track.py --render && head -5 docs/test-status.md | tail -2

trace: ## test ID mồ côi + skill<->ADR sync
	python3 tools/trace/trace.py
