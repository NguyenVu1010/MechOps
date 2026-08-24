---
id: S0001
date: 2026-08-23T06:37:15Z
kind: wrong
outcome: reverted
title: "golangci-lint chay duoc voi ./... trong go.work"
area: infra
milestone: M1
test_ids: []
supersedes: []
branch: "main"
commit: 9f5be49
evidence: "docs/evidence/ci/2026-08-22T192826Z-9f5be49"
promoted_to: "none — da co chu thich canh GO_PKGS trong Makefile:8"
source: agent
---

# S0001 · golangci-lint chay duoc voi ./... trong go.work

## Vì sao đụng tới
Them target lint vao Makefile khi dung Lop 1 cua AI flow.

## Tin rằng
Tuong golangci-lint tu resolve module nhu go build nen 'golangci-lint run' khong tham so la du.

## Đã làm
- Makefile: them target lint goi 'golangci-lint run'
- Chay ./mo lint

## Bằng chứng
level=error typechecking error: pattern ./...: directory prefix . does not contain modules listed in go.work or their selected dependencies

## Kết luận
**reverted** — Dung nguyen nhan da khien 'go test ./...' hong o commit 0ba35f4: workspace mode resolve pattern theo thu muc. Sua thanh 'golangci-lint run $(GO_PKGS)'.

_Đóng 2026-08-23T06:37:16Z · commit `9f5be49`_

## Đã nâng thành
none — da co chu thich canh GO_PKGS trong Makefile:8
