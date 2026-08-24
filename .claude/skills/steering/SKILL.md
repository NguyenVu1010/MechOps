---
name: steering
description: Ghi nhật ký hành động vào .steering/ khi vứt bỏ một hướng đi, phát hiện một giả định sai, hoặc quyết định điều gì đó chưa tới mức ADR. Trigger — bỏ cách này, thử cách khác, hoàn tác, revert, làm lại, hoá ra, tưởng là, không phải như tôi nghĩ, sai rồi, quay lại.
paths:
  - ".steering/**"
---

# Steering — ghi lại cả cái sai

Git chỉ giữ thứ sống sót. Hướng đã thử rồi bỏ, giả định hoá ra sai — không hệ nào
trong repo ghi được, mà đó lại là thứ đắt nhất khi ai đó (kể cả mày ở phiên sau)
gặp lại đúng vấn đề. Format đầy đủ: `.steering/README.md`.

## Ghi lúc nào

**Ngay lúc đổi hướng**, không để tới cuối phiên. Cuối phiên thì lý do thật đã bị
viết lại thành lý do gọn gàng, mà phần đắt nhất chính là lý do thật.

| `--kind` | Dùng khi |
|---|---|
| `attempt` | thử một hướng chưa chắc |
| `wrong` | giả định đã tin là đúng, hoá ra sai |
| `discovery` | phát hiện về hệ thống, chưa thành bug |
| `decision` | quyết định nhỏ chưa tới mức ADR |

`risky` là của hook — tự ghi khi có lệnh phá hoại. Việc của mày chỉ là **đóng** nó.

`--area`: `agent · server · protocol · probe · dashboard · specs · infra · flow`

**`--plan <mX-ten>`**: đang làm trong một feature thì luôn gắn. Nhờ nó
`.steering/plans/<mX-ten>/JOURNAL.md` gom được cả plan lẫn thứ đã thử rồi bỏ vào
cùng một chỗ — không gắn thì mục vẫn ghi được nhưng rơi ra ngoài hồ sơ của feature.

## Ghi trong một lượt

Điền hết ngay lúc `new` — đừng để lại placeholder rồi hẹn quay lại sửa, vì sẽ không quay lại.

```bash
./mo steer new --kind wrong --area agent --ids OTA-07 --plan m3-ota-v1 \
    --title "verify digest bang header cua registry" \
    --context "Dung buoc verify cua OTA-07" \
    --why    "Tuong registry tra Docker-Content-Digest o moi response" \
    --did    "pull.go: doc header | ./mo verify" \
    --proof  "header rong khi qua proxy — pull.go:88 log digest=''"

./mo steer close --last --outcome reverted \
    --why      "doi sang doc digest tu manifest da tai" \
    --promoted "OTA-13"
```

Tiêu đề và nội dung dùng **ASCII không dấu** cho gọn khi grep; tiếng Việt có dấu
vẫn chạy nhưng làm tên file và lệnh grep khó chịu hơn.

## Ba mục quyết định giá trị bản tin

- **`--why` (Tin rằng)** — viết ở thì **tin-là-đúng**: *"tưởng registry trả digest ở
  header"*. Đừng viết *"thử cách A"*: giả định sai chính là thứ người sau cần đọc,
  vì họ sắp tin đúng như thế.
- **`--proof` (Bằng chứng)** — quan sát, không phải cảm nhận. `file:dòng`, output
  lệnh, dòng log. *"header rỗng khi qua proxy"*, không phải *"cách đó không ổn"*.
- **`--promoted` (Đã nâng thành)** — **bắt buộc**, kể cả `none`. Nhật ký ghi lại quá
  khứ; nó không ngăn được lần sau. Thứ ngăn được là một test ID (`bug-to-test`), một
  ADR (`adr`), hay một dòng trong skill. Ô này buộc trả lời "vậy lần sau thì sao".

Một mục một chuyện, tối đa 30 dòng. Dài hơn thì nó là ADR hoặc là test, không phải
nhật ký — `./mo trace` sẽ cảnh báo.

## Ranh giới — đừng tạo nguồn sự thật thứ hai

| Thứ này | Nhà của nó |
|---|---|
| Commit thành công bình thường | `git log` |
| Kết quả test | `docs/evidence/` |
| Quyết định kiến trúc | `docs/adr/` (skill `adr`) |
| Bug cần canh về sau | test ID mới (skill `bug-to-test`) |
| Trạng thái test hiện tại | `docs/test-status.md` |

## Không làm

- Không sửa mục **đã đóng**. Sai → mục mới với `--supersedes S000N`.
  (Mục còn `open` là bản nháp, sửa thoải mái.)
- Không gõ tay `INDEX.md` — máy sinh.
- Không ghi mục chỉ để trông chăm chỉ. Nhật ký toàn tiếng ồn thì không ai đọc, và
  cũng như không.
