# docs/INDEX.md — Methodik-Korpus: Karte & Lesereihenfolge

**Der Einstiegspunkt in die Engineering-Methodik. Fünf Dokumente, ein System.**

> **Zweck.** Dieses Dokument ist die *Karte* über die fünf Methodik-Dokumente: was jedes enthält, in welcher Reihenfolge man sie liest, welches bei Widerspruch gewinnt, und welches Dokument für welche Aufgabe zuständig ist. Die operativen Direktiven leben verdichtet in der auto-geladenen `CLAUDE.md` (Repo-Root); die *Tiefe* liegt hier in `docs/` und wird bei Bedarf gelesen.

---

## Die fünf Dokumente

| # | Dokument | Enthält | Lies es, wenn du … |
|---|---|---|---|
| 1 | **ENGINEERING_PLAYBOOK.md** | Kernmethodik: 13 Prinzipien, Mensch↔Agent-Modell, dokumenten-getriebene Entwicklung, Tranche-Zyklus, Vier-Kategorien-Test-Gate, Architektur-Muster, Deployment/VPS-Härtung, Handoff, CI/CD | deployen, testen, den VPS härten, einen Handoff schreiben, die Test-Strategie oder Architektur nachschlagen willst |
| 2 | **MULTI_AGENT_AND_LONGRUN_STRATEGY.md** | Parallelisierung (Subagenten/Teams/Workflows/Worktrees), lange autonome Läufe, die „Agent-Ready Roadmap" (Item-Metadaten) | einen Lauf parallelisieren, lange/Nacht-Läufe planen oder eine Roadmap agenten-tauglich schneiden willst |
| 3 | **EXECUTION_PLANNING_AND_GUARDRAILS.md** | Ausführungsplanung als Pflicht-Phase, Entscheidungsbaum zur Primitiv-Wahl, Guardrails (erzwungen) vs. Vorgaben (Defaults), Execution-Plan-Template, Checkpoint | einen Lauf *planst*, das richtige Agenten-Primitiv wählst oder die verbindlichen Grenzen/Defaults brauchst |
| 4 | **CODE_CRAFT_AND_DESIGN_STANDARDS.md** | Wie man guten Code schreibt: Test-First, Methodik-Portfolio, UX-/Usability-Methodik, Code-Vorgaben, Dokumentations-Standard, Architektur & Design-Patterns | Code oder UI baust, Patterns einsetzt, entscheidest *wie* getestet wird oder wie viel dokumentiert wird |
| 5 | **AGENT_PLATFORM_HARDENING_BACKLOG.md** | Priorisierter Backlog offener Verbesserungen: Eval-Gate, Telemetrie, Provenance, Trust-Boundary/Venue-Matrix, Regel-Lebenszyklus + 5 Zusatzpunkte | wissen willst, was an der Plattform noch zu härten ist und in welcher Reihenfolge |

---

## Lesereihenfolge

**Frische Executor-Session (Onboarding, read-only):** zuerst die **`CLAUDE.md`** vollständig (macht allein arbeitsfähig) → dann dieses `INDEX.md` → das für die anstehende Aufgabe zuständige Dokument (Tabelle unten). *Nicht alle fünf am Stück laden* — das ist Kontext-Verschwendung; gezielt lesen.

**Mensch / neuer Mitarbeiter (Verständnis):** 1 → 2 → 3 → 4 → 5 (vom Fundament zur Härtung).

**Architekten-Chat (Planung):** 3 (Planung/Guardrails) + 2 (Parallelisierung) für den Lauf-Plan; 1 + 4 als Referenz.

---

## Hierarchie der Wahrheit (bei Widerspruch)

1. **Repo-/Live-Zustand** (was der Code/das System *tatsächlich* tut) gewinnt immer.
2. **`docs/`-Referenzdokumente** (diese fünf) — die kanonische Methodik.
3. **`CLAUDE.md`** — leitet sich aus `docs/` ab, verdichtet für die tägliche Arbeit.

Innerhalb von `docs/` gilt: projekt-spezifische Fakten (Projekt-Stand/Entscheidungslog eines konkreten Projekts) schlagen allgemeine Methodik, wenn sie bewusst abweichen — solche Abweichungen werden als **bekannte Verstöße (Ist ≠ Ziel)** ehrlich dokumentiert, nicht kaschiert.

Bei Unklarheit: **fragen statt raten.**

---

## Aufgabe → Dokument (Schnell-Routing)

| Aufgabe | Dokument |
|---|---|
| Einen autonomen Lauf planen / Primitiv wählen | 3 (Planung/Guardrails) → 2 (Parallelisierung) |
| Roadmap-Item schneiden (agenten-tauglich) | 2 (Agent-Ready Roadmap) |
| Code/Feature bauen, Pattern wählen, testen | 4 (Craft/Standards) |
| Deployen, VPS härten, Rollback, Handoff | 1 (Playbook) |
| Test-Strategie / Vier-Kategorien-Gate | 1 (Playbook) + 4 (Test-First-Handwerk) |
| Sicherheit/Guardrails/Trust-Boundaries | 3 (Guardrails) + 5 (Trust-Boundary-Matrix) |
| Plattform verbessern/härten | 5 (Backlog) |

---

## Wie die Dokumente zusammenhängen

```
1 PLAYBOOK  ──────────►  das Wie der Entwicklung (Fundament)
      │
2 MULTI-AGENT  ────────►  Parallelisierung + lange Läufe + Roadmap-Metadaten
      │
3 EXECUTION+GUARDRAILS ►  Plan-Pass → Checkpoint → Lauf; erzwungene Grenzen + Defaults
      │
4 CODE-CRAFT  ─────────►  wie guter Code/UX entsteht (Handwerk)
      │
5 HARDENING-BACKLOG  ──►  was noch fehlt (Messbarkeit, Beweisbarkeit, Absicherung)
```

Der Fluss eines Vorhabens: **Roadmap-Item (2)** → **Execution Plan (3)** → **Checkpoint (3)** → **autonomer Lauf** (baut nach 1 + 4, unter Guardrails aus 3) → **Morgen-Quercheck** (1: Handoff/HANDBACK) → Roadmap fortgeschrieben. Der **Backlog (5)** härtet diesen Kreislauf.

---

## Verhältnis zur `CLAUDE.md`

Die `CLAUDE.md` im Repo-Root wird von Claude Code **automatisch geladen** und ist bewusst **kurz** (< 200 Zeilen) — sie enthält die *nicht verhandelbaren Direktiven*, die *Defaults* und projekt-spezifische Fakten, plus **Verweise** auf diese Dokumente. Die fünf Dokumente werden **nicht** in die `CLAUDE.md` importiert (das würde den Kontext jeder Session belasten), sondern **bei Bedarf gelesen**. Durchsetzung harter Grenzen erfolgt über **Hooks/Gates**, nicht über den `CLAUDE.md`-Text.

---

## Governance

Alle fünf sind **lebende Dokumente** — fortschreiben wie Code, nie als Denkmal behandeln. Bei architektur-/API-/security-/persistenz-/release-wirksamen Änderungen werden die betroffenen Dokumente **im selben Arbeitsblock** aktualisiert (eine Änderung ohne konsistente Doku gilt als unvollständig). Der Lebenszyklus der Regeln selbst (Owner/Version/Review/Sunset) ist in Dokument 5 (Backlog, G5) definiert.
