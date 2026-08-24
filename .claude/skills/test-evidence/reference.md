# Quy trình từng tầng test

Chi tiết của `SKILL.md`. Đọc khi thật sự viết/chạy test của tầng tương ứng.

---

## [U] — Unit / contract

Chạy mọi PR, không cần hạ tầng. **Ưu tiên tối đa tầng này**: vòng phản hồi vài giây
là thứ giữ cho TDD sống được.

```bash
./mo verify                       # cả bộ
./mo shell                        # rồi:
go test -run TestTEL01 -v ./protocol/...
```

- File `*_test.go` thường, không build tag.
- Test vector nằm ở `specs/testvectors/{valid,invalid}/`. Thêm vector mới thì thêm
  **cả hai chiều** nếu field có ràng buộc — vector chỉ có bản hợp lệ không chứng minh
  được validator từ chối đúng thứ cần từ chối.
- `./mo gen` validate toàn bộ vector; chạy nó sau mỗi lần đụng `specs/`.

---

## [I] — Integration

Cần EMQX + Postgres + registry thật. Chạy nightly và khi gọi tay.

```bash
docker compose -f deploy/docker-compose.yml up -d
./mo test-integration
docker compose -f deploy/docker-compose.yml logs --tail=100   # khi đỏ
```

- **Bắt buộc** build tag ở dòng đầu file, trước `package`:
  ```go
  //go:build integration
  ```
  Thiếu tag → test chạy trong mọi PR và đỏ vì không có hạ tầng.
- Đợi hạ tầng **sẵn sàng**, không đợi bằng `time.Sleep`. Poll cho tới khi connect
  được, có timeout rõ ràng. `Sleep` cố định là nguồn flaky số một ở tầng này.
- Mỗi test tự dọn: agent giả lập, topic, hàng trong DB. Test [I] để lại rác làm hỏng
  test sau nó, và triệu chứng sẽ hiện ở test khác — rất tốn thời gian để lần ra.
- Test kiểm hành vi **theo thời gian** (LWT, reconnect, replay) phải nêu rõ ngưỡng
  lấy từ đâu. Ví dụ LWT là keepalive×1.5, không phải "vài giây".

---

## [H] — Hardware-in-the-loop

**Claude không bao giờ tick tầng này.** Không viết test Go cho nó.

Việc của agent là **soạn sẵn để người chạy được**:

1. Kiểm ID đó thật sự là `[H]` trong catalog.
2. Viết checklist các bước — cụ thể tới mức người không tham gia phiên này làm theo được:
   phần cứng nào, trạng thái ban đầu, thao tác gì (rút điện lúc nào, rút mạng ở đâu),
   quan sát gì, thế nào là đạt.
3. Nêu rõ **cách quan sát**: nhìn log nào, dashboard chỗ nào, sau bao lâu.
4. Dừng lại. Báo cho người: chạy `./mo hw-test ID=<ID> TESTER=<tên> HW="<phần cứng>"`.

Biên bản tự sinh vào `docs/evidence/hw/`, có tên người ký và ngày (catalog quy tắc #2).
Kỷ luật này rẻ; robot brick tại nhà khách thì không.

---

## Một test cover nhiều ID

Dùng subtest, tên subtest chứa ID:

```go
func TestOTA02_HealthFail(t *testing.T) {
    t.Run("OTA02_RollbackTuDong", func(t *testing.T) { ... })
    t.Run("OTA03_CrashLoop",      func(t *testing.T) { ... })
}
```

`track.py` đọc ID từ tên test **và** tên subtest, nên cả hai ID đều được tick.

---

## Khi tracker không tick

Xảy ra khi tên test không khớp `Test<ID bỏ gạch><số>_...`. `track.py` bỏ qua im lặng —
`./mo verify` in `Không có ID nào khớp trong output`. Kiểm theo thứ tự:

1. Tên test đúng dạng chưa (`TestOTA07_...`, không phải `TestOta07` hay `TestOTA_07`).
2. ID có trong `CATALOG` của `track.py` chưa.
3. Test có thật sự chạy không, hay bị lọc bởi build tag / `-run`.
