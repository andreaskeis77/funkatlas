# Multi-Agent- & Long-Run-Strategie

**Companion zum Engineering-Playbook — Parallelisierung von KI-Agenten und maximal lange autonome Claude-Code-Läufe.**

> **Zweck.** Diese Strategie ergänzt das `ENGINEERING_PLAYBOOK.md` um eine Dimension: *wie* wir Arbeit auf parallele Agenten verteilen und *wie* wir möglichst lange, autonome Läufe (1 h+, idealerweise über Nacht) sicher fahren — und vor allem, *wie wir das bereits bei der Definition von Roadmaps und Konzepten berücksichtigen*. Sie ist projekt-unabhängig.
>
> **Grundthese.** Wall-Clock-Länge eines Laufs ist ein **Ergebnis, kein Steuerungsziel.** Lange produktive Autonomie entsteht nicht aus *einem* Riesen-Kontext (der driftet und degradiert), sondern aus einer **orchestrierten Kette kontext-beschränkter Tranchen** mit durablem Gedächtnis dazwischen, plus Subagenten, die den Hauptkontext sauber halten. Wir optimieren auf *ununterbrochenen, verifizierten Fortschritt* — die Stunden folgen.
>
> **Sicherheitsprinzip.** **Autonomie durch Guardrails, nicht durch Vertrauen.** Bei Bypass-Permissions + neuestem Modell + unbeaufsichtigtem Nacht-Lauf sind die automatischen Gates und die Umgebungs-Isolation das *einzige* Sicherheitsnetz. Mehr Autonomie verlangt *stärkere*, nicht schwächere Leitplanken.
>
> **Sprachkonvention.** Doku/Kommunikation Deutsch; Code/Identifier/Commits Englisch.

---

## Inhaltsverzeichnis

0. [Die fünf harten Wahrheiten](#0-die-fünf-harten-wahrheiten)
1. [Claude Codes Multi-Agent-Primitive (Stand 2026)](#1-claude-codes-multi-agent-primitive-stand-2026)
2. [Was parallelisieren — die Parallelisierungs-Taxonomie](#2-was-parallelisieren--die-parallelisierungs-taxonomie)
3. [Die Orchestrierungs-Muster](#3-die-orchestrierungs-muster)
4. [Die Rollen-Bibliothek (`.claude/agents/`)](#4-die-rollen-bibliothek-claudeagents)
5. [Gates als Multi-Agent-Sicherheitsnetz](#5-gates-als-multi-agent-sicherheitsnetz)
6. [Strategie für lange & sehr lange autonome Läufe](#6-strategie-für-lange--sehr-lange-autonome-läufe)
7. [Die Agent-Ready Roadmap (der Kern)](#7-die-agent-ready-roadmap-der-kern)
8. [Konkrete Claude-Code-Setup-Checkliste](#8-konkrete-claude-code-setup-checkliste)
9. [Reifegrad-Stufenplan](#9-reifegrad-stufenplan)
10. [Roadmap-Item-Template (zum Kopieren)](#10-roadmap-item-template-zum-kopieren)
11. [Master-Checkliste](#11-master-checkliste)

---

## 0. Die fünf harten Wahrheiten

Bevor irgendeine Mechanik: Diese fünf Wahrheiten bestimmen, ob Multi-Agent + lange Läufe sich auszahlen oder spektakulär scheitern.

1. **Multi-Agent ist token-teuer und nicht immer besser.** Agent Teams und Subagenten-Fan-out verbrauchen deutlich mehr Tokens als eine Single-Session und addieren Koordinations-Overhead. Sie glänzen bei *parallelisierbarer, lese-/explorationslastiger, unabhängiger* Arbeit. Bei *sequenziell-gekoppelter Schreibarbeit am selben Code* (= „ein kohärentes Feature bauen") verliert Parallelität gegen eine fokussierte Single-Session. **Regel:** das Parallelisierbare parallelisieren, das Gekoppelte serialisieren — und die Roadmap so schneiden, dass *mehr* parallelisierbar wird.

2. **Lange Läufe sind Kontext-Management, nicht Zeit-Management.** Der Limiter ist das Kontext-Budget, nicht die Uhr. „Über Nacht" = eine *Kette* beschränkter, gecheckpointeter Tranchen mit Worklog/HANDBACK dazwischen — nicht *ein* 8-Stunden-Kontext. Subagenten und Workflows sind die Mechanik dafür: sie halten verbose Arbeit aus dem Hauptkontext und geben nur die Schlussfolgerung zurück.

3. **Bypass + Max-Modell + unbeaufsichtigt = Gates sind das einzige Netz.** Ohne menschliche Freigabe pro Aktion verhindern nur noch (a) Umgebungs-Isolation und (b) automatische Gates eine Katastrophe. Die Gates aus dem Playbook (vier Test-Kategorien, Secret-Scan, Frozen Zone, Hard-Stops) werden von „Qualitätssicherung" zu „Überlebens-Infrastruktur".

4. **Fail-safe, nicht fail-open.** Ein unbeaufsichtigter Agent muss bei Unklarheit **parken + loggen**, nicht raten und pushen. Das verlangt: harte Turn-/Iterations-Caps pro Tranche, einen No-Progress-Watchdog, und ein Kosten-Cap, das den Lauf am Limit beendet.

5. **Der Mensch wird zum Architekten des Lauf-Plans.** Die Wertschöpfung verschiebt sich vom Implementieren zum *Entwerfen der Parallelisierung*: Abhängigkeitsgraph, Tranche-Schnitt, maschinen-prüfbare Definition of Done, Integrations-Reihenfolge. Eine Roadmap definiert ab jetzt nicht nur *was* gebaut wird, sondern *wie es ein Agenten-Schwarm in langen Läufen baut* (Teil 7).

---

## 1. Claude Codes Multi-Agent-Primitive (Stand 2026)

Vier native Bausteine. Die Wahl des richtigen Bausteins *ist* die Strategie.

| Primitiv | Was | Stärken | Schwächen / Grenzen | Wann nutzen |
|---|---|---|---|---|
| **Subagenten** | Isolierte Claude-Instanz *in* der Session; eigener Kontext, eigene Tools, eigenes Modell. Nur die **Zusammenfassung** kehrt zum Lead zurück. Definiert via `.claude/agents/*.md` (Frontmatter: `name`, `description`, `tools`, `model`) oder ad-hoc via Task-Tool. | Kontext-Erhalt (verbose Arbeit bleibt isoliert), Parallelität, Least-Privilege je Agent. Built-ins: **Explore** (read-only, Haiku), **Plan** (read-only Recherche), **General-purpose** (volle Tools). | **Können keine Subagenten spawnen** (keine Verschachtelung). Kein Echtzeit-Kontext-Sharing. Same-File-Edits → Konflikt (eigene Dateien/Ordner geben *oder* `isolation: worktree`). **Sweet Spot 3–5 gleichzeitig.** | Parallele Recherche/Exploration, Multi-Lens-Review desselben Artefakts, Edits an *unabhängigen* Dateien, alles Verbose-Lastige. |
| **Agent Teams** | Teammates je im **eigenen** Kontextfenster, die **direkt miteinander** kommunizieren (nicht nur an den Lead melden). Lead koordiniert über geteilte Task-Liste. *Experimentell, standardmäßig aus* (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). | Worker können Erkenntnisse teilen, sich **gegenseitig challengen**, selbst koordinieren. Stark bei: paralleler Exploration, **Debugging mit konkurrierenden Hypothesen**, schichtübergreifenden Änderungen (Frontend/Backend/Tests je ein Teammate). | Höherer Koordinations-Overhead, deutlich mehr Tokens. Schlecht bei sequenziellen Aufgaben, Same-File-Edits, vielen Abhängigkeiten. | Wenn Worker *kommunizieren* müssen, um zu konvergieren — sonst Subagenten nehmen. |
| **Dynamic Workflows** | Der Lead schreibt **dynamisch ein Orchestrierungs-Skript**, fächert in zig–hunderte Subagenten auf, **validiert vor der finalen Antwort**. Form: *fan out → reduce → synthesize*. Plus **Grader** (Performance Outcomes): bewertet jedes Ergebnis gegen eine Rubrik, erzwingt Überarbeitung bis zum Bestehen. *Research Preview; Max/Team/Enterprise + API.* | Skaliert weit über eine Single-Session; Orchestrierung lebt in Code → der Hauptkontext sieht nur das Endergebnis. Für Aufgaben, die **Stunden bis Tage** dauern (verbreitete Bugs, große Migrationen, Security-Audits, Architektur-Analyse). | Opt-in, sehr token-hungrig. Nur sinnvoll, wenn die Aufgabe *sauber* auffächert. | Breite, fan-out-fähige Jobs mit unabhängiger Verifikation; der Mechanismus für *sehr* lange Läufe. |
| **Worktree-Sessions / Background Agents** | Mehrere Claude-Code-Sessions, die *du* selbst startest — jede auf eigenem **Git-Worktree** (= eigener Branch, eigener Arbeitsbaum). Background-Agents laufen unabhängig, beobachtbar von einer Stelle. | Echtes paralleles *Coding* am selben Repo ohne Branch-Kollision; volle Isolation pro Strang. | Manuelle Koordination/Integration; du trägst den Merge-Plan. | Mehrere unabhängige Features/Tickets gleichzeitig; der robusteste Weg für parallele Schreibarbeit. |

**Die Faustregel zur Wahl:** *Ein paar delegierte Aufgaben in einer Session* → Subagenten. *Worker müssen miteinander reden* → Agent Teams. *Zig–hunderte auffächernde Teilaufgaben aus einem Skript* → Dynamic Workflows. *Mehrere unabhängige Code-Stränge am selben Repo* → Worktree-Sessions.

---

## 2. Was parallelisieren — die Parallelisierungs-Taxonomie

Die entscheidende Heuristik: **Lese-/explorationslastig + unabhängig = parallel. Schreib-koordiniert + sequenziell = serialisieren.** Angewandt auf die Aktivitäten, die du genannt hast:

| Aktivität | Parallelisierbar? | Bevorzugtes Primitiv | Isolation / Hinweis |
|---|---|---|---|
| **Konzept/Recon erkunden** (Code lesen, Optionen sammeln, Architektur sondieren) | **Ja, ideal** | Subagenten (Explore/Plan), bei Konvergenz Agent Team | Read-only; mehrere Lenses parallel, Lead synthetisiert. Kein Schreibkonflikt möglich. |
| **Test-Cases definieren** (gegen Spec/Contract, vor dem Code) | **Ja** | Subagent „test-author" je Modul/Endpoint | Eigene Test-Dateien pro Agent. Writer ≠ Reviewer: Test-Autor ≠ Code-Autor. |
| **Code implementieren — *ein* kohärentes Feature** | **Nein → serialisieren** | Single-Session (eine Tranche) | Gekoppelte Schreibarbeit; Parallelität schadet hier. |
| **Code implementieren — *mehrere unabhängige* Features/Module** | **Ja** | Worktree-Sessions *oder* Subagenten mit `isolation: worktree` | Striktes Datei-/Verzeichnis-Eigentum; Abhängigkeitsgraph beachten. |
| **Debuggen — eine Ursache, unklar** | **Ja, ideal** | Agent Team (konkurrierende Hypothesen) | Teammates testen verschiedene Theorien parallel, konvergieren schneller. |
| **Review/QA** (Stil, Security, Test-Coverage, A11y) | **Ja, ideal** | Subagenten-Panel (verschiedene Lenses) auf dasselbe Diff | Jeder Agent blind für die Funde der anderen → fängt mehr Fehlerklassen. |
| **Dokumentation generieren** (aus Code/Diff) | **Ja** | Subagent „doc-writer" | Eigene Doku-Dateien; gegen die Wahrheit prüfen (Text == Code/DB). |
| **Migration/Refactor über viele unabhängige Dateien** | **Ja, ideal** | Dynamic Workflow (`pipeline`/`parallel`) | Programmatische Edits, die sauber auffächern; Grader prüft jede Datei. |
| **Schema-/API-Vertrag ändern (Frozen Zone)** | **Nein → ein bewusster, serieller Akt** | Single-Session + Mensch-Checkpoint | Mehrkonsumentiger Vertrag; niemals parallel/autonom anfassen. |
| **Integration/Merge** (Stränge zusammenführen) | **Nein → serialisieren** | Lead/Orchestrator, definierte Reihenfolge | `merge --no-ff`, Gate am integrierten Stand. |

**Konsequenz für den Bau-Zyklus:** Der Tranchen-Zyklus aus dem Playbook (Erkunden → Planen → Umsetzen → Prüfen) wird teilweise *fan-out-fähig*: **Erkunden** und **Prüfen/Review** parallelisieren hervorragend (read-heavy), **Umsetzen** bleibt pro kohärenter Einheit seriell, lässt sich aber über *unabhängige* Einheiten parallelisieren.

---

## 3. Die Orchestrierungs-Muster

Wiederverwendbare Muster, die direkt auf eure Methodik einzahlen:

### 3.1 Fan out → reduce → synthesize
Das Grundmuster jeder Parallelisierung: Lead zerlegt → N Subagenten arbeiten isoliert → Lead sammelt die Summaries → synthetisiert ein Ergebnis. Bei Dynamic Workflows lebt die Schleife in Code (`agent()` = einer, `parallel()` = Barriere, `pipeline()` = Streaming ohne Barriere), sodass der Hauptkontext nur das Endergebnis sieht — *das* ist der Hebel für lange Läufe.

### 3.2 Das Review-Panel (Writer ≠ Reviewer, realisiert)
Euer „frischer Blick fürs Review" wird zum **Panel differierend skopierter Subagenten** auf dasselbe Artefakt: ein `style-reviewer`, ein `security-reviewer`, ein `test-coverage-reviewer`. Jeder ist blind für die Funde der anderen → das Panel fängt Fehlerklassen, die ein einzelner Reviewer übersieht. Der Lead sammelt die Verdikte.

### 3.3 Debugging mit konkurrierenden Hypothesen
Statt einer linearen Fehlersuche: ein Agent Team, in dem Teammates *verschiedene Theorien parallel* testen und auf die Antwort konvergieren — der schnellste Weg bei unklarer Ursache. Passt zu eurem „Root-Cause-First": mehrere Hypothesen *gleichzeitig*, statt eine nach der anderen.

### 3.4 Die Spec→Code→Test→Docs-Pipeline
Sequenzielle Kette delegierter Schritte, jeder übergibt eine *saubere Zusammenfassung* an den nächsten: `planner` (Recon + Konzept) → `test-author` (Tests gegen Spec) → `implementer` (Code) → `reviewer-panel` (QA) → `doc-writer` (Doku). Jeder Schritt isoliert, der Hauptkontext bleibt schlank.

### 3.5 Der Grader-Loop (loop-until-dry)
Verifikation als Schleife statt als Einmal-Check: ein **Grader** bewertet das Ergebnis gegen eine explizite **Rubrik** und schickt es zur Überarbeitung zurück, bis es besteht. Das ist euer „Verifizierbar statt vertrauensselig" als automatischer Regelkreis — und es ersetzt menschliches Review für alles Maschinen-Prüfbare.

### 3.6 Orchestrator/Lead-Muster
Eine Session ist der **Lead** (Architekt des Laufs): sie zerlegt, dispatcht, sammelt, integriert — schreibt aber idealerweise *selbst wenig Code*. Das hält den Lead-Kontext für Orchestrierung frei statt für grep-Output. Mapped auf euer „Architekt ≠ Executor": der Lead ist der Architekt-im-Lauf, die Subagenten/Teammates sind die Executors.

---

## 4. Die Rollen-Bibliothek (`.claude/agents/`)

Definiere wiederkehrende Worker **einmal** als Markdown-Datei mit Frontmatter (`name`, `description`, `tools`, `model`) — der Lead liest die `description`, um zu entscheiden, wann er delegiert. **Least Privilege je Rolle** (Achtung: `tools` *weglassen* gewährt *alle* Tools, nicht keine — also explizit skopieren). **Modell-Routing** je Rolle: billiges Modell für Read-only-Massenarbeit, stärkstes Modell für harte Synthese.

| Rolle | Zweck | Tool-Scope (Least Privilege) | Modell-Hinweis |
|---|---|---|---|
| `explorer` | Read-only Codebase-Suche, Recon mit Datei:Zeile-Belegen | nur Read/Grep/Glob | günstig/schnell (Haiku-Klasse) |
| `planner` | Konzept, Optionen, Abhängigkeits-Analyse vor dem Bauen | Read-only | stark (Synthese zählt) |
| `test-author` | Tests gegen Spec/Contract, *vor* dem Code | Read + Write (nur Test-Dateien) | mittel/stark |
| `implementer` | Code für *eine* kohärente Einheit | Read + Write (Scope-Dateien) + Run-Tests | stark |
| `style-reviewer` | Lesbarkeit, Idiome, Konventionen | Read-only | mittel |
| `security-reviewer` | Secrets, Injection, Auth, Supply-Chain | Read-only + Secret-Scan | stark |
| `test-coverage-reviewer` | fehlende Fälle, Regressionen | Read-only + Coverage | mittel |
| `integrator` | Stränge zusammenführen, Gate am integrierten Stand | Read + Git-Merge | stark |
| `ops-debugger` | Logs/Health/Exit-Codes triagieren, Hypothesen | Read + Run + Logs | mittel/stark |

> **Disziplin:** Eine Rolle, die als Agent-Team-Teammate läuft, erbt ihre `tools`-Allowlist und ihr Modell; ihre `skills`/`mcpServers`-Frontmatter-Felder greifen *nicht* als Teammate. Rollen also so schneiden, dass sie ohne diese Felder funktionieren, wenn sie im Team laufen sollen.

---

## 5. Gates als Multi-Agent-Sicherheitsnetz

Bei autonomen Multi-Agent-Läufen werden die Gates aus dem Playbook zur **Überlebens-Infrastruktur**. Zusätzlich zu den vier Test-Kategorien:

- **SubagentStop-Hook — der wichtigste neue Baustein.** Ein Hook erzwingt die Unverhandelbaren *bevor* der Lead ein Subagenten-Ergebnis zurückfaltet: **Tests grün · keine Secrets im Diff · keine Out-of-Scope-Datei-Writes · Frozen Zone unberührt.** Das verhindert, dass ein einzelner Agent den Hauptstand vergiftet. Merksatz aus der Praxis: *Skill lehrt das Wie, Hook erzwingt die Regel, Subagent isoliert die Arbeit.*
- **Grader-Rubrik** als zweite Verifikationsschicht (Teil 3.5): jedes generierte Artefakt gegen eine explizite Rubrik, Überarbeitung erzwungen bis zum Bestehen.
- **Das Vier-Kategorien-Gate** läuft weiterhin als Merge-Gate — pro Strang *und* am integrierten Stand. Kein Strang wird zurückgemerged, der nicht grün ist.
- **Secret-Scan + Pre-Commit-Hook** bleiben aktiv; bei mehreren parallelen Schreib-Agenten steigt das Risiko versehentlich committeter Artefakte → `git add -A` ist im autonomen Lauf ein Hard-Stop.
- **Frozen-Zone-Pin** schützt mehrkonsumentige Verträge gegen *jeden* Agenten — kein autonomer Lauf ändert sie.

**Die Logik:** Je autonomer und paralleler, desto mehr verlagert sich Vertrauen von „der Agent macht das schon" zu „die Maschine *beweist*, dass jeder Beitrag die Regeln einhält, bevor er zählt".

---

## 6. Strategie für lange & sehr lange autonome Läufe

Ein 1 h+ / Nacht-Lauf ist kein *einzelner* Kontext, sondern eine **gemanagte Kette**. Sechs Bausteine:

### 6.1 Kontext-Budget-Management (der eigentliche Hebel)
- **Tranche-Sizing:** Jede Arbeitseinheit klein genug, dass sie in *einem* Kontext sauber abschließt (reviewbar, testbar, eingrenzbar, rücknehmbar). Lieber zehn saubere Tranchen als eine, die im Kontext erstickt.
- **Subagenten halten Verbose-Arbeit fern:** Recon, Test-Logs, Such-Dumps laufen *im Subagenten-Kontext*; nur die Zusammenfassung kehrt zurück. Der Lead-Kontext bleibt für Orchestrierung frei.
- **Dynamic Workflows verlagern Orchestrierung in Code:** der Hauptkontext sieht nur Endergebnisse → ermöglicht Läufe, die ein einzelner Kontext nie tragen könnte.
- **Saubere Fortsetzung über Sessions:** Wird der Kontext knapp → **nach der letzten fertigen Tranche stoppen + HANDBACK schreiben**; ein Folge-Lauf setzt fort. So wird „über Nacht" zu einer Kette bounded Runs, nicht zu einem degradierenden Mega-Kontext.

### 6.2 Der Orchestrator/Supervisor
Eine dünne, möglichst deterministische Steuerung (Skript oder Lead-Session), die:
- den **Abhängigkeitsgraphen** der Tranchen kennt und nur *bereite* Pakete dispatcht,
- unabhängige Pakete **parallel** auf Worktrees/Subagenten verteilt,
- **No-Progress / Loops erkennt** (kein Diff, gleiche Fehler N-mal) und den Strang **killt oder parkt**,
- am Ende einen **Morgen-Report** erzeugt (was fertig, was geparkt, Gate-Status, Kosten, offene Entscheidungen).

### 6.3 Fail-safe statt fail-open
- **Park, don't guess:** an Hard-Stop oder echter Ambiguität → parken + Worklog, nicht raten.
- **Max-Turn-/Iterations-Caps** pro Tranche; bei Überschreitung → parken.
- **Rotes Gate ohne klaren additiven Fix → parken.**
- Der Nacht-Lauf endet auf `main` (Arbeit lebt auf Branches), niemals mit halben Tranchen im Nebel.

### 6.4 Kosten-Cap & Alarm (bei Bypass + Max-Modell zwingend)
- **Harte Budget-Obergrenze** für den Lauf (Prepaid ohne Auto-Reload = physische Grenze).
- **Schätzung vor teuren Fan-outs**, **Stichprobe vor Masse**, **idempotente Wiederholung ohne Doppelkosten.**
- **Cost-Logging je Agent/Call**; der Orchestrator **stoppt am Cap** und alarmiert in Klartext.
- Besonders bei Dynamic Workflows (zig–hunderte Agenten) ist das Cap nicht optional.

### 6.5 Sandbox/Isolation für unbeaufsichtigte Nacht-Läufe
**Direkt an euer Setup (Claude Code auf dem Prod-VPS) gekoppelt — die schärfste Auflage:**
- Nacht-Läufe laufen in einem **separaten Worktree/Clone**, **niemals** gegen die Prod-Instanz.
- **Kein Live-DB-Write** (Tests nur gegen tmp/Kopie), **kein Restart/Push auf `main`** ohne grünes Gate, **kein `pip install`/Env-Mutation**, **Frozen Zone unberührt** — die Hard-Stops aus dem Playbook sind hier *existenziell*, nicht nur best practice.
- Ressourcen-Headroom prüfen: ein Agenten-Schwarm + Builds auf der Box, die *auch Prod hostet*, darf Prod nicht aushungern. Builds/UX-Tests bleiben aus dem Prod-Pfad (Cloud-CI).
- Mittelfristig: für ernsthafte Nacht-Autonomie **Dev-Agent und Prod auf getrennte Maschinen** (oder Auto-Deploy erst nach Gate aus einem isolierten Worktree).

### 6.6 Die Übergabe-Kette als durables Gedächtnis
- **Worklog (append-only)** pro Tranche: was gebaut, Dateien, Testresultat, Entscheidungen/Parks.
- **HANDBACK** am Lauf-Ende: Branch + SHA · Tranchen-Status · Gate-Resultat · Park-Liste · Entscheidungen/Ambiguitäten · Promotion-Rezept + Smoke-Marker.
- Der **Morgen-Quercheck** des Menschen liest Worklog + HANDBACK + Morgen-Report → prüft Urteils-/Geld-/Unumkehrbar-Punkte, dokumentiert nach, gibt frei. Genau dein Modell: „danach quer-checken, prüfen, notfalls dokumentieren".

---

## 7. Die Agent-Ready Roadmap (der Kern)

**Das ist die eigentliche Neuerung.** Eine Roadmap/ein Konzept definiert ab jetzt nicht nur *was* gebaut wird (Funktionsumfang, Use-Cases, Success-Factors), sondern encodiert **den Parallelisierungs- und Lauf-Plan**: *wie* ein Agenten-Schwarm es in langen, autonomen Läufen baut. Jedes Roadmap-Item trägt zusätzlich zu Scope/Akzeptanz folgende **agenten-spezifische Metadaten**:

### 7.1 Pflicht-Metadaten je Roadmap-Item

1. **Abhängigkeiten (DAG).** Welche Items müssen *vorher* fertig sein. Daraus ergibt sich der **kritische Pfad** (was *muss* seriell laufen) und die **parallelen Fronten** (was *gleichzeitig* laufen darf).
2. **Parallelisierbarkeits-Tag.** Genau einer von:
   - `serial` — gekoppelte Schreibarbeit; eine Single-Session-Tranche.
   - `parallel-read` — Recon/Review/Exploration; Subagenten/Team-Fan-out.
   - `parallel-write` — unabhängige Dateien/Module; Worktree-Sessions oder `isolation: worktree`.
   - `fan-out` — programmatisch über viele unabhängige Einheiten; Dynamic Workflow.
   - `frozen` — Vertrag/Frozen Zone; **nur seriell + Mensch-Checkpoint**, nie autonom.
3. **Tranche-Schnitt.** In wie viele *kontext-beschränkte* Einheiten das Item zerfällt (jede reviewbar/testbar/eingrenzbar/rücknehmbar). Ein Item, das nicht schneidbar ist, ist zu groß für einen autonomen Lauf.
4. **Maschinen-prüfbare Definition of Done.** *Welche Gates konkret* grün sein müssen (welche Test-Kategorien, welche Contract-/Smoke-Checks, welche Grader-Rubrik). „Done" muss von der Maschine *entscheidbar* sein — sonst kann der Agent nicht autonom abschließen.
5. **Datei-/Verzeichnis-Eigentum.** Welche Pfade das Item berührt → Grundlage für konfliktfreie Parallelisierung (zwei parallele Stränge dürfen sich nicht überlappen).
6. **Integrations-Reihenfolge.** In welcher Reihenfolge parallele Stränge zurückgemerged werden (und gegen welchen Gate-Stand).
7. **Checkpoints & Park-Punkte.** Wo der Mensch zwingend gebraucht wird (**Urteil/Geld/Unumkehrbarkeit**) und wo der Agent bei Ambiguität *parken* soll statt zu raten.
8. **Run-Sizing.** Grobschätzung: füllt das Item einen ~1-h-Lauf, einen Nacht-Lauf, oder ist es ein Mehr-Nacht-Epic (→ in HANDBACK-gekoppelte Läufe zerlegen).

### 7.2 Pro Roadmap-Phase: der „Agent-Lauf-Plan"

Über die Einzel-Items hinaus bekommt jede Phase einen kurzen **Lauf-Plan**:

- **Parallele Fronten:** welche Item-Gruppen *gleichzeitig* laufen können (disjunkte Datei-Eigentümer, keine offenen Abhängigkeiten).
- **Serieller Rückgrat-Pfad:** der kritische Pfad, der die Phase taktet.
- **Orchestrierungs-Form je Front:** Subagenten-Panel / Worktree-Sessions / Agent Team / Dynamic Workflow.
- **Gate-/Integrations-Punkte:** wann zusammengeführt und gegen welchen Stand geprüft wird.
- **Nacht-Lauf-Kandidaten:** welche Fronten sich für unbeaufsichtigte Läufe eignen (hoher Autonomie-Anteil, wenige Checkpoints, klare maschinelle DoD) — und welche *nicht* (Frozen Zone, Urteils-/Geld-Punkte).

### 7.3 Die Konzept-Phase denkt Parallelität mit

Schon bei der Konzeption (nicht erst bei der Roadmap) gilt:
- **Architektur additiv schneiden**, damit mehr Arbeit `parallel-write`-fähig wird (neue Tabellen/Routen/Module statt invasiver Eingriffe in geteilten Code).
- **Verträge früh einfrieren** (Frozen Zone), damit parallele Konsumenten unabhängig bauen können.
- **Eine Wahrheit je Datensorte** verhindert, dass parallele Agenten um dieselbe Quelle konkurrieren.
- **Maschinen-prüfbare Akzeptanz** von Anfang an mitdenken — ein Success-Factor, der nicht testbar ist, blockiert Autonomie.

> **Kurz:** Ein gut geschnittenes Konzept *maximiert die parallelisierbare Fläche* und *minimiert die Checkpoints* — das ist die Voraussetzung für lange, autonome Läufe.

---

## 8. Konkrete Claude-Code-Setup-Checkliste

Für den Max-Autonomie-Modus (neuestes Modell, max Aufwand, Bypass) — mit den nötigen Gegengewichten:

**Agenten & Rollen**
- [ ] `.claude/agents/` mit den Rollen aus Teil 4 (explorer, planner, test-author, implementer, review-Panel, integrator, ops-debugger), **Tools je Rolle explizit skopiert** (nicht weglassen!), **Modell je Rolle geroutet** (günstig für Read-only, stark für Synthese).
- [ ] Agent Teams nur dort aktivieren, wo Worker *kommunizieren* müssen (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) — sonst Subagenten.
- [ ] Sweet Spot **3–5 gleichzeitige** Subagenten respektieren; Fan-out auf zig–hunderte nur via Dynamic Workflow für sauber auffächernde Jobs.

**Gates & Hooks (das Sicherheitsnetz)**
- [ ] **SubagentStop-Hook**: Tests grün · keine Secrets im Diff · keine Out-of-Scope-Writes · Frozen Zone unberührt — *bevor* zurückgemerged wird.
- [ ] Pre-Commit-Hook (Secret-Scan + ruff-kritisch) aktiv; `git add -A` als Hard-Stop.
- [ ] Vier-Kategorien-Gate pro Strang *und* am integrierten Stand.
- [ ] Grader-Rubrik für generierte Artefakte definiert.

**Isolation (zwingend bei Prod-VPS)**
- [ ] Nacht-Läufe in **separatem Worktree/Clone**, nie gegen die Prod-Instanz; `isolation: worktree` für parallele Schreib-Subagenten.
- [ ] Hard-Stops scharf: kein Live-Write, kein Push/Restart ohne Gate, kein `pip install`, Frozen Zone tabu.
- [ ] Ressourcen-Headroom geprüft; Builds/UX-Tests aus dem Prod-Pfad (Cloud-CI).

**Lange Läufe**
- [ ] Tranchen klein geschnitten; Worklog (append-only) + HANDBACK verdrahtet.
- [ ] Orchestrator mit Abhängigkeitsgraph, No-Progress-/Loop-Watchdog, Max-Turn-Caps, Morgen-Report.
- [ ] **Kosten-Cap + Low-Credit-Alarm**; Orchestrator stoppt am Cap.
- [ ] Headless-Start (`claude -p` / SDK) für unbeaufsichtigten Betrieb; Lauf endet auf `main`.

**Steuerung**
- [ ] `CLAUDE.md` referenziert diese Strategie und die Rollen; globale Prinzipien oben, lokale Spezifika in Unterordnern.
- [ ] Slash-Commands für wiederkehrende Lauf-Typen (z. B. „review-panel", „spec-to-docs").

---

## 9. Reifegrad-Stufenplan

**Nicht überspringen — jede Stufe wird mit tragfähigen Gates verdient.** Multi-Agent-Autonomie auf dünnem Test-Fundament ist ein Brandbeschleuniger.

| Stufe | Was | Voraussetzung |
|---|---|---|
| **0 — Single-Session-Tranchen** | Eine Session, ein Tranchen-Zyklus, eng geführt. | Tranchen-Disziplin + ein grünes Gate. |
| **1 — Subagenten** | Parallele Recon/Exploration + Review-Panel (Writer ≠ Reviewer). Built-ins Explore/Plan nutzen. | SubagentStop-Hook + Vier-Kategorien-Gate. |
| **2 — Worktree-Sessions** | Mehrere unabhängige Code-Stränge parallel, du integrierst. | Saubere Datei-Eigentümer + Integrations-Reihenfolge. |
| **3 — Agent Teams** | Schichtübergreifende Änderungen + konkurrierende-Hypothesen-Debugging. | Stabile Gates + Kosten-Logging (Teams sind token-teuer). |
| **4 — Dynamic Workflows + Nacht-Orchestrierung** | Fan-out auf zig–hunderte Agenten, Grader-Loop, unbeaufsichtigte Läufe. | Kosten-Cap + Sandbox-Isolation + Watchdog + Morgen-Report. |

Pro Projekt dort einsteigen, wo die Gates es tragen — und erst hochstufen, wenn die jeweilige Voraussetzung *bewiesen* (nicht geglaubt) ist.

---

## 10. Roadmap-Item-Template (zum Kopieren)

```markdown
### [R-042] <Item-Titel>

**Scope / Use-Case:** <was & warum, ein Absatz>
**Success-Factors (maschinen-prüfbar):** <welche messbaren Kriterien>

— Agent-Metadaten —
- **Abhängigkeiten:** [R-040, R-041]        # leer = parallele Front
- **Parallelisierbarkeit:** parallel-write   # serial | parallel-read | parallel-write | fan-out | frozen
- **Orchestrierung:** Worktree-Sessions      # Single-Session | Subagenten-Panel | Agent Team | Dynamic Workflow
- **Tranche-Schnitt:** 3                      # Anzahl kontext-beschränkter Einheiten
- **Datei-Eigentum:** src/api/items/, tests/test_api_item_*.py
- **Definition of Done (Gates):** Kat.1+Kat.3 grün · Contract-Test items_v2 · Smoke /api/v2/items 200 · Grader „items-crud" ≥ Schwelle
- **Integrations-Reihenfolge:** nach R-040, vor R-045
- **Checkpoints (Mensch):** keine            # bzw. „Urteil: Migration realer Bestand"
- **Park-Punkte:** bei Schema-Ambiguität → parken
- **Run-Sizing:** 1-h-Lauf                    # 1-h | Nacht | Mehr-Nacht-Epic
- **Nacht-Lauf-tauglich:** ja
```

---

## 11. Master-Checkliste

**Parallelisierung** — Lese-/explorationslastig+unabhängig → parallel; schreib-koordiniert+sequenziell → seriell · richtiges Primitiv wählen (Subagent/Team/Workflow/Worktree) · 3–5 Subagenten-Sweet-Spot · disjunktes Datei-Eigentum · Frozen Zone nie parallel/autonom.

**Orchestrierung** — fan-out→reduce→synthesize · Review-Panel (Writer≠Reviewer) · konkurrierende-Hypothesen-Debugging · spec→code→test→docs-Pipeline · Grader-Loop · Lead schreibt wenig Code.

**Gates als Netz** — SubagentStop-Hook (Tests/Secrets/Scope/Frozen) vor Merge-back · Grader-Rubrik · Vier-Kategorien-Gate pro Strang + integriert · Secret-Scan · `git add -A` = Hard-Stop.

**Lange Läufe** — Tranchen klein · Subagenten halten Verbose-Arbeit fern · Workflows verlagern Orchestrierung in Code · Kontext knapp → stoppen+HANDBACK · Orchestrator mit DAG/Watchdog/Caps/Morgen-Report · Kosten-Cap+Alarm · Sandbox-Isolation (nie Prod-Instanz) · fail-safe statt fail-open · Ende auf `main`.

**Agent-Ready Roadmap** — je Item: DAG · Parallelisierbarkeits-Tag · Tranche-Schnitt · maschinen-prüfbare DoD · Datei-Eigentum · Integrations-Reihenfolge · Checkpoints/Park-Punkte · Run-Sizing · je Phase: Agent-Lauf-Plan · Konzept maximiert parallele Fläche, minimiert Checkpoints.

**Reifegrad** — Stufe 0→4 nicht überspringen; jede Stufe mit bewiesenen Gates verdienen.

---

*Companion zu `ENGINEERING_PLAYBOOK.md`. Lebendes Dokument — fortschreiben wie jedes andere. Die Tool-Spezifika (Agent Teams, Dynamic Workflows) sind Stand 2026 und entwickeln sich schnell; die Prinzipien — Parallelisierbares parallelisieren, Autonomie durch Guardrails, lange Läufe als gemanagte Tranchen-Kette — bleiben.*
