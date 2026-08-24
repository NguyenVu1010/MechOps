# Hướng dẫn review — MechOps

Đây là file Claude Code Review đọc để hiệu chỉnh mức nghiêm trọng cho repo này.
Bối cảnh chung ở `CLAUDE.md`; file này chỉ nói *cái gì đáng chặn merge*.

Sản phẩm là nền tảng quản trị fleet robot có OTA. Một bug ở đây không làm hỏng
một request — nó brick một con robot ở nhà khách hàng, cách 300km. Hiệu chỉnh
mức nghiêm trọng theo thực tế đó.

## 🔴 Important — chặn merge

Chỉ dùng cho các lỗi sau. Mọi thứ khác nhiều nhất là Nit.

- **Lệch hợp đồng.** Code đọc/ghi field khác với `specs/schemas/*.schema.json`
  hoặc `specs/asyncapi.yaml`. Spec thắng code (constitution #4) — báo lỗi ở phía code.
- **Đổi nghĩa hoặc xóa field đang có** trong `specs/`, kể cả khi có vẻ vô hại.
  Đây là breaking change, là quyết định của founder, không phải của PR.
- **Ghi state SAU khi hành động** trong `agent/`. Luật OTA #2: mọi chuyển state
  phải ghi SQLite TRƯỚC hành động. Rút điện giữa chừng mà state chưa ghi = robot brick.
- **Pull theo tag thay vì digest** trong luồng OTA (luật OTA #3).
- **Rollback quyết định ở server** thay vì ở agent (luật OTA #1).
- **Topic string hardcode** ngoài `protocol/topics.go`.
- **Thiếu check payload > 64KB** ở bất kỳ encoder mới nào phía agent.
- **Nuốt lỗi**: `err` bị bỏ qua, hoặc log-rồi-return-nil.
- **Query không scope theo tenant** trong `server/`.
- **Test được sửa cho khớp bug của code**, hoặc `t.Skip` thêm vào để CI xanh.
- **Test ID được tick mà không có evidence trỏ được** (constitution #2).
- **Secret / cert / token đi vào log hoặc vào repo.**

## 🟡 Nit — nói, nhưng đừng chặn

Tối đa **5 nit mỗi lần review**. Nhiều hơn thì gộp thành một dòng "còn N mục tương tự".
Nếu tất cả phát hiện đều là nit, mở đầu phần tóm tắt bằng "Không có vấn đề chặn merge".

## Không báo

- Bất cứ thứ gì CI đã bắt: gofmt, `go vet`, golangci-lint, lỗi type.
  Trùng lặp làm người ta bỏ qua cả review.
- File `*.gen.go` — sinh từ schema, sửa schema chứ không sửa file.
- `docs/evidence/**` và `docs/test-status.*` — máy ghi, người không sửa.
- Ý kiến về đặt tên/bố cục khi code đang theo đúng `.claude/skills/go-conventions`.

## Bằng chứng trước khi báo

Mọi phát hiện về *hành vi* phải kèm `file:dòng` trong source, không suy từ tên hàm.
Nếu chỉ suy đoán được mà không chỉ ra được dòng, hạ xuống Nit và nói rõ là phỏng đoán.

## Luôn kiểm

- Mỗi hàm chạm network/DB nhận `context.Context` là tham số đầu.
- Log dùng `slog` và kèm `deviceId`/`agentId`/`cmdId`/`deploymentId` khi ngữ cảnh có.
- Field mới trong schema là optional, và có test vector cả hợp lệ lẫn không hợp lệ.
- `agent/` không import `server/` và ngược lại (constitution #7).

## Khi review lại lần hai trở đi

Chỉ báo Important mới. Không thêm nit mới — một sửa đổi một dòng không đáng đi tới
vòng review thứ bảy vì phong cách.
