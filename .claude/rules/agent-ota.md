---
paths:
  - "agent/**"
---

# Luật cứng khi làm việc trong agent/

Ba luật OTA (constitution #3) không phải khuyến nghị. Vi phạm bất kỳ luật nào
đều dẫn tới cùng một hậu quả: robot brick tại nhà khách, cách xa 300km.

1. **Rollback quyết định TẠI AGENT.** Server chỉ ra lệnh deploy. Agent tự quyết
   định khi nào quay về version cũ. Không bao giờ chờ server cho phép rollback —
   lúc cần rollback nhất thường là lúc mất mạng.

2. **Mọi chuyển state ghi SQLite TRƯỚC hành động.** Dùng transaction.
   Ghi trước, làm sau. Không có ngoại lệ "hành động này nhanh lắm" — rút điện
   không xin phép. Đây là ranh giới giữa khôi phục được và brick.

3. **Pull theo digest, không theo tag.** Tag có thể bị đẩy lại trỏ vào image khác;
   digest thì không. Không có `:latest`, không có tag mutable ở bất kỳ đâu trong
   luồng OTA.

## Chiều phụ thuộc

`agent/` **không bao giờ** import `server/` (constitution #7). Cần dùng chung thì
đưa vào `protocol/`. `golangci-lint` có rule `depguard` chặn việc này — nếu lint
báo lỗi import, đó là thiết kế đang sai, không phải lint khó tính.

## Vài thứ hay bị quên ở tầng này

- Payload > 64KB: agent **từ chối trước khi publish**, không đẩy lỗi cho broker.
- `seq` là counter monotonic, phải sống qua restart. Reset `seq` làm hỏng replay.
- `ts` dùng `time.Now().UnixMilli()`. Lệch giờ > 30s phải phát event `agent.clock_skew`.
- Mọi log kèm `deviceId`/`agentId`/`cmdId`/`deploymentId` khi ngữ cảnh có — đây là
  các khoá duy nhất để tra một sự cố ngoài hiện trường.
