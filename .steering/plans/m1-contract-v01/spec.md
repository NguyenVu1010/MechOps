---
plan: m1-contract-v01
milestone: M1
status: draft
covers: [TEL-01, TEL-07]
adr: [0001]
requirements:
  - docs/protocol-notes.md#3
  - docs/product/06-spec-management.md
---

# m1-contract-v01 · spec — CÁI GÌ

## Hành vi mong đợi

`docs/protocol-notes.md` dang la narrative cho nguoi doc. Feature nay chuyen phan
**hop dong** cua no thanh dang may doc duoc, de code khong the lech spec ma khong ai biet.

Xong feature nay thi:

1. Moi message MQTT trong protocol-notes muc 3 co mot JSON Schema trong `specs/schemas/`.
2. `specs/asyncapi.yaml` khai du channel cho cac message do (khong con dong TODO(M0)).
3. `protocol/topics.go` co constant cho moi topic da khai trong asyncapi — khong con
   topic nao chi ton tai duoi dang chuoi trong tai lieu.
4. Moi schema co it nhat mot test vector hop le va mot khong hop le trong
   `specs/testvectors/`, va `./mo gen` validate sach.
5. `make gen` sinh that `protocol/types.gen.go` tu schema, khong con la `echo TODO`.

## Ngoài scope

- Message cua **command channel** (protocol-notes muc 4) va **OTA manifest** (muc 5):
  thuoc M3, khong lam bay gio.
- `specs/openapi.yaml` cho REST enroll: thuoc feature provisioning (PRV-*), khong phai day.
- Probe API (muc 7): co file `specs/probe-api.md` rieng, giu nguyen o feature nay.
- Viet code agent/server dung cac type sinh ra — feature nay chi dung o contract.

## Nguồn yêu cầu

- `docs/protocol-notes.md` muc 3 (Envelope & Profile schema) — noi dung nguon.
- `docs/product/06-spec-management.md` "Lop 2 — Contract may doc duoc" — ly do lam.
- ADR-0001 (MQTT thay vi TCP tu che) — rang buoc dinh dang message.

## Vì sao feature này đi trước

Ba viec con lai cua M0 (topic constant, codegen, ha tang [I]) deu phu thuoc vao
schema. Va `contract-guard` luat 1 dang tuyen bo "types.gen.go sinh tu schema, khong
sua tay" trong khi chua co gi sinh ra file do — luat dang tro vao khoang khong.
