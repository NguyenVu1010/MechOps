---
name: rust-conventions
description: Quy ước Rust riêng của repo MechOps, áp cho agent. Đọc khi viết code Rust mới, thêm crate, viết state machine OTA, hoặc thêm logging trong agent. Trigger — Rust, cargo, crate, tokio, agent, state machine, rusqlite, tracing.
paths:
  - "**/*.rs"
  - "**/Cargo.toml"
metadata:
  adr: [0012, 0005]
---

# Rust Conventions — MechOps agent

## Layout
- `/agent` là một Cargo workspace. Crate `mechops-agent` (binary) và `mechops-protocol`
  (kiểu sinh bằng `typify` từ `specs/schemas`, **không sửa tay**).
- Module trong `mechops-agent/src/`: `identity` (cert, enroll, renew) · `transport`
  (trait + impl MQTT) · `telemetry` · `buffer` (SQLite offline) · `probe_hub` (Unix
  socket NDJSON) · `ota` (state machine + docker) · `cmd` (dispatcher) · `pty` · `logs`.
- Agent **không** biết server tồn tại ngoài `specs/`. Không có crate chung với server.

## Luật có chốt chặn máy (ADR-0012)
- `#![forbid(unsafe_code)]` ở `main.rs`. Không cgo/FFI; C/C++ sống sau ranh giới tiến trình.
- Không `unwrap()`/`expect()` ngoài `#[cfg(test)]`. Không `println!` — dùng `tracing`.
- Crate mới phải có trong bảng ADR-0012; crate `-sys` bị `cargo-deny` chặn.

## Quy ước
- Lỗi: `thiserror` cho kiểu lỗi của module, `anyhow` ở `main`. Wrap với ngữ cảnh:
  `.context("pull image theo digest")`. Không nuốt lỗi bằng `let _ =`.
- Log: `tracing` với field có cấu trúc, luôn kèm `device_id`/`agent_id`/`cmd_id`/
  `deployment_id` khi có. Tên field snake_case trong code; subscriber JSON xuất ra.
- State machine OTA: một `enum OtaState`, `match` không có nhánh `_`. Mọi chuyển state
  đi qua `Store::persist_transition()` trả về `Persisted<NewState>`; hàm hành động
  (pull, stop, start) chỉ nhận `Persisted<_>`. Đây là cách constitution #3 "ghi SQLite
  TRƯỚC hành động" được compiler canh.
- Async: tokio. Một task cho MQTT, một cho probe hub, một cho OTA; nói chuyện qua
  `mpsc`. Không `Arc<Mutex<_>>` quanh state machine — state machine sở hữu dữ liệu.
- Sáu tháng đầu: `clone()` thoải mái, không lifetime trong API public, không trait
  object async. Tối ưu khi có số đo (ADR-0012).
- Test: tên `<id bỏ gạch, chữ thường>_<mô tả>` (ví dụ `prv01_enroll_token_hop_le`,
  `ota04_rut_dien_giua_downloading`) để tracker tick được. Chạy bằng `cargo nextest`.
- Test ĐỎ trước (constitution #1): `cargo check` trong vòng đỏ–xanh, `cargo nextest`
  khi commit.
