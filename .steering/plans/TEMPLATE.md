# Template — một plan trong .steering/plans/<mX-ten>/

Tạo bằng `./mo steer plan new <mX-ten> --milestone M3 --covers "OTA-01,OTA-07" --adr 0005`.

```
<mX-ten>/
├── STATUS.md      ← MẶT TIỀN. Máy sinh: cổng nào đã chốt, task mấy/mấy, ID nào xanh
├── spec.md        CÁI GÌ              draft → locked
├── clarify.md     CHƯA RÕ CÁI GÌ      open  → answered      ← GATE NGƯỜI
├── plan.md        LÀM THẾ NÀO         draft → locked
├── testcases.md   LÀM SAO BIẾT XONG   draft → locked
├── tasks.md       THỨ TỰ              draft → locked        ← dấu tích do MÁY điền
└── JOURNAL.md     ĐÃ XẢY RA GÌ        máy sinh từ entries có `plan: <mX-ten>`
```

Mở feature ra thì `STATUS.md` trả lời ngay: đang phát triển gì, chốt tới đâu, còn bao xa.

## Frontmatter — mọi file dùng chung, khác nhau ở `status`

```yaml
---
plan: m3-ota-v1                       # trùng tên thư mục
milestone: M3
status: draft                         # của RIÊNG file này, không phải của cả plan
covers: [OTA-01, OTA-07]              # BẮT BUỘC — trace kiểm với catalog
adr: [0005]                           # trace kiểm tồn tại + chưa supersede
requirements:
  - docs/product/01-spec-v2.md#ota
---
```

`status` là **của từng artifact**, không phải của cả plan. Chốt cả cụm một lần thì
gate tuần tự của SDD không tồn tại.

## Cổng chốt — tuần tự, máy cưỡng chế

```
./mo steer plan lock <plan> spec       → cần clarify đã `answered`
./mo steer plan lock <plan> plan       → cần spec locked
./mo steer plan lock <plan> testcases  → cần plan locked + đủ mục `## <ID>` cho mọi covers
./mo steer plan lock <plan> tasks      → cần testcases locked + mọi task có ID trong covers
```

Mỗi `lock` còn kiểm nội dung không còn chỗ `<...>`. Chốt xong bốn cổng thì vào `/task`.
`./mo trace` chặn nếu ai lách thứ tự bằng cách sửa tay `status`.

Vì sao tuần tự: bẻ task từ một plan chưa chốt là bẻ theo thứ còn đổi được dưới chân mình.

---

## spec.md — CÁI GÌ
- Hành vi mong đợi, viết bằng thứ quan sát được từ bên ngoài
- Ngoài scope: thứ cố tình không làm (để người review không đi tìm)
- Nguồn yêu cầu: mục nào trong `docs/product/` hoặc ADR nào dẫn tới feature này

## clarify.md — CHƯA RÕ CÁI GÌ  ← GATE NGƯỜI
- Agent điền câu hỏi, **người** điền đáp án. Dạng `### N. <câu hỏi>` + `**Đáp:**`
- Còn câu chưa có đáp án thì `lock spec` bị chặn (constitution #9)

## plan.md — LÀM THẾ NÀO  (skill `tech-plan`)
1. Delta hợp đồng `specs/` — field/topic/message nào đổi (field mới phải optional)
2. State machine — trạng thái nào ghi SQLite, ghi lúc nào
3. Ma trận thất bại — mất điện · mất mạng · disk đầy · lệch giờ, **mỗi dòng một test ID**
4. Chia tầng [U]/[I]/[H]
5. Đường ranh module (chiều phụ thuộc server → protocol ← agent)
6. Quyết định cần ADR

## testcases.md — LÀM SAO BIẾT XONG
**Thiết kế test, KHÔNG phải danh sách ID.** Danh sách ID là `docs/product/05-test-catalog.md`
— nguồn sự thật duy nhất, đừng chép lại. File này giữ thứ catalog không chứa nổi:

```markdown
## OTA-07 · [I] · Digest sai → không start
- **Tiền đề:** registry có image, manifest digest sai 1 ký tự
- **Thao tác:** agent nhận cmd deploy với digest đó
- **Mong đợi:** state không rời PULLING; event `ota.digest_mismatch`; container cũ vẫn chạy
- **Bằng chứng:** dòng log nào, hàng nào trong SQLite
- **Tên test:** `TestOTA07_DigestMismatch`

## ID đề xuất thêm vào catalog
- OTA-13 — [I] — digest qua proxy trả rỗng
  → thêm vào 05-test-catalog.md + CATALOG track.py CÙNG commit trước khi dùng
```

Mọi ID trong `covers:` phải có một mục `## <ID>` trước khi `lock testcases`.
"Mong đợi" phải quan sát được từ bên ngoài — "không lỗi" không phải kết quả mong đợi.

## tasks.md — THỨ TỰ
```markdown
- [ ] T1 — Schema enroll request/response · `PRV-01`
```
- Task ≤ nửa ngày, **mỗi task ≥1 test ID**, ID phải nằm trong `covers:`
- **Dấu tích do máy điền** (`./mo steer plan sync`): task xanh khi MỌI test ID của nó
  đã pass trong tracker. **Tick tay bị `./mo trace` chặn** — đó là cách `tasks.md`
  biến thành nguồn "đã xong" thứ hai rồi mâu thuẫn với `test-status.md` (constitution #2).
- `./mo status` tự sync, nên checkbox không bao giờ cũ.

---

Sửa bất kỳ file nào ở trên → chạy lại `/spec-analyze`.
Feature đóng → `./mo steer plan freeze <mX-ten>`: mọi artifact thành `frozen`, bất biến.
