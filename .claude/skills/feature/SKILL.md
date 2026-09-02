---
name: feature
description: Mở feature mới theo vòng ngoài SDD (specify, clarify, plan, tasks, analyze). Dùng khi bắt đầu một cụm việc/milestone mới.
argument-hint: <tên feature + milestone + test ID liên quan>
disable-model-invocation: true
---

# Feature — vòng ngoài

Bắt đầu feature: `$ARGUMENTS`.

```bash
./mo steer plan new <mX-ten> --milestone M3 \
    --covers "OTA-01,OTA-02,OTA-07" \
    --adr 0005 \
    --requirements "docs/product/01-spec-v2.md#ota"
```

Lệnh này dựng sẵn bốn file kèm frontmatter. `--covers` bắt buộc và bị kiểm với
catalog — feature không cover test ID nào là feature không hợp lệ, và ID ma thì
tracker không bao giờ tick.

Plan nằm trong `.steering/plans/` chứ không phải `specs/`: `specs/` là **hợp đồng**
máy-đọc-được (phần open source), plan là **quá trình**. Nhờ vậy `JOURNAL.md` của
plan gom được mọi thứ đã thử và bỏ trong lúc làm feature — plan và kết quả nằm cạnh
nhau, không phải nhảy hai thư mục.

## Sáu bước, DỪNG ở bước 2

Chưa rõ đường đi → chạy skill `brainstorm` **trước** bước 1. Đường đi đã rõ thì bỏ qua.

1. **specify** → `spec.md`
   Hành vi mong đợi, thứ **ngoài scope**, và dòng `covers: [<test ID>]` lấy từ
   `docs/product/05-test-catalog.md`. Feature không cover ID nào = feature không hợp lệ.
   Viết bằng hành vi quan sát được, không bằng cách cài đặt.

2. **clarify** → `clarify.md` → **DỪNG**
   Liệt kê **MỌI** điểm mờ thành câu hỏi rồi dừng, chờ founder trả lời thẳng vào file.
   Không tự giả định, kể cả khi đoán được và kể cả khi đoán đúng — gate này là chỗ
   giả định sai bị giết với giá rẻ nhất trong toàn bộ quy trình.

3. **plan** → `plan.md` — skill `tech-plan`
   Delta hợp đồng · state machine · ma trận thất bại · chia tầng test · đường ranh
   module · quyết định cần ADR. Bỏ bước này thì mọi quyết định kỹ thuật bị đẩy vào
   lúc đang code, và `tasks.md` chỉ là danh sách mong muốn.

4. **tasks** → `tasks.md`
   Mỗi task ≤ nửa ngày, bắt buộc gắn ≥1 test ID. Task không có ID = task không hợp lệ.
   Thứ tự: contract trước, agent trước dashboard, happy path trước edge case
   (`02-dev-plan-phase0.md` mục 4).

5. **testcases** → `testcases.md`
   Thiết kế test cho **mọi** ID trong `covers:`: tiền đề · thao tác · mong đợi ·
   bằng chứng · tên test. "Mong đợi" phải quan sát được từ bên ngoài — "không lỗi"
   không phải kết quả. Hành vi chưa có ID → mục "ID đề xuất thêm vào catalog".

6. **analyze** — skill `spec-analyze`
   Đối chiếu chéo spec ↔ plan ↔ testcases ↔ tasks ↔ catalog. Có `DỪNG` thì không đi tiếp.

## Cổng chốt — sau mỗi bước

```bash
./mo steer plan lock <plan> spec        # cần clarify đã answered
./mo steer plan lock <plan> plan
./mo steer plan lock <plan> testcases
./mo steer plan lock <plan> tasks
```

Tuần tự và máy cưỡng chế: bẻ task từ plan chưa chốt là bẻ theo thứ còn đổi được
dưới chân mình. `lock` cũng chặn nếu file còn chỗ `<...>`. Chốt xong bốn cổng mới
vào `/task`. `STATUS.md` (máy sinh) cho biết đang chốt tới đâu.

Xong vòng ngoài mới vào vòng trong: `/task <ID>`.

## Trong lúc làm

Mọi mục nhật ký của feature này phải gắn `--plan <mX-ten>`:

```bash
./mo steer new --kind attempt --plan m3-ota-v1 --area agent --ids OTA-07 ...
```

`JOURNAL.md` trong thư mục plan tự gom lại — mở plan ra là thấy cả thứ đã định làm
lẫn thứ đã thử rồi bỏ.

**Đừng tick tay `tasks.md`.** Dấu tích do `./mo steer plan sync` điền từ tracker:
task xanh khi mọi test ID của nó đã pass. `./mo trace` chặn tick tay.

## Khi feature đã mở mà phải sửa

Sửa một trong bốn artifact → chạy lại `/spec-analyze`. Đừng đi tiếp bằng trí nhớ:
lệch giữa spec và tasks không tự báo, nó chỉ hiện ra ở review hoặc ở khách hàng.

## Khi feature đóng

`./mo steer plan freeze <mX-ten>` — `status: frozen`, từ đó plan bất biến. Lệnh từ
chối nếu còn mục nhật ký `open`: đóng băng kèm nợ là đóng băng một nửa sự thật.
