# WORKLOG — FunkAtlas (append-only)

## 2026-07-14 · Lauf 1 (M0) · T0.1 „Gerüst + Gate"

- **Gebaut:** `pyproject.toml` (D4-Dependency-Set OHNE fritzconnection, per Go) ·
  `src/funkatlas/` (\_\_init\_\_ Version-Single-Truth, settings mit FUNKATLAS_-Prefix
  und env>dotenv>Default, config mit VEREINHEITLICHTEM Key-Merge, schema mit
  ensure_schema/WAL/busy_timeout/now_utc_iso/device_id-Spalten, gate mit 4 Schritten,
  \_\_main\_\_ CLI) · tools/ (task_runner mit COMMANDS→USAGE-Generierung, precommit_check,
  hooks/pre-commit, install_git_hooks.ps1) · funkatlas.cmd/.ps1 · .gitattributes ·
  .vscode/tasks.json · .github/workflows/ci.yml · .env.example · README ·
  tests (conftest mit Kill-Switch vor Import + tmp_db; unit: version/settings/config/
  gate_secrets/task_runner_usage; consistency: schema) · frische .secrets.baseline.
- **D5-Fixes in dieser Tranche (mit Regressionstest):** Config-Merge vereinheitlicht
  (Test `test_partial_yaml_keeps_unlisted_defaults` pinnt das Legacy-Silent-Drop-Verhalten
  als behoben) · `new_secrets` POSIX-pfadnormalisiert (Test
  `test_windows_and_posix_paths_are_equivalent`) · USAGE-Drift konstruktiv unmöglich
  (USAGE aus COMMANDS generiert + Test).
- **Red gesehen:** `test_malformed_yaml_yields_defaults` schlug zunächst fehl, weil der
  „kaputte" YAML-String gültiges YAML war (`{':': 'not yaml ::['}`) — Test auf echt
  malformiertes YAML korrigiert. Beweis, dass der Test etwas einschränkt.
- **Tests:** 18 passed (offline). **Gate:** GESAMT: PASS (compile · ruff-kritisch ·
  pytest · secret-scan). Hooks installiert (core.hooksPath → tools/hooks).
- **Entscheidungen/Parks:** Baseline-Falsch-Positiv (Plan-Doku Zeile 69) akzeptiert
  und in PROJECT_STATE dokumentiert. Keine Parks.

## 2026-07-14 · Lauf 1 (M0) · T0.2 „Minimal-Harvest: logsink + Collect-Kern"

- **Gebaut:** `logsink.py` (Harvest mit Device-Dimension: `logs/metrics/<device_id>/
  <domain>/<day>.jsonl`, append-only, kompakte sortierte Zeilen, ts_utc-Format-Guard
  NEU — Recon-Risiko „blinder ts[:10]-Slice" adressiert; Event-Partition nach eigenem
  event_ts; log_dir dynamisch über Settings-Modul-Attribut, NICHT import-gebunden —
  Legacy-Bug WORKLOG wlan:39) · `collect.py` (Runden-Kern: `_COLUMNS`-Registry als
  Single-Source, `register_domain` additiv mit Shape-Konflikt-Guard, `insert_raw`
  Versicherung, `twin_write` DB↔JSONL aus demselben Dict).
- **Tests:** logsink-Units (Partition, Pflichtfelder, Format-Guard, Append-Semantik,
  Event-Partition) · Konsistenz `logs == DB` gegen synthetische Domain (Registry-
  iterierend — neue Spalten automatisch abgedeckt) · raw-Roundtrip. 29 passed.
- **Gate:** GESAMT: PASS. **Parks:** keine.

## 2026-07-14 · Lauf 2 (M1) · T1.1 „wifi-status Probe"

- **Gebaut:** `probes/wifi_status.py` (netsh-Parser: Bytes-Disziplin ohne text=True,
  Decode-Kette utf-8→cp850→cp1252 — REALER Befund: Win11-Build liefert UTF-8, ältere
  CP850; DE/EN-Nadeln je Feld; „AP BSSID" vs „BSSID" per Suffix; Komma+Punkt-Dezimal;
  Ü-Mangling durch „bertragungsrate"-Substring umgangen) · Schema v2 additiv:
  `stg_wifi_status` + Index (SCHEMA_VERSION 1→2 beweist die additive Migration am
  lebenden Objekt) · Collector mit raw-Versicherung + twin_write je Interface.
- **Fixtures:** echte LaptopAndi-Aufnahme sanitisiert (E11): SSID→REDACTED_SSID,
  BSSIDs/MACs→aa:bb:cc:00:00:NN, GUID→0; UTF-8- UND CP850-Variante; synthetisches
  EN-Fixture; DE-disconnected. Live-Nebenbefund: B2 bestätigt (2,4 GHz/Kanal 6/59 %).
- **Tests:** Parser-Goldwerte DE/EN, CP850==UTF-8-Äquivalenz, disconnected-Degradation,
  Garbage→[], Collector-Integration (raw+stg+JSONL, logs==DB je Registry). 36 passed.
- **Parks:** keine.
