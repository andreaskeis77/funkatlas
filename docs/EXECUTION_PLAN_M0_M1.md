# Execution Plan — M0 (Projektfundament + Harvest) + M1 (Probe v0)

**Stand: 2026-07-14 · Plan v1 · Status: ZUR FREIGABE (Go/No-Go durch Andreas)**

> Erstellt nach `docs/EXECUTION_PLANNING_AND_GUARDRAILS.md` §2 im read-only Plan-Pass.
> Recon-Basis: Legacy-Repo `github.com/andreaskeis77/wlan` (Shallow-Clone, read-only gesichtet;
> 7 Bereiche parallel recon'd, jede Fundstelle adversarial gegen den Code verifiziert —
> 6/7 Bereiche ohne Beanstandung, 1 Nebensache korrigiert, siehe §12).
> Legacy-Pfade sind unten als `wlan:pfad:zeilen` notiert.

---

## 1. Ziel & Scope-Bezug

Adressiert **M0** („Projektfundament") und **M1** („Erste Messwerte") aus `docs/ROADMAP.md`.
Fachliche Referenz: `docs/GROBKONZEPT.md` §3 (Harvest), §4 (Architektur), §5 (Datenmodell).

- **M0:** Repo-Gerüst mit hermetischem Quality-Gate + Harvest der bewährten `wlan`-Bausteine (E2), Tests grün.
- **M1:** Probe v0 auf LaptopAndi: WLAN-Status (Client-Sicht) + Ping/Jitter/Loss + DNS, lokale Speicherung (SQLite + `logs/`), nacht-tauglich via Supervisor/Heartbeat.

**Nicht in Scope:** Ingest-API/Zentrale (M2), Dashboard (M3), Live-Calls an Router (M5 — E14-Verifikation), Netzwechsel-Runden (M6).

## 2. Abhängigkeitsgraph

```
T0.1 Gerüst+Gate ──► T0.2 Harvest FRITZ-Bausteine ──► T1.1 wifi-status Probe ──► T1.2 ping/dns+Runde ──► T1.3 Supervisor+Nachtlauf
```

Kritischer Pfad = die gesamte Kette (bewusst seriell, Begründung §4). T1.1/T1.2 wären
theoretisch parallelisierbar (verschiedene Probe-Module), teilen aber `_COLUMNS`-Registry,
Collect-Runden-Wiring und `conftest` — das Datei-Eigentum ist **nicht** disjunkt → seriell.

## 3. Parallele Fronten

**Keine Schreib-Fronten.** Parallel läuft nur Read-only-Arbeit:
- Recon (erledigt, Workflow mit 7 Recon- + 7 Verify-Agenten).
- **Review-Panel** nach T0.2 und nach T1.3: 3 read-only Subagenten (style / security / test-coverage) auf das jeweilige Diff.

## 4. Primitiv-Wahl (mit Begründung nach §3-Entscheidungsbaum)

| Arbeit | Primitiv | Begründung |
|---|---|---|
| T0.1–T1.3 Implementierung | **Single-Session-Kette** | Gekoppelte Schreibarbeit an einem Gerüst (ein Paket, geteilte Registry/conftest/Gate). Keine Front berührt Frozen Zone (die friert erst in M2 ein). Default-Neigung: billiger/sicherer. |
| Review nach T0.2 / T1.3 | **Subagenten-Panel (3, read-only)** | Read-heavy, unabhängige Lenses, kein Schreibkonflikt möglich. |
| Recon | Fan-out-Workflow (erledigt) | Breite + Unabhängigkeit + Prüfbarkeit gegeben. |

**Bewusst NICHT:** Worktree-Sessions oder Agent-Team für M0/M1 — zwei Fronten auf demselben
jungen Gerüst erzeugen nur Merge-Kosten ohne Zeitgewinn.

## 5. Rollen-Besetzung

- **implementer** = Haupt-Session (stärkstes Modell): baut Tranchen test-first.
- **Review-Panel** = 3 read-only Subagenten (style-, security-, test-coverage-Lens).
- Kein test-author ≠ implementer-Split in M0/M1: Der Harvest bringt die Tests des Legacy-Repos
  als externe, bereits geschriebene Spezifikation mit — die Writer≠Reviewer-Funktion erfüllt
  das Panel. (Ab M2, wenn neue Verträge entstehen, wird der Split eingeführt.)

## 6. Tranche-Schnitt & Reihenfolge

### M0 — Projektfundament + Harvest (2 Tranchen)

**T0.1 „Gerüst + Gate"** — Sicherheitsnetz zuerst, dann erst Harvest.
- `pyproject.toml` (Python 3.12, Deps → §D4), Paket `src/funkatlas/`, Version-Single-Truth.
- Task-Runner + `funkatlas.cmd`/`.ps1` (Venv-Auflösung, `wlan:tools/task_runner.py:1-67`, `wlan:wlan.ps1:1-7`).
- `gate.py` mit 4 Schritten: compileall · ruff-kritisch `E9,F63,F7,F82` · pytest offline (`-m 'not network'`) · Secret-Scan gegen frische Baseline (`wlan:src/wlan/gate.py:23-90`). **Live-Smoke bewusst erst ab M2** (es existiert noch kein Server) → §D3.
- Pre-Commit-Paar + Installer via `core.hooksPath` (`wlan:tools/hooks/pre-commit:1-12`, `wlan:tools/precommit_check.py:20-63`), `new_secrets` als Single-Source, **Pfad-Normalisierung `as_posix()`** (Fix der OS-Kopplung, `wlan:.secrets.baseline:126`).
- `.gitattributes` (LF, `.cmd/.ps1` CRLF), `.vscode/tasks.json`, CI `windows-latest` = exakt das lokale Gate (`wlan:.github/workflows/ci.yml:19-22`).
- `schema.py`-Harvest: `ensure_schema`-Muster + Migrations-Registry + WAL-`connect()` **+ neu: `PRAGMA busy_timeout`** (`wlan:src/wlan/schema.py:36-49, 52-63, 244-268`), `now_utc_iso` Zulu-Konvention (`wlan:src/wlan/schema.py:29-33`).
- `settings.py` (Prefix `FUNKATLAS_`, `repr=False` für Secrets, `reload_settings`, dotenv `override=False`; `wlan:src/wlan/settings.py:28-106`) + `config.py` (**vereinheitlicht: Key-Merge für alle Loader**, Fix von `wlan:src/wlan/config.py:52-60`).
- `tests/conftest.py`: `FUNKATLAS_DISABLE_DOTENV` **vor** erstem Import (ladungstragende Reihenfolge, `wlan:tests/conftest.py:14`), `tmp_db`-Fixture.
- `docs/PROJECT_STATE.md` v1 (Entscheidungslog E1–E15 übernommen) + `WORKLOG.md`.

**Maschinelle DoD T0.1:** `funkatlas.cmd gate` → `GESAMT: PASS` · Schema-Tests grün (alle Tabellen, Migration idempotent + einmal recorded, Zulu-Sortierbarkeit — Muster `wlan:tests/consistency/test_schema.py`) · `test_gate_secrets`-Semantik grün · CI grün auf Push.

**T0.2 „Harvest FRITZ-Bausteine"** — der eigentliche E2-Harvest, mit `device_id` ab Tag 1 (§D1).
- `fritz.py`: `Caller`-Protocol + `safe_call`/`is_error` (Fehler-als-Daten; 401 = Normalfall, `wlan:src/wlan/fritz.py:8, 19-84`) + `BoxClient`; **Adaption: explizite Per-Device-Konfiguration statt Settings-Singleton, TLS-Option (Port 49443, B8)**.
- `_util.py` komplett: `tenth_db`, `RSNI_NA=255→None`, `client_id` = `c_`+sha256(MAC)[:10] (`wlan:src/wlan/adapters/_util.py:14-59`).
- Adapter dsl/wan/wlan/box/mesh/eventlog (`wlan:src/wlan/adapters/*.py`) + `snapshot.py` (Redact/Flatten/Diff, `wlan:src/wlan/snapshot.py:19-113`; kuratierte Liste per Device-Typ parametrisiert).
- **Beim Harvest gefixt (test-first, §D5):** Eventlog-Zeitzone (Lokalzeit-als-Z-Bug, `wlan:src/wlan/adapters/eventlog.py:52`) · tote Byte-Raten-Placeholder-Spalten NICHT übernehmen (`wlan:src/wlan/adapters/wan.py:36-40`; Delta-Berechnung sauber in M5, additiv).
- `logsink.py` mit Device-Dimension: `logs/metrics/<device_id>/<domain>/<day>.jsonl`, `device_id` im Record (`wlan:src/wlan/logsink.py:21-60` + Risiko-Analyse Recon).
- `collect.py`-Muster: eine Runde = ein `ts_utc`, raw-Versicherung → stg → JSONL-Spiegel, Event-Idempotenz via `UNIQUE(event_key)` (`wlan:src/wlan/collect.py:22-188`); `device`-Hardcoding `'box'` ersetzt durch durchgereichte Identität (`wlan:src/wlan/collect.py:65` ff.).
- Fixtures übernehmen: `box_discovery/box_wan/repeater_discovery/speedtest.sanitized.json` + `FixtureCaller` (`wlan:tests/conftest.py:42-84`) + alle Unit-/Integrations-/Konsistenz-Tests als Regressionsanker.

**Maschinelle DoD T0.2:** alle geernteten Adapter-Contract-Tests grün gegen Fixtures (Goldwerte `wlan:tests/integration/test_adapters_p2.py`) · `logs == DB`-Test grün **mit device-Dimension** (Muster `wlan:tests/consistency/test_logs_equal_db.py:20-22`) · Eventlog-tz-Regressionstest grün · Gate PASS.

### M1 — Probe v0 (3 Tranchen)

**T1.1 „wifi-status Probe" (Neubau, kein Harvest)** — Client-Sicht des WLAN-Interfaces.
- Parser für `netsh wlan show interfaces` → SSID/BSSID/Band/Kanal/Signal%/Link-Rate; **Bytes-Disziplin wie beim Ping** (nie `text=True` — OEM-Codepage!), Fixtures Deutsch + Englisch, aufgenommen auf LaptopAndi.
- Neue Tabelle `stg_wifi_status` (additiv via `ensure_schema`) + JSONL-Domain `wifi_status`; BSSID pseudonymisiert analog `client_id` — **eigene BSSID des Verbunds bleibt lokal zuordenbar** über `config/` (nicht `devices.yaml`-pflichtig, keine Fremd-PII).

**Maschinelle DoD T1.1:** Parser-Unit-Tests grün (DE + EN, getrenntes Interface degradiert zu `None`-Feldern statt Crash) · Collect-Runde schreibt stg + JSONL · `logs == DB` grün für die neue Domain.

**T1.2 „ping/dns + Messrunde"** — Harvest + kleiner Neubau.
- `ping.py`-Harvest unverändert im Kern: Bytes-Runner, `_TIME_RE` (Zeit=/time=, `<1ms`, Komma-Dezimal), Jitter/Loss-Mathematik (`wlan:src/wlan/probes/ping.py:20-53`); **Fix des Config-Drifts:** Targets aus `config/probes.yaml` statt hartcodiert (`wlan:src/wlan/probes/ping.py:56-66` ignoriert die YAML heute).
- DNS-Probe (Neubau, klein): Resolve-Zeit via injizierbarem Resolver (hermetisch testbar).
- `collect_probe_once`: eine Runde = ein `ts_utc` + `device_id` (LaptopAndi), alle Probe-Domains.

**Maschinelle DoD T1.2:** geerntete Ping-Parse-Regressionstests grün (inkl. cp1252/100%-Loss-Guard) · DNS-Probe hermetisch grün · Runden-Test grün (Muster `wlan:tests/integration/test_collect_once.py`) · `logs == DB` grün.

**T1.3 „Supervisor + Nachtlauf-Tauglichkeit"** — Harvest + Lückenschluss.
- Supervisor-Harvest: `_safe`-Wrapper (nie raisen, **Heartbeat im finally** — Liveness beweisbar auch bei Fehlern, `wlan:src/wlan/supervisor.py:62-80`) · APScheduler-3.x-Rezept `max_workers=1`, `coalesce=True`, `max_instances=1`, `misfire_grace_time=30` (Laptop-Sleep/Wake!, `wlan:src/wlan/supervisor.py:126-133`) · Heartbeat-Tabelle **+ device_id**.
- CLI `python -m funkatlas probe [--max-runtime]`, headless (kein Tray — Probe-Knoten brauchen keinen, `wlan:src/wlan/desktop.py` bleibt draußen).
- **Neuer Test, der die Legacy-Lücke schließt:** bounded `run(max_runtime=2)`-Integrationstest (Legacy hatte keinen Test für `run()` selbst).
- `ops/autostart_install.ps1`-Harvest (Scheduled Task, RestartCount 3) + `docs/RUNBOOK.md` v1 mit **Energieprofil-Checkliste (E9, Owner-Handgriff)**; Heartbeat-Lücken per einfacher Abfrage sichtbar.

**Maschinelle DoD T1.3:** Supervisor-Integrationstests grün (Jobs schreiben Daten + Heartbeat; Fehler heartbeatet trotzdem; bounded run) · Gate PASS am Ende = M1-Code fertig.
**Operative Abnahme M1 (Owner, nicht maschinell):** eine Nacht Messreihe auf LaptopAndi liegt vor (ROADMAP-Kriterium) — Probe abends starten, morgens Heartbeat-Lücken + Daten prüfen.

## 7. Run-Sizing

| Lauf | Inhalt | Größe | Nacht-tauglich |
|---|---|---|---|
| Lauf 1 | T0.1 + T0.2 (M0 komplett) | 1-h- bis Mehr-h-Lauf | ja (keine Checkpoints, rein additiv, hermetisch) |
| Lauf 2 | T1.1 + T1.2 + T1.3 (M1 komplett) | Mehr-h-/Nacht-Lauf | ja |

Pro Tranche ein Commit (Conventional Commits, `T-…`-Präfix). Session-/Kosten-Limits sind real
(im Recon-Lauf einmal getroffen): Jeder Abbruch landet dank Tranchen-Commits + WORKLOG auf
einem sauberen, fortsetzbaren Stand; bei Kontext-Knappheit → letzte fertige Tranche + HANDBACK.

## 8. Guardrail-Bindung

| Guardrail | Bindung in M0/M1 |
|---|---|
| **Router strikt read-only (nur `Get*`)** | Geernteter Code ruft ausschließlich `Get*` (verifiziert: `wlan:src/wlan/fritz.py:5` „Strictly read-only: only ``Get*`` actions are ever issued" + alle SOURCES-Maps). In M0/M1 finden **überhaupt keine** Router-Calls statt — alles läuft gegen Fixtures. |
| **Merge-Gate hermetisch** | `addopts = "-m 'not network' -q"` (Muster `wlan:pyproject.toml:47`) — auch ein nacktes `pytest` ist offline. Echte Calls nur unter `network`-Marker (M5+, bewusster Schritt). `FUNKATLAS_DISABLE_DOTENV` vor jedem Test-Import. |
| **Explizite Adds** | `git add <pfad>` je Tranche; nie `-A`. Pre-Commit-Hook aktiv ab T0.1. |
| **Keine Secrets/PII** | Secret-Scan im Gate + Pre-Commit (Baseline frisch, UTF-8 ohne BOM — PowerShell-`>`-Gotcha `wlan:WORKLOG.md:122`). Fixtures nur sanitisiert. MAC/IP nie im Klartext persistieren (`client_id`-Hashing). `.env` gitignored, `.env.example` dokumentiert Least-Privilege-TR-064-User. |
| **`config/devices.yaml` nie committen** | Bereits in `.gitignore` (Initial-Commit). In M0/M1 wird die Datei noch gar nicht angelegt — die Klartext-Registry kommt erst mit M5 (Geräte-Detektiv). Probe-Identität (`device_id`) ist Pseudonym-frei konfiguriert und kein PII. |
| Kein Live-DB-Write | Es existiert noch keine Live-DB. Tests ausschließlich tmp-DB. Der Nachtlauf schreibt betriebsgemäß nach `data/` (gitignored). |
| Kosten-Cap | Richtwert je Lauf: ~1,5 M Output-Tokens; am Cap/Session-Limit: sauber stoppen nach letzter fertiger Tranche + HANDBACK. |
| Lauf endet auf `main` | M0/M1 sind additiv auf jungem Repo; Arbeit direkt auf `main` mit Tranchen-Commits ist hier vertretbar (Single-Owner, kein Prod). Ab M2 (Frozen Zone) Feature-Branches + Gate-Merge. |

## 9. Kostenschätzung

- **Geld:** 0 € — keine bezahlten APIs, kein Datenvolumen (Kreis B unberührt; alles lokal/Fixtures).
- **Tokens (Richtwert):** M0 ≈ 0,5–1,5 M · M1 ≈ 1–2 M. (Recon hat ~0,74 M verbraucht.)
- **Owner-Zeit:** Go/No-Go jetzt · nach M1 einmal Probe über Nacht laufen lassen + Energieoptionen setzen (Runbook-Checkliste).

## 10. Checkpoints & Park-Punkte

- **Checkpoint (Mensch):** nur dieses Go/No-Go. M0/M1 haben laut ROADMAP keine weiteren Checkpoints.
- **Park-Punkte (parken statt raten):**
  - Vorgriffe auf den Ingest-API-Contract (M2-Frozen-Zone) — nichts einfrieren, nichts „schon mal designen".
  - Rotes Gate ohne klaren additiven Fix.
  - Echte `netsh`-Ausgabe weicht strukturell von den Fixtures ab und der Parser bräuchte eine Design-Entscheidung (z. B. mehrere Interfaces gleichzeitig).
  - Jede Versuchung, einen Router live anzusprechen (auch „nur kurz testen") → E14-Verifikation ist ein M5-Schritt.

## 11. Definition of Done (maschinell, je Lauf)

- **M0 fertig:** `funkatlas.cmd gate` → `GESAMT: PASS` · alle geernteten Tests grün (Unit + Integration + Konsistenz inkl. `logs == DB` und Schema-Idempotenz) · CI grün · ROADMAP/PROJECT_STATE im selben Block fortgeschrieben.
- **M1 code-fertig:** zusätzlich wifi-status-/ping-/dns-/Supervisor-Tests grün inkl. bounded-run · Gate PASS.
- **M1 abgeschlossen (ROADMAP):** + eine Nacht Messreihe (operative Abnahme durch Andreas).

## 12. Harvest-Inventar (Recon-Belege, verifiziert)

Verifikation: je Bereich ein adversarialer Zitat-Check gegen den Clone. Ergebnis: fritz-adapters,
logsink-report, supervisor-scheduler, taskrunner-gate-ci, fixtures-probes-analyze, docs-gotchas
= alle Zitate bestätigt; schema-storage = 1 Korrektur (mart_*-Verbleib: als „bewusst
zurückgestellt" dokumentiert in `wlan:docs/HANDBACK.md:36`, nicht in der ROADMAP — die
mart-Schicht hat **null Code**, es gibt dort nichts zu ernten).

| Baustein | Kern-Belege (Legacy) | Übernahme |
|---|---|---|
| TR-064-Grenze: `Caller`-Protocol, `safe_call` (Fehler-als-Daten), `BoxClient` | `fritz.py:19-84`; 401=Normalfall `fritz.py:8` | as-is + Per-Device-Config, TLS-Option |
| Einheiten-Kit: `tenth_db`, RSNI-255-Sentinel, `client_id`-Hash | `adapters/_util.py:14-59` | as-is |
| Adapter dsl/wan/wlan/box/mesh/eventlog | `adapters/dsl.py:18-49`, `wan.py:10-41`, `wlan.py:12-49`, `box.py:13-33`, `mesh.py:16-77`, `eventlog.py:20-87` | as-is + device_id; eventlog-tz-Fix; Byte-Raten-Stubs raus |
| Settings-Snapshot + Redact + Diff | `snapshot.py:19-113` | as-is, kuratierte Liste per Device-Typ |
| Collect-Orchestrierung (ein ts/Runde, raw-Versicherung, Event-Idempotenz) | `collect.py:22-188` | Muster as-is, Device-Identität durchreichen |
| Schema: `ensure_schema`, WAL, Zulu-`ts_utc`, Migrations-Registry | `schema.py:29-33, 36-49, 52-63, 244-268` | as-is + `busy_timeout` + device_id-Spalten |
| Settings/Config: env>dotenv>Default, `repr=False`, Reload | `settings.py:28-106`, `config.py:36-60` | as-is, `FUNKATLAS_`-Prefix, Merge vereinheitlicht |
| logsink: JSONL append-only, Tages-Partition | `logsink.py:21-60` | as-is + `<device_id>`-Pfadebene |
| Report/Summary-Muster (TEXT==DB via ein Read-Model) | `analyze/summary.py:43-77`, `report.py:26-67` | Muster ja; per-Device-Generalisierung erst M3 |
| Thresholds: `evaluate`/`worst` richtungs-bewusst | `analyze/thresholds.py:13-37`; Grenzwert-Semantik warn strikt `>`! | as-is (Grenz-Semantik exakt erhalten) |
| Supervisor: `_safe`+Heartbeat-im-finally, 1-Writer-Executor, Sleep/Wake-Defaults | `supervisor.py:62-80, 126-133` | as-is + device_id; bounded-run-Test neu |
| Gate/Task-Runner/Hooks/CI/Wrapper | `gate.py:23-135`, `tools/*`, `ci.yml` | as-is; Smoke erst M2; Baseline-Pfade posix |
| Ping-Probe (Bytes, DE/EN, `<1ms`, Komma) | `probes/ping.py:20-53`; „teuerster Bug" `ping.py:5` | as-is; Targets aus Config (Drift-Fix) |
| Fixtures (sanitisiert) + `FixtureCaller` | `tests/conftest.py:42-84`, `tests/fixtures/*` | as-is (Regressionsanker); Repeater-Fixture = Degradations-Vorbild für 6850/M3 |
| GOTCHA-Kanon + Einheiten-Tabelle | `CLAUDE.md:32-36`, `docs/DATENSTRATEGIE.md:21-39` | in PROJECT_STATE/CLAUDE.md übernommen (erledigt) |

**Alle sechs Grobkonzept-GOTCHAs code-verifiziert:** Signal=Prozent (`DATENSTRATEGIE.md:30`,
`schema.py:176` `signal_pct`) · 0,1-dB (`_util.py:39`) · kbit/s-Sync (`dsl.py:8`) ·
Byte-Rate nur aus Delta — **nie implementiert, Spalten immer None** (`wan.py:36`,
`HANDBACK.md:35`) · Repeater-401→Mesh-via-Box (`fritz.py:8`, `PROJECT_STATE.md:29`) ·
ping nie `text=True` (`ping.py:5`).

**Geerbter Backlog (bewusst NICHT M0/M1):** Live-Verifikation echte Box (→ M5, E14) ·
Byte-Raten-Delta + Public-IP-Hash (→ M5) · Per-Client-Signal, PII-schwer (→ M5, mit E11-Registry) ·
Speedtest-Probe (Fixture existiert; → M4 mit Budget-Wächter) · marts (→ M3/M4) · Backup+Restore-Probe (→ M2/M3).

## 13. Entscheidungen im Plan (bitte im Go bestätigen oder kippen)

- **D1 · device_id ab Tag 1** in Schema, JSONL-Records und `logs/`-Pfaden (`logs/metrics/<device_id>/<domain>/<day>.jsonl`). Grund: Layout + Feldnamen werden in M2 Frozen Zone — die Dimension **jetzt** einziehen ist additiv, später ist es ein Breaking Change. Korrelation über `(device_id, ts_utc)`; ein `run_id` erst bei realem Bedarf (YAGNI).
- **D2 · Voll-Harvest in M0** (alle sechs Adapter + Snapshot), obwohl die Probe sie erst ab M5 live nutzt. Grund: Tests existieren als Sicherheitsnetz, GOTCHAs wandern in einem kohärenten Port mit. *Billigere Alternative:* Minimal-Harvest (nur schema/logsink/gate/supervisor/ping, ≈ 40 % weniger M0-Umfang), Adapter erst in M5 — Preis: doppeltes Einarbeiten, Drift-Risiko. **Empfehlung: Voll-Harvest.**
- **D3 · Gate v0 ohne Live-Smoke-Schritt** — es gibt bis M2 keinen Server. Der Smoke kommt in M2 zurück (Ingest-API gegen tmp-DB booten + eine synthetische Messung durchschieben).
- **D4 · Dependency-Set M0/M1 (Hard-Stop „neue Dependency" — hiermit zur Freigabe):** Runtime `pyyaml`, `python-dotenv`, `APScheduler>=3.10,<4` (Pin ist ladungstragend), `fritzconnection>=1.14` (lazy importiert; Fixture-Tests brauchen es nicht). Dev: `pytest`, `ruff`, `detect-secrets`. **Nicht** in M0/M1: fastapi/uvicorn/httpx (M2), pystray/pillow (Tray unnötig für Probe-Knoten), pyinstaller (später).
- **D5 · Legacy-Bugs beim Harvest test-first fixen:** Eventlog-Zeitzone · Byte-Raten-Stubs entfernen · Config-Merge vereinheitlichen · Baseline-Pfad-Normalisierung · `probes.yaml`-Target-Drift. Alles klein, alles mit Regressionstest.
- **D6 · wifi-status via `netsh`-Parsing** (nicht Win32-WLAN-API): einfacher, fixture-testbar, DE/EN-robust machbar; Format-Drift-Risiko dokumentiert. Native API bleibt Option, falls `netsh` sich als zu wackelig erweist (dann Park + Entscheidung).

## 14. Challenge (aktiv, wie angefordert)

**Wo der Plan angreifbar ist:**
1. **Ist der Voll-Harvest (D2) YAGNI-widrig?** Ehrliche Antwort: teilweise. Mesh/Eventlog/Snapshot liegen bis M5 brach. Ich empfehle ihn trotzdem — die Ernte ist durch existierende Tests fast risikofrei und E2 nennt genau diese Bausteine. Wer M0 schlanker will, streicht Adapter+Snapshot aus T0.2 (Minimal-Variante in D2).
2. **device_id (D1) ist ein Vorgriff auf M2.** Stimmt — aber ein bewusster: Die Alternative (Single-Device-Layout jetzt, Breaking Change beim Einfrieren in M2) widerspricht „additiv vor invasiv" direkter. Das ist die eine Design-Entscheidung, die ich nicht parken kann, ohne M2 teurer zu machen.
3. **APScheduler behalten oder 30-Zeilen-Loop?** Recon zeigt: Die Nutzung ist simpel genug für einen Eigenbau. Ich behalte APScheduler, weil `coalesce/max_instances/misfire_grace_time` exakt das Laptop-Sleep/Wake-Szenario der Nachtmessungen (E9) abdecken — das selbst nachzubauen ist verstecktes Risiko, keine Ersparnis.
4. **Größte reale Risiken:** (a) Windows-Energieverwaltung unterbricht Nachtmessungen — mitigiert durch Runbook-Checkliste (Owner) + Heartbeat-Lücken sichtbar; (b) `netsh`-Ausgabeformat variiert je Windows-Build/Sprache — mitigiert durch Bytes-Parsing + Fixtures beider Sprachen + Park-Regel; (c) Session-/Kostenlimits mitten im Lauf (im Recon real passiert) — mitigiert durch Tranchen-Commits + HANDBACK-Disziplin.
5. **Was NICHT parallelisiert wird (und warum das richtig ist):** die gesamte Implementierung. M0/M1 sind ein zusammenhängendes Gerüst mit geteiltem Datei-Eigentum (Registry, conftest, Gate). Parallelität würde hier nur Merge-Konflikte kaufen. Parallel bleibt ausschließlich Read-only (Recon erledigt, Review-Panels geplant).
6. **Bewusst verschoben, nicht vergessen:** Ingest-Contract-Design (M2, mit frischem Kopf und diesem Plan als Basis) · Live-TR-064-Verifikation E14 (M5, erster echter Netz-Schritt) · Speedtest/Budget-Wächter (M4, Geld-Nähe = eigener Checkpoint).

## 15. Freigabe

**Go:** ☐ Andreas · Datum: ____ · Plan v1 · Kosten-Rahmen §9 akzeptiert · D1–D6 bestätigt/angepasst: ____

Bei substanzieller Plan-Änderung im Lauf: parken + Re-Approval (kein stilles Abweichen).

---

## Änderungslog

- **v1 (2026-07-14):** Erstfassung nach Recon (7 Bereiche, adversarial verifiziert) — zur Freigabe.
