---
plan: m1-contract-v01
milestone: M1
status: open
covers: [TEL-01, TEL-07]
adr: [0001]
requirements:
  - docs/protocol-notes.md#3
  - docs/product/06-spec-management.md
---

# m1-contract-v01 · clarify — CHƯA RÕ CÁI GÌ

> Agent điền câu hỏi. **Người** điền đáp án. Chưa có đáp án thì chưa chốt spec.
> Năm câu dưới đây đều làm đổi khối lượng công việc, không phải hỏi cho có.

### 1. Envelope dùng chung hay lặp trong từng schema?

`telemetry.schema.json` hien dat `v` / `ts` / `seq` truc tiep trong object. Neu moi
message deu co ba field nay thi nen tach `envelope.schema.json` roi `$ref`, hay cu
lap lai o tung file?

- Tach: doi nghia mot lan la doi het, kho lech.
- Lap: moi schema doc doc lap duoc, sinh type de hon.

**Đáp:**

### 2. Làm bao nhiêu schema trong feature này?

Protocol-notes muc 3 co 5 message: `telemetry` (da co), `state`, `events`,
`agents/status`, `agents/inventory`. Lam ca 5, hay chi lam nhung cai M1 that su can
(`status` cho LWT/TEL-03, `state` cho TEL-04)?

**Đáp:**

### 3. Công cụ codegen nào?

`Makefile` ghi TODO la `go-jsonschema`. Day la **dependency moi** nen theo
constitution #5/#6 phai co ADR. Ba lua chon:

- `go-jsonschema` (atombender) — pho bien, nhung sinh type kha tho voi `$ref` long nhau
- `quicktype` — manh hon, nhung keo theo Node vao container dev
- Viet tay struct trong `protocol/`, chi dung schema de validate — khong can dependency

**Đáp:**

### 4. `additionalProperties: true` là cơ chế forward-compat chính thức?

`telemetry.metrics` dang de `additionalProperties: true`. TEL-07 doi "field la khong
gay loi". Vay day co phai luat cho **moi** schema khong, hay chi rieng `metrics`?
Neu la luat chung thi phai ghi vao skill `contract-guard`.

**Đáp:**

### 5. TEL-07 là tầng [H] — feature này có được coi là xong khi TEL-07 chưa tick?

TEL-01 la [U], `./mo gen` chay duoc ngay. TEL-07 la [H], chi nguoi tick sau khi chay
tren phan cung that. Feature dong khi TEL-01 xanh, hay doi ca TEL-07?

**Đáp:**
