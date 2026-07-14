.PHONY: verify test-integration hw-test status gen trace

gen: ## sinh protocol/types.gen.go từ specs/schemas + validate testvectors
	@echo "TODO(M0): go-jsonschema specs/schemas/*.schema.json -> protocol/types.gen.go"
	python3 tools/gen/validate_vectors.py

verify: gen
	gofmt -l . && go vet ./... || true
	go test -json ./... | python3 tools/testtrack/track.py --go-json -

test-integration:
	go test -json -tags=integration ./... | python3 tools/testtrack/track.py --go-json -

hw-test:
	python3 tools/testtrack/hwtest.py $(ID) --tester $(TESTER) --hardware "$(HW)"

status:
	python3 tools/testtrack/track.py --render && head -5 docs/test-status.md | tail -2

trace: ## test ID mồ côi + skill<->ADR sync
	python3 tools/trace/trace.py
