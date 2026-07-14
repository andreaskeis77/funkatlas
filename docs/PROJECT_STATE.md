# PROJECT_STATE — FunkAtlas

**Kanonischer Stand + Entscheidungslog. Fortgeschrieben, nie weggeworfen.**

## Produkt (ein Absatz)

FunkAtlas ist die private Multi-Netz-WLAN-Analyseplattform für das Haus Keis:
Probes auf LaptopAndi und Dell (später Android) messen dauerhaft beide
Netz-Kreise (A: Telekom-DSL/7590+Repeater · B: congstar-5G/Netgear M3 + 6850
als Client); eine Zentrale sammelt, korreliert mit der Router-Innensicht und
verifiziert Optimierungen per Vorher/Nachher-Experiment. Nachfolger von
`wlan` (Harvest, kein Fork).

## Entscheidungslog

- **E1–E15:** fixiert in `docs/GROBKONZEPT.md` §1 (Interview-Runde 1, 2026-07-13).
- **E16 (2026-07-14, Andreas — Go Execution Plan M0+M1 v2):** D1 device_id ab
  Tag 1 · **D2 minimal** — TR-064-Adapter-Harvest erst M5 · D3 Gate ohne
  Live-Smoke bis M2 · **D4 ohne fritzconnection** (Antrag mit M5) · D5-Fixes
  anteilig beim jeweiligen Harvest (Eventlog-tz-Fix → M5) · D6 wifi-status via
  netsh · E9-Energieprofil-Checkliste vor erstem Nachtlauf zum Abhaken.
  Referenz: `docs/EXECUTION_PLAN_M0_M1.md` §15.

## Stand

- **M0 ✅ (2026-07-14):** T0.1 Gerüst + Gate (Paket, Task-Runner, Hooks, CI,
  hermetische Testbasis) · T0.2 Minimal-Harvest (logsink mit device_id,
  Collect-Kern, logs==DB-Maschinerie) · Review-Panel (3 Lenses, 20 Findings)
  ausgewertet, alle Major/Minor gefixt oder bewusst dokumentiert. 66 Tests,
  Gate `GESAMT: PASS`, CI grün.
- **M1 🔨 (Lauf 2):** T1.1 wifi-status ✅ (netsh-Parser DE/EN, Bytes-Disziplin,
  Schema v2) · T1.2 ping/dns + Messrunde ✅ (Schema v3, ein ts je Runde) ·
  T1.3 Supervisor/Nachtlauf: in Arbeit.

## Bekannte Verstöße / GOTCHAs (Ist ≠ Ziel, ehrlich)

- Kein Live-Smoke-Schritt im Gate bis M2 (bewusst, D3).
- TR-064-Zugang 7590 unverifiziert (E14 → M5). Legacy wurde NIE live gegen die
  echte Box verifiziert — alle „verified units" stammen aus Recorded-Fixtures.
- Geerbte Domänen-GOTCHAs: siehe CLAUDE.md PROJEKT-Block (Signal=Prozent,
  0,1-dB, kbit/s, TotalBytes-Delta, Repeater-401, ping nie `text=True`).
- Baseline-Befund `docs/EXECUTION_PLAN_M0_M1.md:69` = Falsch-Positiv
  (Keyword-Detektor auf Doku-Prosa), bewusst in `.secrets.baseline` akzeptiert;
  zwei `pragma: allowlist secret` in Tests (Testdaten-Literale).
- `mart_*`-Schicht (Medallion) existiert noch nicht — kommt mit M3/M4.
- Pre-Commit scannt Working-Tree-Inhalte, nicht Staged-Blobs (Gate + CI sind
  der Backstop; Härtung via `git show :<path>` = Backlog).
- CI installiert ungepinnte Deps (Lockfile/Constraints = Backlog); Token ist
  auf `contents: read` beschränkt.
