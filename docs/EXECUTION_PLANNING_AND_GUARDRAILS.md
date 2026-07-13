# Ausführungsplanung & Guardrails

**Companion zu `ENGINEERING_PLAYBOOK.md` und `MULTI_AGENT_AND_LONGRUN_STRATEGY.md` — die Prozess- und Policy-Ebene für autonome Multi-Agent-Ausführung.**

> **Zweck.** Dieses Dokument macht die *Ausführungsplanung* zu einem festen Teil der Methodik. Claude Code bearbeitet nicht nur die fachliche Roadmap, sondern **leitet aus ihr den optimalen Lauf-Plan ab** — welche Agenten/Parallelisierung, wie lang/autonom, mit welchen Sicherungen — als reviewbares Artefakt, das Mensch und Agent **diskutieren und freigeben**, bevor der autonome Lauf startet. Dazu definiert es die **Guardrails** (umgebungs-erzwungene Grenzen) und **Vorgaben** (Defaults, die Claude Code automatisch anwendet). Projekt-unabhängig.
>
> **Die drei tragenden Entscheidungen.**
> 1. **Ausführungsplanung ist eine Pflicht-Phase** zwischen Roadmap/Konzept und autonomem Lauf — kein autonomer Lauf ohne freigegebenen Execution Plan (skaliert mit Lauf-Umfang, siehe §6).
> 2. **Guardrails sind umgebungs-erzwungen, nicht plan-erzwungen.** Ein Plan kann falsch sein; die Hard-Stops dürfen davon nicht abhängen — sie werden via Hooks/Sandbox durchgesetzt, *unabhängig* vom Plan.
> 3. **Vorgaben reduzieren Entscheidungslast.** Im Zweifel das billigere/sicherere Primitiv. Defaults leben in `CLAUDE.md` und werden automatisch angewandt.
>
> **Grundziel.** Maximale Autonomie und möglichst lange Läufe — *abgesichert* durch einen freigegebenen Plan + erzwungene Leitplanken. **Autonomie durch Guardrails, nicht durch Vertrauen.**

---

## Inhaltsverzeichnis

0. [Wo die Planung im Lebenszyklus sitzt](#0-wo-die-planung-im-lebenszyklus-sitzt)
1. [Die Pflicht-Phase „Ausführungsplanung"](#1-die-pflicht-phase-ausführungsplanung)
2. [Der Execution Plan (Artefakt)](#2-der-execution-plan-artefakt)
3. [Das Entscheidungs-Verfahren (Primitiv-Wahl)](#3-das-entscheidungs-verfahren-primitiv-wahl)
4. [Guardrails (umgebungs-erzwungen, nicht verhandelbar)](#4-guardrails-umgebungs-erzwungen-nicht-verhandelbar)
5. [Vorgaben / Defaults (Policy)](#5-vorgaben--defaults-policy)
6. [Planungs-Aufwand skaliert mit Lauf-Umfang](#6-planungs-aufwand-skaliert-mit-lauf-umfang)
7. [Der Checkpoint: Mensch ↔ Claude Code](#7-der-checkpoint-mensch--claude-code)
8. [Integration in CLAUDE.md & Doku-Kanon](#8-integration-in-claudemd--doku-kanon)
9. [Templates (zum Kopieren)](#9-templates-zum-kopieren)
10. [Master-Checkliste](#10-master-checkliste)

---

## 0. Wo die Planung im Lebenszyklus sitzt

Die Methodik bekommt eine neue, verbindliche Station — **zwischen** der fachlichen Roadmap/Konzeption und der autonomen Ausführung:

```
Konzept/Roadmap (fachlich: Scope, Use-Cases, Success-Factors)
        │
        ▼
[ AUSFÜHRUNGSPLANUNG ]  ← read-only Plan-Pass durch Claude Code
   erzeugt: Execution Plan (Primitiv-Wahl, Fronten, Run-Sizing, Guardrails, Kosten)
        │
        ▼
[ CHECKPOINT: Diskussion + Go/No-Go ]  ← Mensch + Claude Code, skaliert mit Umfang
        │
        ▼
[ AUTONOMER LAUF ]  ← Tranchen/Subagenten/Worktrees/Teams/Workflows, gate-gesichert
        │
        ▼
[ MORGEN-QUERCHECK ]  ← Worklog/HANDBACK/Report, Mensch prüft Urteil/Geld/Unumkehrbar
```

**Architekt ≠ Executor, jetzt prozessual verankert:** Der Execution Plan entsteht im *Plan-Pass* (Architekten-Rolle, read-only); der *Lauf* führt ihn autonom aus (Executor-Rolle). Idealerweise prüft eine **frische** Session den Plan vor dem Lauf (Writer ≠ Reviewer auf der Planungs-Ebene).

---

## 1. Die Pflicht-Phase „Ausführungsplanung"

### 1.1 Der Auftrag an Claude Code (neu)

Claude Codes Aufgabe erweitert sich: Es analysiert die Roadmap/das Konzept **read-only** und liefert einen **Execution Plan** — den *optimalen* Weg, das Vorhaben mit Agenten, Parallelisierung und (möglichst langen) autonomen Läufen umzusetzen. Das ist kein optionaler Vorschlag, sondern ein **Pflicht-Deliverable** vor jedem nicht-trivialen autonomen Lauf.

### 1.2 Ablauf des Plan-Passes (read-only)

1. **Recon:** relevante Roadmap-Items, Architektur, Frozen-Zone-Verträge, Datei-Eigentümer mit Datei:Zeile-Belegen lesen — *noch nicht* planen-aus-dem-Gedächtnis.
2. **Abhängigkeitsgraph (DAG)** der Items ableiten → kritischer Pfad + parallele Fronten.
3. **Primitiv-Wahl je Item/Front** nach dem Verfahren in §3.
4. **Tranche-Schnitt** je Item (kontext-beschränkte Einheiten).
5. **Run-Sizing & Guardrail-Bindung** (welche Defaults/Hard-Stops greifen, welcher Kosten-Cap).
6. **Kostenschätzung** (besonders bei Fan-out/Workflows) + **Checkpoints/Park-Punkte** markieren.
7. **Execution Plan schreiben** (§2) und zur Freigabe stellen — **stopp**.

### 1.3 Das Gate

**Kein autonomer Lauf ohne freigegebenen Execution Plan** (Umfang gemäß §6). Das ist die methodische Neuerung: Ausführungsplanung ist ein *Gate* im Lebenszyklus, wie Tests ein Gate beim Merge sind.

---

## 2. Der Execution Plan (Artefakt)

Ein versioniertes Markdown-Dokument (lebt in `docs/`, wird wie jedes Referenzdokument gepflegt). **Pflicht-Inhalt:**

1. **Ziel & Scope-Bezug** — welche Roadmap-Items dieser Lauf adressiert.
2. **Abhängigkeitsgraph** — Items + Kanten; kritischer Pfad markiert.
3. **Parallele Fronten** — welche Item-Gruppen *gleichzeitig* laufen (disjunkte Datei-Eigentümer, keine offenen Abhängigkeiten).
4. **Primitiv-Wahl je Front** — Single-Session / Subagenten-Panel / Worktree-Sessions / Agent Team / Dynamic Workflow — **mit Begründung** nach §3.
5. **Rollen-Besetzung** — welche `.claude/agents/`-Rollen (explorer, test-author, implementer, review-Panel, integrator …), je mit Tool-Scope und Modell.
6. **Tranche-Schnitt & Reihenfolge** — kontext-beschränkte Einheiten je Item + Integrations-Reihenfolge der Fronten.
7. **Run-Sizing** — 1-h-Lauf / Nacht-Lauf / Mehr-Nacht-Epic; Nacht-Tauglichkeit je Front (ja/nein + Grund).
8. **Guardrail-Bindung** — welche Hard-Stops + Defaults gelten; Isolations-Setup (Worktree/Clone); Kosten-Cap; Watchdog-Caps.
9. **Kostenschätzung** — grober Token-/Credit-Rahmen, v. a. bei Fan-out/Workflows.
10. **Checkpoints & Park-Punkte** — wo der Mensch zwingend gebraucht wird (Urteil/Geld/Unumkehrbar) und wo bei Ambiguität geparkt wird.
11. **Definition of Done (maschinell)** — welche Gates/Rubriken den Lauf als erfolgreich definieren.

> Der Plan ist **lebendig**: Parkt der Lauf an einer Stelle oder ändert sich die Lage, wird der Plan im Folge-Pass fortgeschrieben (nie weggeworfen).

---

## 3. Das Entscheidungs-Verfahren (Primitiv-Wahl)

Codifiziert, damit die Wahl **repeatable** ist statt ad-hoc. Claude Code wendet diesen Entscheidungsbaum je Item/Front an.

### 3.1 Der Entscheidungsbaum

```
Berührt es einen Mehrkonsumenten-Vertrag / die Frozen Zone?
  └─ JA  → SERIELL + Mensch-Checkpoint. Nie autonom/parallel.            [STOP]
  └─ NEIN ↓

Ist es EINE kohärente Schreib-Einheit (ein Feature, gekoppelte Logik)?
  └─ JA  → SINGLE-SESSION (eine Tranche).                                [STOP]
  └─ NEIN ↓

Ist es read-only (Recon, Review, Analyse, Suche)?
  └─ JA  → SUBAGENTEN-PANEL (3–5, verschiedene Lenses), Lead synthetisiert.[STOP]
  └─ NEIN ↓   (es ist schreibende Arbeit über MEHRERE Einheiten)

Sind die Einheiten unabhängig UND berühren disjunkte Dateien?
  └─ NEIN → SERIELL ordnen (Abhängigkeiten/Konflikte) oder neu schneiden. [STOP]
  └─ JA  ↓

Müssen die Worker WÄHREND der Arbeit miteinander kommunizieren/koordinieren?
  └─ JA  → AGENT TEAM (z. B. schichtübergreifend, konkurrierende Hypothesen).[STOP]
  └─ NEIN ↓

Wie viele unabhängige Einheiten?
  └─ 2 – ~5     → WORKTREE-SESSIONS / Subagenten mit isolation:worktree.  [STOP]
  └─ zig–hunderte, sauber auffächernd, je maschinell prüfbar
                → DYNAMIC WORKFLOW (fan-out→reduce→synthesize + Grader).  [STOP]
```

### 3.2 Litmus je Primitiv (Kurz-Rubrik)

- **Single-Session:** gekoppelte Schreibarbeit; Korrektheit hängt an *einem* zusammenhängenden Kontext.
- **Subagenten-Panel:** read-heavy, verbose, unabhängige Lenses; Nutzen = Diversität + Kontext-Erhalt; **3–5** ist der Sweet Spot.
- **Worktree-Sessions:** mehrere unabhängige Schreib-Stränge, du integrierst; disjunkte Datei-Eigentümer Pflicht.
- **Agent Team:** Worker müssen *reden*/konvergieren (Hypothesen, Cross-Layer); token-teuer → nur wenn Kommunikation echten Wert schafft.
- **Dynamic Workflow — nur wenn ALLE vier zutreffen:**
  1. **Breite** (zig–hunderte Einheiten, nicht 3–5),
  2. **Unabhängigkeit** (kein gegenseitiger Bezug, disjunkte Dateien),
  3. **Kontext-Sprengung** (Summe passt in keinen Einzelkontext),
  4. **Prüfbarkeit** (Rubrik/Gate je Einheit → Grader kann loop-until-pass).
  Fehlt eine → billigeres Primitiv.

### 3.3 Die Default-Neigung
**Im Zweifel das billigere/sicherere Primitiv.** Eskalation (mehr Parallelität, schwereres Primitiv) ist eine *bewusste* Entscheidung mit Begründung im Execution Plan — nicht der Default.

---

## 4. Guardrails (umgebungs-erzwungen, nicht verhandelbar)

Diese Grenzen halten **unabhängig** davon, was ein Plan vorschlägt — durchgesetzt via Hooks, Sandbox, CI, nicht via guten Absichten. Sie sind die Hard-Stops aus dem Playbook, hier als bindende Lauf-Guardrails:

| Guardrail | Durchsetzung |
|---|---|
| **Kein Live-DB-/Prod-Write** — Tests nur gegen tmp/Kopie | Env-Isolation; `…_DB_PATH→tmp`; Prod-Pfad für den Lauf unerreichbar |
| **Kein Restart/Merge/Push auf `main` ohne grünes Gate** | SubagentStop-Hook + Vier-Kategorien-Gate vor Merge-back |
| **Nacht-/unbeaufsichtigte Läufe nur in separatem Worktree/Clone** | nie gegen die Prod-Instanz; `isolation: worktree` für parallele Schreib-Agenten |
| **Frozen Zone unberührt** | Snapshot-/Contract-Test bricht bei Form-Änderung |
| **Keine neue Dependency / kein `pip install` / keine Env-Mutation** | Sandbox; Dependency-Änderungen nur als Mensch-Schritt |
| **Keine Secrets/PII; kein `git add -A`** | Secret-Scan-Hook (staged); explizite Adds erzwungen |
| **Kosten-Cap je Lauf** | Cost-Logging je Call; Orchestrator stoppt am Cap + Alarm |
| **Fail-safe statt fail-open** | Max-Turn-Caps, No-Progress-Watchdog → parken, nicht raten |
| **Least Privilege je Rolle** | Tools je `.claude/agents/`-Rolle explizit skopiert (nicht weglassen!) |
| **Lauf endet auf `main`** | Arbeitskopie zurückgesetzt; Arbeit lebt auf Branches |

**Prinzip:** Je mehr Autonomie und Parallelität, desto stärker müssen diese Guardrails greifen. Sie sind die *einzige* Grenze, wenn keine menschliche Freigabe pro Aktion mehr existiert (Bypass-Modus).

---

## 5. Vorgaben / Defaults (Policy)

Die **Vorgaben** reduzieren Entscheidungslast: Claude Code wendet sie automatisch an (aus `CLAUDE.md`), ohne Rückfrage. Sie sind die *Standard-Einstellung*; Abweichung ist eine bewusste, begründete Entscheidung im Execution Plan.

| Bereich | Default-Vorgabe |
|---|---|
| **Primitiv-Default** | Single-Session. Eskalation nur, wenn das Verfahren (§3) sie rechtfertigt. |
| **Subagenten-Parallelität** | max **3–5** gleichzeitig; darüber nur via Dynamic Workflow für sauberen Fan-out. |
| **Modell-Routing** | Read-only-Massenarbeit → günstig/schnell (Haiku-Klasse); harte Synthese/Implementierung → stärkstes Modell. |
| **Dynamic Workflows** | **Erst-Lauf beaufsichtigt + hart gedeckelt**; unbeaufsichtigt erst nach bewiesenem Verhalten. Immer Kosten-Cap. |
| **Nacht-Läufe** | nur in separatem Worktree; Kosten-Cap + Watchdog + Morgen-Report Pflicht; Frozen-Zone-/Urteils-/Geld-Items ausgeschlossen. |
| **Planungs-Zeremonie** | skaliert mit Lauf-Umfang (§6) — Mini-Änderung fast ohne Plan, Nacht-Lauf voller Plan + Go. |
| **Default-Neigung** | im Zweifel **billiger/sicherer**: weniger Parallelität, kleineres Primitiv, mehr Verifikation. |
| **Verifikation** | jeder Bugfix → Regressionstest; jedes generierte Artefakt → Gate/Grader-Rubrik. |
| **Kommunikation** | nur bei Entscheidung (Urteil/Geld/Unumkehrbar) oder echtem Blocker melden; sonst Status + weiterarbeiten. |

> Diese Tabelle gehört (verdichtet) in die `CLAUDE.md`, damit sie **automatisch geladen** und ohne Nachfragen befolgt wird.

---

## 6. Planungs-Aufwand skaliert mit Lauf-Umfang

**Die Anti-Bürokratie-Regel.** Würde jede Mini-Änderung einen vollen Execution Plan + Diskussion brauchen, stirbt das Tempo, das Autonomie bringen soll. Darum skaliert die Planungs-Zeremonie mit dem Umfang des Laufs:

| Lauf-Umfang | Planungs-Aufwand | Checkpoint |
|---|---|---|
| **Micro (1 Tranche, lokal, reversibel)** | kein formaler Plan — direkt im Tranchen-Zyklus (Erkunden→Planen→Umsetzen→Prüfen). | keiner (außer Frozen-Zone/Urteil). |
| **1-h-Lauf (wenige Items, eine Front)** | **Kurz-Plan** (5 Zeilen): Items, Primitiv, Datei-Eigentum, DoD, Kosten-Cap. | leichtgewichtiges Go (eine Bestätigung). |
| **Nacht-Lauf (mehrere Fronten, unbeaufsichtigt)** | **voller Execution Plan** (§2). | **Pflicht-Checkpoint** (Go/No-Go, §7) — zählt als Urteils-/Geld-Entscheidung. |
| **Mehr-Nacht-Epic** | voller Plan **+ Zwischen-Checkpoints** + HANDBACK-gekoppelte Lauf-Kette. | mehrere Checkpoints entlang des kritischen Pfades. |

**Faustregel:** Der Planungsaufwand ist proportional zu *Reichweite × Irreversibilität × Kosten* des Laufs. Klein/reversibel/billig → fast kein Overhead. Groß/unbeaufsichtigt/teuer → voller Plan + Freigabe.

---

## 7. Der Checkpoint: Mensch ↔ Claude Code

Hier findet die **Diskussion** statt, die du willst: nicht „der Agent macht einfach", sondern Mensch und Claude Code einigen sich auf den optimalen Weg — *bevor* der Lauf startet. Der Execution-Plan-Checkpoint ist einer der **wenigen echten Checkpoints** (Urteil/Geld/Unumkehrbarkeit): ein Nacht-Lauf bindet Zeit *und* Geld (besonders Fan-out/Workflows), also ist seine Freigabe eine bewusste Entscheidung.

### 7.1 Was der Mensch prüft (Go/No-Go)
- **Primitiv-Wahl plausibel?** Wird unnötig parallelisiert (teuer) oder unnötig serialisiert (langsam)?
- **Fronten wirklich disjunkt?** Kein verstecktes Datei-/Abhängigkeits-Overlap, das später Merge-Konflikte erzeugt.
- **Run-Sizing & Nacht-Tauglichkeit** realistisch? Sind Frozen-Zone-/Urteils-Items sauber ausgeschlossen?
- **Kosten-Rahmen** akzeptabel, Cap gesetzt?
- **Guardrails & Isolation** korrekt gebunden (separater Worktree, nie Prod)?
- **DoD maschinell entscheidbar?** Kann der Lauf autonom abschließen?

### 7.2 Die Diskussion ist beidseitig
Claude Code **challengt** den Plan aktiv mit: alternative Schnitte, Risiken, billigere Wege, wo Parallelität sich *nicht* lohnt. Der Mensch lenkt nach (mehr/weniger Autonomie, andere Reihenfolge, zusätzliche Checkpoints). Ergebnis: ein *gemeinsam getragener* Plan.

### 7.3 Freigabe & Protokoll
Das Go wird im Worklog/Plan festgehalten (wer, wann, welche Version des Plans, welcher Kosten-Cap). Der Lauf referenziert den freigegebenen Plan. Ändert der Lauf den Plan substanziell (z. B. neue Front nötig) → **parken + Re-Approval**, nicht stillschweigend abweichen.

---

## 8. Integration in CLAUDE.md & Doku-Kanon

Damit das **gelebte Methodik** wird, nicht totes Papier:

- **`CLAUDE.md`** (auto-geladen) bekommt einen Abschnitt „Ausführungsplanung & Guardrails": (a) die Pflicht-Phase + das Gate (§1.3), (b) die Vorgaben-Tabelle (§5) verdichtet, (c) die Guardrails (§4) als eiserne Regeln, (d) der Verweis auf dieses Dokument als kanonische Quelle.
- **Doku-Governance:** Ändern sich Guardrails/Vorgaben, gilt die harte Regel — betroffene Dokumente im selben Arbeitsblock aktualisieren; eine Änderung ohne konsistente Doku ist unvollständig.
- **ADR:** Die Einführung der Pflicht-Phase und der Guardrail-Durchsetzung wird als ADR festgehalten (Kontext/Entscheidung/Konsequenz), damit die *Begründung* nicht verloren geht.
- **Roadmap-Kopplung:** Jedes Roadmap-Item trägt die Agent-Metadaten aus der Multi-Agent-Strategie (DAG, Parallelisierbarkeits-Tag, Datei-Eigentum, DoD, Run-Sizing). Der Execution Plan *aggregiert* sie zu Fronten und Läufen — der Plan-Pass wird dadurch fast mechanisch.

> **Kreis geschlossen:** Roadmap-Item-Metadaten (Strategie-Doc §7) → Plan-Pass aggregiert → Execution Plan → Checkpoint → autonomer Lauf unter Guardrails → Morgen-Quercheck → Roadmap fortgeschrieben.

---

## 9. Templates (zum Kopieren)

### 9.1 Execution Plan

```markdown
# Execution Plan — <Phase/Lauf-Name>  (Stand: <Datum>, Plan v<n>)

## Ziel & Scope
Adressierte Items: [R-040, R-041, R-042]

## Abhängigkeitsgraph
R-040 → R-042 ;  R-041 (unabhängig)
Kritischer Pfad: R-040 → R-042

## Parallele Fronten
- Front A: [R-041]            Datei-Eigentum: src/ingest/**          (disjunkt)
- Front B: [R-040 → R-042]    Datei-Eigentum: src/api/**, tests/api/** (seriell intern)

## Primitiv-Wahl (mit Begründung)
- Front A: Worktree-Session — unabhängige Schreib-Einheit, disjunkte Dateien.
- Front B: Single-Session-Kette — gekoppelte Logik (R-040 blockt R-042).
- Review (beide Fronten): Subagenten-Panel (style/security/test-coverage).

## Rollen-Besetzung
implementer (stark), test-author (mittel), security-reviewer (stark, read-only) ...

## Tranche-Schnitt & Integrations-Reihenfolge
Front A: 2 Tranchen. Front B: 3 Tranchen. Merge: A, dann B-Kette; Gate am integrierten Stand.

## Run-Sizing
Nacht-Lauf. Nacht-tauglich: ja (keine Frozen Zone, keine Urteils-Items).

## Guardrails & Isolation
Separater Worktree C:\proj\agent-wt\; nie Prod. Kosten-Cap: <X> Credits. Watchdog: 12 Turns/Tranche.
Hard-Stops aktiv: kein Live-Write, kein Push ohne Gate, Frozen Zone tabu, kein add -A.

## Kostenschätzung
Front A ~<…>, Front B ~<…>; Cap <X> mit Low-Credit-Alarm.

## Checkpoints & Park-Punkte
Checkpoint: keiner (rein additiv). Park: bei Schema-Ambiguität in R-042 → parken.

## Definition of Done (maschinell)
Kat.1+Kat.3 grün · Contract items_v2 · Smoke 200 · Grader "items-crud" ≥ Schwelle.

## Freigabe
Go: <Name> @ <Datum> auf Plan v<n>, Cap <X>.
```

### 9.2 Kickoff-/Freigabe-Snippet (an Claude Code)

```text
Plan-Pass (read-only) für Phase <X>:
1. Recon der Items <…> + Frozen-Zone-/Datei-Eigentum prüfen (Datei:Zeile-Belege).
2. Execution Plan nach EXECUTION_PLANNING_AND_GUARDRAILS.md §2 erstellen.
3. Primitiv-Wahl nach §3 begründen; Default-Neigung billiger/sicherer.
4. Guardrails §4 binden; Kosten-Cap vorschlagen; Nacht-Tauglichkeit je Front bewerten.
5. STOPP zur Diskussion. Challenge den Plan aktiv (billigere Wege, Risiken, wo Parallelität sich nicht lohnt).
Erst nach Go autonom ausführen; bei substanzieller Planänderung parken + Re-Approval.
```

---

## 10. Master-Checkliste

**Prozess** — Ausführungsplanung ist Pflicht-Phase · read-only Plan-Pass → Checkpoint → autonomer Lauf → Morgen-Quercheck · kein autonomer Lauf ohne freigegebenen Plan (Umfang-skaliert) · Architekt ≠ Executor, frische Session reviewt den Plan.

**Execution Plan** — Ziel/Scope · DAG/kritischer Pfad · disjunkte Fronten · Primitiv-Wahl mit Begründung · Rollen+Tool-Scope+Modell · Tranche-Schnitt+Integrations-Reihenfolge · Run-Sizing+Nacht-Tauglichkeit · Guardrail-Bindung+Isolation · Kostenschätzung+Cap · Checkpoints/Park-Punkte · maschinelle DoD.

**Entscheidungs-Verfahren** — Entscheidungsbaum je Item/Front · Frozen Zone → seriell+Checkpoint · kohärente Schreib-Einheit → Single-Session · read-only → Subagenten-Panel · unabhängige Schreib-Stränge → Worktree/Team/Workflow je Skala · Dynamic Workflow nur bei Breite+Unabhängigkeit+Kontext-Sprengung+Prüfbarkeit · Default-Neigung billiger/sicherer.

**Guardrails (erzwungen)** — kein Live-Write · kein Push ohne Gate · Nacht-Lauf nur separater Worktree (nie Prod) · Frozen Zone tabu · keine Env-Mutation · keine Secrets/`add -A` · Kosten-Cap · fail-safe · Least Privilege · Ende auf `main`.

**Vorgaben/Defaults** — Primitiv-Default Single-Session · 3–5 Subagenten · Modell-Routing · Workflows erst beaufsichtigt+gedeckelt · Nacht-Läufe isoliert+Cap+Watchdog+Report · Zeremonie skaliert mit Umfang · im Zweifel billiger/sicherer · Regressionstest/Grader je Artefakt.

**Checkpoint** — Mensch prüft Primitiv/Fronten/Sizing/Kosten/Guardrails/DoD · beidseitige Diskussion (Claude Code challengt) · Go protokolliert · substanzielle Abweichung → parken+Re-Approval.

**Integration** — CLAUDE.md trägt Phase+Vorgaben+Guardrails · Doku-Governance · ADR für die Einführung · Roadmap-Item-Metadaten ↔ Execution Plan gekoppelt.

---

*Companion zu `ENGINEERING_PLAYBOOK.md` und `MULTI_AGENT_AND_LONGRUN_STRATEGY.md`. Lebendes Dokument. Die Tool-Spezifika (Dynamic Workflows, Agent Teams) sind Stand 2026 und entwickeln sich; die Prinzipien — Planung als Gate, Guardrails umgebungs-erzwungen, Defaults billiger/sicherer, Zeremonie skaliert mit Umfang — bleiben.*
