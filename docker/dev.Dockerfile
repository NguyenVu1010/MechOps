# Môi trường dev MechOps — local phải giống CI (ADR 0010).
# Máy dev không cần cài Go/Python/make; mọi lệnh đi qua ./mo.
FROM golang:1.22-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 python3-jsonschema python3-yaml make git ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# Phiên bản golangci-lint có MỘT nhà: .golangci-version ở root.
# CI đọc cùng file đó, nên container dev và CI không thể lệch nhau.
#
# Tải binary đã build sẵn, KHÔNG `go install`: `go install` sẽ build lint bằng
# toolchain Go 1.22 của image và vỡ khi bản lint mới đòi Go mới hơn.
COPY .golangci-version /tmp/.golangci-version
RUN curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh \
      | sh -s -- -b /usr/local/bin "$(cat /tmp/.golangci-version)" \
 && rm /tmp/.golangci-version \
 && golangci-lint --version

# Repo được bind-mount vào /w. Git từ chối repo thuộc UID khác nếu không khai safe.
RUN git config --global --add safe.directory /w

ENV GOCACHE=/cache/go-build \
    GOMODCACHE=/cache/go-mod \
    GOFLAGS=-buildvcs=false

WORKDIR /w
