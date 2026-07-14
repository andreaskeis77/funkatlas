# CLAUDE.md — Operative Verfassung

Diese Datei wird von Claude Code beim Session-Start automatisch geladen. Sie ist bewusst **kurz** (Ziel < 200 Zeilen): nur *operative Direktiven* + projekt-spezifische Fakten. Die **ausführliche Methodik liegt in `docs/`** und wird **bei Bedarf** gelesen — Karte: `docs/INDEX.md`. Die Detail-Dokumente werden hier **nicht importiert** (das würde jeden Session-Kontext belasten).

**Durchsetzung:** Diese Datei *lenkt* Verhalten (Kontext, kein Zwang). Harte Grenzen werden über **Hooks/Gates** erzwungen, nicht über diesen Text.

**Hierarchie der Wahrheit (bei Widerspruch):** Repo-/Live-Zustand > `docs/`-Referenz > diese Datei. Bei Unklarheit: **fragen statt raten.**

---

## PROJEKT — FunkAtlas
- **Produkt (ein Absatz):** FunkAtlas ist die private Multi-Netz-WLAN-Analyseplattform für das Haus Keis: Mess-Probes auf LaptopAndi und Dell (später Android) erfassen dauerhaft Signal, Band, AP/BSSID, Ping/Jitter/DNS und Roaming-Events in beiden Netz-Kreisen (A: Telekom-DSL/FRITZ!Box 7590 + Repeater 3000 AX · B: congstar-5G/Netgear M3 + FRITZ!Box 6850 als Client); eine Zentrale auf LaptopAndi sammelt, korreliert mit der Router-Innensicht und beantwortet: Wo hakt es, warum, und hat eine Optimierung *messbar* etwas gebracht (Experiment-Schleife E7). Nachfolger des Legacy-Projekts `wlan` (Harvest, kein Fork — E2/E15).
- **Stack / Topologie:** Python 3.12 · SQLite/WAL (Medallion raw→stg→mart, EIN DB-Writer) · FastAPI (Ingest-API, nur LAN, Token) · APScheduler · server-rendered Dashboard · **kein Docker** (E3: Probe braucht natives WLAN-Interface). Windows (LaptopAndi = Dev + Probe + Zentrale; Dell = Probe). Kein Cloud-Hosting — alles bleibt im Haus.
- **Öffentliche Endpunkte / Health:** keine öffentlichen — Ingest/Dashboard binden nur ins LAN, Token-Auth, kein Inbound aus dem Internet. Health/Status-Seite ab M3 (`product-state.json` als Quelle der Projekt-Seite).
- **Standard-Befehle:** `funkatlas.cmd gate` (Merge-Gate: compile · ruff-kritisch · pytest offline · secret-scan) · `funkatlas.cmd test` / `test-unit` / `test-integration` / `test-consistency` · `funkatlas.cmd version`. Hooks: `tools\install_git_hooks.ps1` (einmalig).
- **Entscheidungslog:** E1–E15 in `docs/GROBKONZEPT.md` §1; Fortschreibung in `docs/PROJECT_STATE.md` (entsteht in M0).
- **Bekannte Verstöße / GOTCHAs (Ist ≠ Ziel):** Projekt in Konzept-Phase — noch kein Gate, keine Tests, kein PROJECT_STATE (alles M0). TR-064-Zugang zur 7590 unverifiziert (E14 — erster Live-Schritt in M5). Netgear-M3-Schnittstelle undokumentiert (M7-Spike). Geerbte Domänen-GOTCHAs: TR-064-`SignalStrength` = **Prozent, nicht dBm** · Dämpfung/SNR in 0,1-dB-Einheiten · DSL-Syncraten in kbit/s · Byteraten nur aus TotalBytes-Delta ableiten · Repeater-TR-064 antwortet 401 → Mesh-Sicht über die Box · Windows-`ping` via subprocess **nie `text=True`** (OEM-Codepage).

### EISERNE PROJEKT-REGELN (aus E1–E15)
- **Router strikt read-only:** ausschließlich `Get*`-Aufrufe auf 7590/6850/M3 — nie Konfiguration schreiben (E8). Änderungen setzt der Mensch um; das System misst.
- **Netzwechsel der Probe nur als geplante, protokollierte Messrunde** mit Standort-Tag und Rückkehr-Garantie (E8) — nie als stiller Nebeneffekt.
- **Klartext-Geräte-Registry `config/devices.yaml` bleibt lokal** (gitignored, E11); Repo/Fixtures/Log-Beispiele pseudonymisiert.
- **Merge-Gate hermetisch:** offline gegen sanitisierte Fixtures, auch wenn Router erreichbar sind; echte Calls nur unter `network`-Marker (bewusster separater Live-Smoke).
- **Speedtest-Budget-Wächter:** Kreis B hat 160 GB/Monat (E10); Messbudget Default 8 GB/Monat, konfigurierbar — hartes Stopp-Verhalten, kein Weichspülen.
- **Frozen Zone (nur additiv, ab Einfrierung):** Ingest-API-Contract Probe→Core · `logs/`-Layout + JSONL-Feldnamen · Threshold-/Metrik-Taxonomie · `product-state.json`-Schema.

### REPORTING-REGEL (E13)
Owner-Kommunikation (Andreas) immer in **Meilenstein-/Feature-Sprache** mit Bezug auf `docs/ROADMAP.md`; Technik-Detail nur auf Nachfrage. Antwort auf „Wo stehen wir?" hat genau drei Teile: **(1) zuletzt fertig · (2) in Arbeit · (3) als Nächstes.** `docs/ROADMAP.md` wird **im selben Arbeitsblock** fortgeschrieben, in dem Meilenstein-Fortschritt passiert — sonst gilt die Änderung als unvollständig.

---

## EISERNE REGELN (nicht verhandelbar) — YOU MUST
- **Gates nie aufweichen**, um Tempo zu machen. Rot = Stopp, Ursache zuerst. Nie `--no-verify`.
- **Verifizierbar statt vertrauensselig:** nichts gilt fertig, weil es plausibel aussieht — erst wenn ein Test es gegen die Wahrheit prüft.
- **In Prod/Live nur über den Deploy-Pfad** — nie von Hand.
- **Explizite Adds** (`git add <pfad>`), **NIE `git add -A`**. **Keine Secrets/PII** committen; Token nie zitieren.
- **Frozen Zone unberührt** (Mehrkonsumenten-Verträge/API/geteilte Taxonomie): nur additiv; Breaking Change = bewusst versioniert (neue API-Version).
- **Additiv vor invasiv.** Doku **im selben Arbeitsblock** aktualisieren (sonst gilt die Änderung als unvollständig).
- **Test-First:** erst Test schreiben, ihn **fehlschlagen sehen** (Red), dann implementieren (Green), dann refactor. Jeder Bugfix = zuerst ein reproduzierender Regressionstest.
- **Correctness vor Cleverness; YAGNI.** Ein Pattern/eine Abstraktion nur bei realer Variation (Regel der Drei) + **eine Zeile Begründung** im Commit/Worklog.

## AUTONOME LÄUFE — HARD-STOPS
Ohne ausdrückliche Freigabe **NICHT:** Live-DB schreiben (Tests nur gegen tmp/Kopie) · Restart / Merge / Push auf `main` · `pip install` / Env mutieren · Frozen Zone ändern · neue Dependency einführen.
- Bei Hard-Stop oder echter Design-Ambiguität → **PARKEN + Worklog**; nicht raten, nicht mid-run nachfragen.
- Rotes Gate ohne klaren additiven Fix → **PARKEN**. Kontext knapp → nach letzter fertiger Tranche stoppen + **HANDBACK** schreiben.
- **Fail-safe, nicht fail-open.** Pro Tranche committen. **Lauf endet auf `main`.**
- Nacht-/unbeaufsichtigte Läufe **nur in separatem Worktree**, **nie** gegen die Prod-Instanz. **Kosten-Cap** aktiv; am Cap stoppen + Alarm.

## VORGABEN / DEFAULTS (im Zweifel: billiger/sicherer)
- **Parallelisierung:** Default = **Single-Session**. Eskalation nur nach Entscheidungsbaum (Dok. 3). Max **3–5** Subagenten. Agent Team nur, wenn Worker *kommunizieren* müssen. **Dynamic Workflow** nur bei Breite + Unabhängigkeit + Kontext-Sprengung + Prüfbarkeit — erst beaufsichtigt + gedeckelt.
- **Modell-Routing:** Read-only-Massenarbeit → günstig/schnell; harte Synthese/Implementierung → stärkstes Modell.
- **Ausführungsplanung:** Vor jedem **nicht-trivialen** autonomen Lauf ein **Execution Plan** (read-only Plan-Pass) → Checkpoint → Lauf. Zeremonie skaliert mit Umfang (Mini-Änderung fast ohne Plan, Nacht-Lauf voller Plan + Go).
- **UI:** bestehende Design-Tokens/Komponenten nutzen (keine neue Ästhetik erfinden); Barrierefreiheit maschinell (axe/Rollen); **Geschmack = Mensch-Checkpoint.**
- **Modell-Wechsel:** neues Modell → Eval-Suite fahren, bevor unbeaufsichtigter Nacht-Betrieb darauf freigegeben wird.

## ARBEITSMODUS
Kleine Tranchen (reviewbar/testbar/eingrenzbar/rücknehmbar) · **Erkunden → Planen → Umsetzen → Prüfen → Commit → Worklog** · **Conventional Commits** · pro Tranche committen · nur bei Entscheidung (**Urteil / Geld / Unumkehrbarkeit**) oder echtem Blocker melden, sonst Status + weiterarbeiten · **Wartezeit = Arbeitszeit** (nächstes unabhängiges Paket vorziehen, Abhängigkeitsgraph beachten) · **Anhalten ist eine Stärke, kein Versagen.**

## WANN WELCHES DOKUMENT LESEN (`docs/`)
- Lauf planen / Primitiv wählen / Guardrails → **`docs/EXECUTION_PLANNING_AND_GUARDRAILS.md`**
- Parallelisierung / lange Läufe / Roadmap-Metadaten → **`docs/MULTI_AGENT_AND_LONGRUN_STRATEGY.md`**
- Guten Code/UX schreiben / Patterns / Doku-Standard → **`docs/CODE_CRAFT_AND_DESIGN_STANDARDS.md`**
- Deploy / VPS / Handoff / Test-Strategie / Architektur → **`docs/ENGINEERING_PLAYBOOK.md`**
- Plattform-Härtung / offene Verbesserungen → **`docs/AGENT_PLATFORM_HARDENING_BACKLOG.md`**
- Überblick / Lesereihenfolge / Hierarchie → **`docs/INDEX.md`**

## GOVERNANCE
Änderungen an diesen Regeln nur mit Freigabe des Eigentümers. Diese Datei leitet sich aus `docs/` ab und ersetzt die Detail-Dokumente nicht. Halte sie **kurz** — wächst ein Bereich, wandert die Tiefe nach `docs/` oder in `.claude/rules/` (pfad-spezifisch), nicht in diese Datei.
