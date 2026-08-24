---
name: troubleshoot
description: BẮT BUỘC đọc khi test đỏ không rõ lý do, hành vi khác mong đợi, robot/agent không lên, telemetry không về, OTA kẹt, hoặc cần đọc evidence để dựng lại sự cố. Trigger, debug, đỏ, fail, không chạy, kẹt, treo, offline, không thấy, tại sao, dựng lại lỗi, đọc log.
---

# Troubleshoot — dựng lại trước, sửa sau

Khác skill `bug-to-test` (đó là **kỷ luật**: ID mới trước khi sửa). Đây là **cách**:
làm sao biết chuyện gì đã xảy ra trong một hệ 4 tầng bất đồng bộ.

## Luật số một

**Chưa tái hiện được thì chưa hiểu — không sửa.** Sửa theo phỏng đoán trong hệ
bất đồng bộ thường làm triệu chứng biến mất mà nguyên nhân ở lại, và nó quay lại
ở nhà khách hàng thay vì trên máy.

## Khoanh tầng trước khi đào

Bốn tầng, hỏi đúng thứ tự này — đừng bắt đầu từ tầng đang nghi:

| Tầng | Câu hỏi khoanh vùng | Nhìn ở đâu |
|---|---|---|
| agent | tiến trình có sống? state trong SQLite là gì? | log agent, bảng state |
| broker | message có tới EMQX? ACL có chặn? | log EMQX, `$SYS`, thử `mosquitto_sub` |
| server | có nhận và ghi được? | slog server, Postgres/Timescale |
| dashboard | có subscribe SSE? | network tab, log server |

Sai lầm hay gặp: "dashboard không hiện" nên đi sửa dashboard, trong khi agent chưa
publish lần nào. Bao giờ cũng đi từ nguồn dữ liệu ra, không từ chỗ nhìn thấy vào.

## Khoá tra cứu

Mọi log là slog JSON và **phải** kèm `deviceId` / `agentId` / `cmdId` / `deploymentId`
khi ngữ cảnh có. Đây là các khoá duy nhất nối được sự kiện giữa bốn tầng — lọc theo
một khoá và đọc dọc theo thời gian, đừng đọc từng tầng riêng.

Log không có khoá tra cứu là một bug riêng: ghi lại, sửa (skill `go-conventions`).

## Đọc evidence

`docs/evidence/ci/<ISO>-<commit>/raw.jsonl` là output `go test -json` **nguyên bản**.
Tên thư mục chứa commit hash — dựng lại được đúng cây mã đã cho ra kết quả đó.

```bash
./mo shell
go test -run TestOTA07 -v ./agent/...      # chạy lại đúng một test
git stash && git checkout <commit>          # về đúng cây mã của evidence
```

Test xanh trong CI mà đỏ ở local (hoặc ngược lại) thì nghi theo thứ tự:
build tag `integration` · hạ tầng compose chưa lên · timing/race (chạy `-race -count=5`).

## Ba câu hỏi trước khi sửa một dòng

1. **Tái hiện được chưa?** Chưa → quay lại khoanh tầng.
2. **Đây là bug của code hay của spec?** Code lệch `specs/` là bug của code
   (constitution #4). Spec sai là quyết định của founder — dừng và hỏi.
3. **Có test ID nào cover chưa?** Chưa → chuyển sang skill `bug-to-test`,
   thêm ID mới TRƯỚC khi sửa. Không có ngoại lệ cho "lỗi nhỏ".

## Bẫy riêng của hệ này

- **Test đỏ vì `seq`** — counter monotonic phải sống qua restart. Reset `seq` làm
  replay hỏng, và triệu chứng hiện ở server chứ không ở agent.
- **Offline "sai"** — LWT phát theo keepalive×1.5, không tức thì. Đo trước khi gọi là bug.
- **OTA kẹt** — đọc state SQLite TRƯỚC, đừng đọc log trước. Nếu state không khớp
  hành động thực tế thì đã vi phạm luật ghi-trước-hành-động, và đó mới là bug thật.
- **Message biến mất không log** — nghi ACL EMQX (ACL-01/02) và trần payload 64KB
  (ACL-04) trước khi nghi code.
- **Lệch giờ > 30s** làm mọi thứ theo `ts` trông vô lý. Kiểm `agent.clock_skew` (TEL-06).

## Không làm

- Không thêm log rồi để đó — log tạm phải xoá hoặc nâng thành slog có khoá tra cứu.
- Không `t.Skip` một test đỏ để đi tiếp. Test đỏ = việc chưa xong.
- Không sửa test cho khớp hành vi của code.
