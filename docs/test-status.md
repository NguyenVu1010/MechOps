# RobotOps — Test Status

> ⚙️ File này do `tools/testtrack/track.py` sinh — **không sửa tay**.
> Cập nhật: 2026-07-13T10:14:36Z · commit `c732f36` · **0/49 ✅** (0%)

## A · Provisioning — 0/5 `░░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | PRV-01 | [I] | Enroll token hợp lệ | — | — |
| ⬜ | PRV-02 | [I] | Token đã dùng/hết hạn | — | — |
| ⬜ | PRV-03 | [I] | Cert tự gia hạn <30 ngày | — | — |
| ⬜ | PRV-04 | [I] | Cert hết hạn hoàn toàn | — | — |
| ⬜ | PRV-05 | [H] | Enroll Jetson+Pi <5 phút | — | — |

## B · ACL cách ly — 0/4 `░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | ACL-01 | [I] | Agent A publish topic B → từ chối | — | — |
| ⬜ | ACL-02 | [I] | Subscribe wildcard bị giới hạn | — | — |
| ⬜ | ACL-03 | [I] | Không cert → chặn tầng TLS | — | — |
| ⬜ | ACL-04 | [I] | Payload >64KB bị từ chối | — | — |

## C · Telemetry/offline — 0/7 `░░░░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | TEL-01 | [U] | Test vectors validate đúng | — | — |
| ⬜ | TEL-02 | [I] | 24h không leak, seq liền | — | — |
| ⬜ | TEL-03 | [I] | LWT khi rút mạng | — | — |
| ⬜ | TEL-04 | [I] | Replay đúng seq/ts sau reconnect | — | — |
| ⬜ | TEL-05 | [I] | Buffer 24h+ downsample | — | — |
| ⬜ | TEL-06 | [I] | Clock skew >30s có event | — | — |
| ⬜ | TEL-07 | [H] | Field lạ không gây lỗi | — | — |

## D · Probe API — 0/6 `░░░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | PRB-01 | [U] | apiVersion sai → từ chối sạch | — | — |
| ⬜ | PRB-02 | [I] | AMR profile lên dashboard | — | — |
| ⬜ | PRB-03 | [I] | Probe chết → degraded, agent sống | — | — |
| ⬜ | PRB-04 | [I] | Probe restart không nhân đôi | — | — |
| ⬜ | PRB-05 | [I] | 2 probe Mode B hợp nhất inventory | — | — |
| ⬜ | PRB-06 | [H] | Kill node ROS thật → alarm ≤10s | — | — |

## E · OTA ⭐ — 0/12 `░░░░░░░░░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | OTA-01 | [I] | Deploy pass toàn state machine | — | — |
| ⬜ | OTA-02 | [I] | Health fail → tự rollback | — | — |
| ⬜ | OTA-03 | [I] | Crash-loop → tự rollback | — | — |
| ⬜ | OTA-04 | [H] | Rút điện giữa DOWNLOADING | — | — |
| ⬜ | OTA-05 | [H] | Rút điện giữa SWITCHING | — | — |
| ⬜ | OTA-06 | [I] | Rút mạng giữa download | — | — |
| ⬜ | OTA-07 | [I] | Digest sai → không start | — | — |
| ⬜ | OTA-08 | [I] | Lệnh quá hạn → rejected | — | — |
| ⬜ | OTA-09 | [I] | Staged rollout dừng khi wave fail | — | — |
| ⬜ | OTA-10 | [I] | Deploy chồng → từ chối | — | — |
| ⬜ | OTA-11 | [H] | Disk đầy → fail sạch | — | — |
| ⬜ | OTA-12 | [H] | Ma trận Jetson+Pi đủ OTA-01→05 | — | — |

## F · Alert — 0/4 `░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | ALT-01 | [I] | Offline → notify ≤60s | — | — |
| ⬜ | ALT-02 | [I] | Raised/cleared không spam | — | — |
| ⬜ | ALT-03 | [I] | 50 robot offline → gộp tin | — | — |
| ⬜ | ALT-04 | [I] | Webhook chết → retry giới hạn | — | — |

## G · Terminal/log — 0/4 `░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | TRM-01 | [I] | PTY + audit log đầy đủ | — | — |
| ⬜ | TRM-02 | [I] | Viewer bị chặn terminal | — | — |
| ⬜ | TRM-03 | [I] | Rớt mạng → phiên đóng sạch | — | — |
| ⬜ | TRM-04 | [I] | Log tail tự tắt theo TTL | — | — |

## H · White-label/Installer — 0/4 `░░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | WLB-01 | [I] | Theming không cần rebuild | — | — |
| ⬜ | INS-01 | [H] | Người ngoài cài <30 phút | — | — |
| ⬜ | INS-02 | [I] | install.sh idempotent | — | — |
| ⬜ | INS-03 | [I] | Backup/restore Postgres | — | — |

## I · Tải & bền bỉ — 0/3 `░░░`

| | ID | Tầng | Mô tả | Lần cuối | Evidence |
|---|---|---|---|---|---|
| ⬜ | LOD-01 | [I] | 50 agent 72h không mất QoS1 | — | — |
| ⬜ | LOD-02 | [I] | Bão reconnect có backpressure | — | — |
| ⬜ | LOD-03 | [H] | 30 ngày fleet thật, 0 brick | — | — |
