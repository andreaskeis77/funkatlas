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

## 2026-07-14 · Lauf 2 (M1) · T1.2 „ping/dns + Messrunde"

- **Gebaut:** `probes/ping.py` (Harvest: Bytes-Regex Zeit=/time=/`<1ms`/Komma-Dezimal,
  Jitter/Loss-Mathematik; D5-Fix: Targets/count/timeout aus `config.probes()` statt
  hartcodiert — count wird in Command UND parse durchgereicht) · `probes/dns.py`
  (Resolve-Timing, injizierbarer Resolver+Timer, degradiert bei OSError) ·
  `probes/round.py` (`collect_probe_once`: ein ts je Runde, ein Commit) ·
  Schema v3 additiv: `stg_ping` + `stg_dns` + Indizes · `config/probes.yaml` +
  `DEFAULT_PROBES` in config.py (Key-Merge).
- **Tests:** Ping-Regressionen (cp1252-Umlaut-Bytes, Zeitüberschreitung→100 %,
  Partial-Loss, mehr Matches als count) · DNS ok/fail hermetisch · volle Runde
  (ein ts über alle Domains, JSONL je Domain, logs==DB für ping). 47 passed.
- **Parks:** keine.

## 2026-07-14 · Review-Panel M0 (3 Lenses, 20 Findings) → Fixes

- **Major gefixt (je mit Regressionstest):** Gate-Secret-Scan war fail-open bei
  Git-Fehler (leere Liste → PASS) → `_git_files` prüft returncode, None → FAIL ·
  Nicht-ASCII-Dateinamen entkamen dem Scan (Octal-Quoting) → `-z`/NUL-Splitting in
  Gate UND Pre-Commit · `twin_write` konnte logs==DB still brechen (unregistrierte/
  reservierte Keys nur im JSONL) → `insert_stg` rejektiert · `event_ts` floss
  unvalidiert in Dateinamen → `_day_from_ts`-Validierung · Pfad-Traversal über
  `device_id`/`domain`/`kind` → Slug-Validierung in logsink · Default-`device_id`
  war Hostname (oft PII!) → `dev-`+sha256[:8]-Digest · SQL-Identifier-Grenze in
  `register_domain` erzwungen (Injection-Guard).
- **Minor gefixt:** `_run` mit encoding=utf-8/replace (Gate+Hook stürzen nie an
  cp1252) · task_runner pinnt cwd=REPO_ROOT + Exit-Code-Passthrough-Test ·
  tmp_db-Teardown: monkeypatch.undo() VOR reload_settings (Stale-Singleton-Falle) ·
  CI permissions: contents:read · Pre-Commit ACMR statt ACM.
- **Neue Test-Abdeckung (Panel-Lens 3):** gate.main-Aggregation (später PASS darf
  FAIL nicht überschreiben) · step_secret_scan-Verdrahtung (BOM-Baseline, Baseline-
  Ausschluss, git-Fehler→FAIL) · precommit_check komplett (frisches Secret→1,
  ruff nur auf .py, git-Fehler→1).
- **Bewusst NICHT gefixt (dokumentiert):** Pre-Commit scannt Working-Tree statt
  Staged-Blobs (Gate+CI sind Backstop; Materialisierung via `git show :` = spätere
  Härtung) · CI-Dependency-Pinning (Lockfile) → Backlog.
- **Stand:** 66 Tests grün, Gate GESAMT: PASS.

## 2026-07-14 · Lauf 2 (M1) · T1.3 „Supervisor + Nachtlauf-Tauglichkeit"

- **Gebaut:** `supervisor.py` (Harvest: `_safe` nie-raisen + Heartbeat-im-finally
  mit device_id, APScheduler-3.x-Rezept max_workers=1/coalesce/max_instances=1/
  misfire_grace_time=30 für Laptop-Sleep/Wake, injizierbare conn_factory/cfg/runner) ·
  `status.py` (Heartbeat-Lücken-Report + letzte Messrunde, ASCII-safe für OEM-Konsole) ·
  CLI `python -m funkatlas probe [--once|--max-runtime]` + `heartbeat` · task_runner-
  Kommandos probe/probe-once/heartbeat · `config/scheduler.yaml` (60 s, leichte Taktung) ·
  `ops/autostart_install.ps1` (Scheduled Task, RestartCount 3, -Remove) ·
  `docs/RUNBOOK.md` v1 inkl. **E9-Energieprofil-Checkliste** (7 Punkte zum Abhaken).
- **Tests:** job_probe schreibt Daten+Heartbeat · _safe heartbeatet auch bei Fehler ·
  **bounded run(max_runtime=2.5) terminiert und misst** (schließt die Legacy-Lücke:
  run() war dort ungetestet) · Heartbeat-Gap-Mathematik (7140-s-Lücke erkannt) ·
  Report-Inhalte. 73 passed, Gate GESAMT: PASS.
- **Live-Smoke (bewusst, außerhalb des Gates):** `probe-once` auf LaptopAndi →
  {wifi_status: 1, ping: 2, dns: 1} unter device_id `laptopandi` (lokale .env);
  Smoke-Daten vor Produktivstart zurückgesetzt. Keine Router-Calls.
- **Parks:** keine.

## 2026-07-14 · Review-Panel M1, Teil 1 (test-coverage-Lens, 5 Findings) → Fixes

- **Design-Fix (Major-Finding an der Wurzel behoben statt Divergenz zu pinnen):**
  Teilausfall einer Runde konnte logs≠DB erzeugen (JSONL geschrieben, DB-Rollback).
  Neu: Messwerte = unabhängige Fakten — `insert_raw` committet sofort (Beweiszweck!),
  `twin_write` committet je Zeile VOR dem JSONL-Append, `collect_probe_once`
  isoliert Domains (anmutige Entartung: eine kaputte Probe killt weder Runde noch
  Geschwister; `errors`-Map im Summary). Test pinnt: ping-OSError → wifi/dns-Zeilen
  in DB UND JSONL identisch, ping nirgends, raw-Versicherung überlebt.
- **Neue Tests (Rest der Findings):** __main__-Dispatch (--once/--max-runtime-
  Forwarding, heartbeat, version) · Zwei-Interface-Isolation im netsh-Parser ·
  conn_factory-Doppelfehler entkommt _safe nicht (caplog: job+heartbeat warning) ·
  Heartbeat-Fensterfilter (25-h-alter Stempel zählt nicht).
- **Stand:** 80 Tests grün, Gate GESAMT: PASS. Security/Correctness-Lens laufen
  nach (Session-Limit im ersten Anlauf), Findings folgen.
