# ADR-0012: Rust cho agent trên robot; Go giữ cho server
- Status: accepted
- Date: 2026-10-18
- Covers: []
- Supersedes: ADR-0009 **phần agent** (ADR-0009 vẫn có hiệu lực cho server và `protocol/`)

## Context

ADR-0009 chọn Go cho cả agent lẫn server, so với C++. Nó chưa so với Rust, và được
viết khi giả định team sẽ học Go. Tới 2026-10-18 repo có 22 dòng Go, 0/49 test,
và founder quyết định đầu tư vào Rust làm ngôn ngữ dài hạn. Đây là thời điểm rẻ nhất
để xét lại: chưa có code agent nào phải viết lại.

Agent là phần duy nhất của hệ thống chạy trên thiết bị của khách hàng, với quyền
cao, nhận lệnh từ mạng (OTA, PTY), và phải sống nhiều năm không restart. Ba lợi thế
của Rust trúng đúng phần này, không trúng server:

1. **State machine OTA là lõi sản phẩm** (constitution #3). `enum` + `match` bắt buộc
   đủ nhánh: thêm state mà quên đường rollback thì không compile. `Result` có
   `#[must_use]`: không nuốt lỗi được. Luật "ghi SQLite TRƯỚC hành động" mã hoá được
   bằng kiểu: hàm chuyển state chỉ nhận token do hàm ghi DB trả ra.
2. **Bảo mật**: memory-safe như Go, thêm chặn data race lúc compile.
   `#![forbid(unsafe_code)]` là một chốt chặn máy theo đúng tinh thần ADR-0011, và
   vendor audit mã nguồn mở đọc được nó ở dòng đầu.
3. **Không GC, footprint 5–10 MB, binary tĩnh musl** trên thiết bị ta không kiểm
   soát tài nguyên.

Server không có lợi thế nào trong ba điểm trên: việc của nó là CRUD, SSE,
orchestration, ghi Timescale theo batch. Go thắng về hệ sinh thái (sqlc, pion,
gopcua), tốc độ viết, và khả năng người không chuyên review code do AI sinh.

## Options đã cân nhắc

1. **Go cho cả hai** (ADR-0009). Một toolchain, học nhanh nhất. Nhưng founder đã
   chọn đầu tư vào Rust, và Go không cho state machine kiểu-an-toàn.
2. **Rust cho cả hai.** Một ngôn ngữ mới duy nhất. Nhưng server không được lợi gì
   và nhân đôi rủi ro học trên team part-time. Có thể xét lại sau M3 bằng ADR mới
   nếu team đã thạo.
3. **C++ cho agent** vì team đã biết. Loại: agent có quyền root nhận lệnh từ mạng,
   khoảng 70% lỗ hổng nghiêm trọng trong codebase C/C++ là lỗi bộ nhớ, khách IEC 62443
   sẽ hỏi đúng câu này.
4. **Rust cho agent, Go cho server.** ← chọn

## Decision

**Agent viết bằng Rust. Server và `protocol/` (Go) giữ theo ADR-0009.** Probe theo
ADR-0013.

Bộ crate chốt cho Phase 0 (thêm crate ngoài danh sách này cần ADR theo constitution #5):

| Việc | Crate |
|---|---|
| Runtime | tokio |
| MQTT 5 | rumqttc (module v5) — **spike xác nhận response topic + user properties trước khi code OTA** |
| TLS, CSR | rustls, rcgen |
| Docker | bollard |
| SQLite | rusqlite (feature bundled) |
| Telemetry hệ thống | sysinfo |
| PTY | portable-pty |
| JSON, validate | serde, serde_json, jsonschema |
| Log có cấu trúc | tracing, tracing-subscriber (JSON) |
| Lỗi | thiserror (lib), anyhow (bin) |
| CLI | clap |
| Kiểu protocol | sinh bằng `typify` từ `specs/schemas/*.schema.json` — không viết tay |

Luật đi kèm, mỗi luật có chốt chặn máy:

| Luật | Chốt chặn |
|---|---|
| Không `unsafe` trong agent | `#![forbid(unsafe_code)]` ở `agent/src/main.rs`; `trace.py` kiểm dòng này có mặt |
| C/C++ chỉ sống sau ranh giới tiến trình, không cgo/FFI vào agent | `cargo-deny` cấm crate `-sys` ngoài danh sách cho phép (rusqlite bundled là ngoại lệ duy nhất) |
| Không `unwrap()`/`expect()` ngoài test, không `println!` | clippy `unwrap_used`, `expect_used`, `print_stdout` mức deny |
| Log phải có `deviceId`/`agentId`/`cmdId`/`deploymentId` khi có ngữ cảnh | review + skill `rust-conventions` |
| Dependency có license sạch, không CVE | `cargo-deny check` trong `./mo verify` |

Quy tắc học để không chết giữa đường: **Rust xấu mà compile thắng Rust đẹp.** Sáu
tháng đầu cho phép `clone()` thoải mái, `anyhow` cho mọi lỗi ở binary, không lifetime
trong API public, không trait object async. Tối ưu khi có số đo.

**Gate rút lui:** nếu hết 8 tuần kể từ khi `/task PRV-01` bắt đầu mà PRV-01 và TEL-03
chưa xanh, viết ADR quay về Go cho agent. Protocol nằm trong `specs/` nên hai tháng
đó mất code, không mất thiết kế.

Thay đổi hạ tầng repo đi kèm (việc của M0', xem `docs/product/08-master-plan.md`):
`docker/dev.Dockerfile` thêm Rust stable pinned + sccache + mold; `agent/` rời `go.work`
thành Cargo workspace; `track.py` đọc JUnit từ `cargo-nextest`; `Makefile` tách
`lint-go`/`lint-rust`; tên test Rust dạng `prv01_enroll_token_hop_le` (tracker đã
`norm_id` không phân biệt hoa thường và gạch).

## Consequences

+ Lõi OTA được compiler canh, không chỉ test canh. Agent không có `unsafe`, không GC.
+ Constitution #7 (agent không import server) được ép bằng ranh giới ngôn ngữ, không
  cần `depguard` cho agent nữa.
+ Hai implementation độc lập của cùng `specs/` (Rust agent, Go server) bắt được chỗ spec
  mơ hồ mà một implementation không thấy — đúng điều TEL-07 muốn kiểm.
− Hai ngôn ngữ hệ thống trong repo: hai bộ lint, hai đường codegen, image dev nặng thêm
  ~1.5 GB. Chấp nhận vì ranh giới agent/server vốn đã là ranh giới cứng nhất.
− Compile Rust chậm hơn Go. Giảm bằng `cargo check` trong vòng đỏ–xanh, sccache, mold.
− Thời gian tới mức viết PR tốt là 3–6 tháng, dài hơn Go. Đó là cái giá founder chọn
  trả, và gate rút lui 8 tuần giới hạn thiệt hại.
− Tuyển dev Rust ở Việt Nam khó hơn Go. Agent nhỏ và mã nguồn mở, nên bề mặt cần người
  là hẹp.
− Phase 1 WebRTC phía agent dùng `webrtc` crate (port của Pion), ít chín hơn Pion. Cần
  spike trước khi ký ADR WebRTC.
