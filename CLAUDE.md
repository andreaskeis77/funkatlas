# CLAUDE.md — Operative Verfassung

Diese Datei wird von Claude Code beim Session-Start automatisch geladen. Sie ist bewusst **kurz** (Ziel < 200 Zeilen): nur *operative Direktiven* + projekt-spezifische Fakten. Die **ausführliche Methodik liegt in `docs/`** und wird **bei Bedarf** gelesen — Karte: `docs/INDEX.md`. Die Detail-Dokumente werden hier **nicht importiert** (das würde jeden Session-Kontext belasten).

**Durchsetzung:** Diese Datei *lenkt* Verhalten (Kontext, kein Zwang). Harte Grenzen werden über **Hooks/Gates** erzwungen, nicht über diesen Text.

**Hierarchie der Wahrheit (bei Widerspruch):** Repo-/Live-Zustand > `docs/`-Referenz > diese Datei. Bei Unklarheit: **fragen statt raten.**

---

## PROJEKT — AUSFÜLLEN JE PROJEKT
<!-- Projekt-spezifisch. Beim Einsetzen in ein Repo ausfüllen; beim Mergen mit einer bestehenden CLAUDE.md die vorhandenen Projekt-Fakten HIER übernehmen. -->
- **Produkt (ein Absatz):** <was ist das, für wen>
- **Stack / Topologie:** <Sprachen, Frameworks, DB, Hosting/VPS>
- **Öffentliche Endpunkte / Health:** <URLs, /healthz, /status>
- **Standard-Befehle:** <z. B. `./task.cmd quality-gates` · `test` · `server` · `handoff`>
- **Entscheidungslog:** siehe `docs/PROJECT_STATE.md` <oder inline: E1…En>
- **Bekannte Verstöße / GOTCHAs (Ist ≠ Ziel):** <ehrlich auflisten, was noch NICHT methodik-konform ist — z. B. „Kat.4-Tests fehlen", „kein Staging">

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
