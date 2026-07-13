# Engineering-Playbook — Best Practices für KI-gestützte Software-Entwicklung

**Destilliert aus zwei realen Projekten: `capsule` (Wardrobe-/Ontologie-/Ingest-System) und `boxscore` (selbst-gehostete NFL-Wissensplattform).**

> **Zweck.** Dieses Dokument ist eine **projekt-unabhängige, wiederverwendbare Methodik** als Grundlage für künftige Software-Projekte. Es beschreibt *wie* gearbeitet wird — Methodik, Werkzeugkette, Test-Strategie, UX, Debugging, Deployment (insbesondere VPS), Handoff-Management und die Zusammenarbeit Mensch ↔ Claude Code. Projekt-Spezifika sind nur dann erwähnt, wenn sie ein Verfahren konkret machen.
>
> **Quellenlage.** Beide Projekte teilen dieselbe DNA, repräsentieren aber **zwei Reifegrade derselben Methodik**: `capsule` ist der Ursprung des Playbooks und zeigt die Evolution von eng geführter ChatGPT-Arbeit hin zum autonomen Agenten; `boxscore` ist die saubere „Greenfield"-Umsetzung mit voll realisierter Auto-Deploy-Kette. Wo sich „Ist" und „Ziel" unterscheiden, ist das markiert — gerade diese Ehrlichkeit ist Teil der Methode.
>
> **Sprachkonvention (übernommen).** Dokumentation & Kommunikation auf **Deutsch**; Code, Identifier, Commits, Branch-Namen auf **Englisch**.

---

## Inhaltsverzeichnis

1. [Kernthese in einem Satz](#1-kernthese-in-einem-satz)
2. [Die 13 Leitprinzipien](#2-die-13-leitprinzipien)
3. [Arbeitsmodell: Mensch + KI-Agent](#3-arbeitsmodell-mensch--ki-agent)
4. [Claude Code & die Werkzeugkette](#4-claude-code--die-werkzeugkette)
5. [Dokumenten-getriebene Entwicklung](#5-dokumenten-getriebene-entwicklung)
6. [Die Tranche — Bau- und Planungseinheit](#6-die-tranche--bau--und-planungseinheit)
7. [Architektur für Robustheit & Resilienz](#7-architektur-für-robustheit--resilienz)
8. [Test-Strategie (das Herzstück)](#8-test-strategie-das-herzstück)
9. [UX: Design und sein Test](#9-ux-design-und-sein-test)
10. [KI-Verifikations-Gates](#10-ki-verifikations-gates)
11. [Debugging](#11-debugging)
12. [Deployment & Betrieb — VPS-Fokus](#12-deployment--betrieb--vps-fokus)
13. [Sicherheit & Kosten](#13-sicherheit--kosten)
14. [Handoff-Management & durables Gedächtnis](#14-handoff-management--durables-gedächtnis)
15. [CI/CD & Governance](#15-cicd--governance)
16. [Bauplan für ein neues Projekt](#16-bauplan-für-ein-neues-projekt)
17. [Reifegrad-Vergleich der beiden Projekte](#17-reifegrad-vergleich-der-beiden-projekte)
18. [Master-Checkliste](#18-master-checkliste)
19. [Anhang: Werkzeug- & Befehls-Referenz](#19-anhang-werkzeug--befehls-referenz)

---

## 1. Kernthese in einem Satz

**Ein Mensch gibt Richtung und trifft die *wenigen* echten Entscheidungen; ein KI-Agent baut, prüft und betreibt maximal automatisiert — und nichts gilt als fertig, weil es plausibel aussieht, sondern erst, wenn ein automatischer Test es gegen die Wahrheit geprüft hat.**

Alles Weitere in diesem Dokument ist eine Ausfaltung dieses Satzes. Zwei Konsequenzen sind nicht verhandelbar und kehren überall wieder:

- **Gates statt Gefühl** — und **Gates werden nie aufgeweicht, um Tempo zu machen** (die wichtigste Einzelregel beider Projekte).
- **Verifizierbar statt vertrauensselig** — Plausibilität ist kein Nachweis; ein Test gegen etwas Maßgebliches schon.

---

## 2. Die 13 Leitprinzipien

Diese Prinzipien stammen wörtlich aus der gelebten Praxis und bilden den unveränderlichen Kern. Jedes neue Projekt erbt sie.

| # | Prinzip | Bedeutung in der Praxis |
|---|---------|-------------------------|
| 1 | **Verifizierbar statt vertrauensselig** | Code, Daten und KI-Output gelten nur, wenn ein Test sie gegen etwas Maßgebliches geprüft hat. |
| 2 | **Gates statt Gefühl — nie aufweichen** | Grün = darf live; Rot = Stopp, zuerst die *Ursache* reparieren. Niemals `--no-verify`, niemals rote Tests „durchwinken". |
| 3 | **Experience-first, vertikaler Schnitt** | Erst *eine* Sache komplett end-to-end (Daten → Produkt → live → getestet), dann in die Breite. Kein monatelanges Vorarbeiten ohne benutzbares Produkt. |
| 4 | **Eine Wahrheit je Datensorte** | Genau *eine* maßgebliche Quelle je Informationsart. Konflikt = Fehler, kein stilles Überschreiben. |
| 5 | **Kleine Tranchen, ständig integriert** | Ein immer auslieferbarer Hauptzweig, kurzlebige Branches, häufige Integration. Keine großen Sammelrefactorings, keine Code-Freezes. |
| 6 | **Correctness vor Cleverness; Reproduzierbarkeit vor implizitem Wissen** | Was nicht reproduzierbar und dokumentiert ist, existiert für das Projekt nicht. |
| 7 | **Additiv vor invasiv** | Neue Felder/Tabellen/Routen werden additiv eingeführt; bestehende Verträge bleiben unberührt. Breaking Changes sind ein bewusster, versionierter Akt. |
| 8 | **Dokumente sind das Rückgrat** | Entscheidungen, Pläne, Datenstrategie, Worklogs, Betriebshandbuch leben als versionierte Dateien — das Langzeitgedächtnis von Mensch *und* Agent. |
| 9 | **Maximal automatisiert, minimal manuell** | Jeder wiederkehrende Handgriff wird zur Pipeline. Manuell nur, wo **Urteil, Geld oder Unumkehrbarkeit** im Spiel sind. |
| 10 | **Anmutige Entartung statt Totalausfall** | Fehlt eine optionale Quelle, läuft das Produkt *degradiert* weiter statt zu crashen. |
| 11 | **Zero-Trust gegenüber KI-Output** | Wo eine KI erzeugt, ersetzt automatische Verifikation gegen eine Quelle der Wahrheit das menschliche Review. |
| 12 | **Sicherheit & Kosten als Leitplanken** | Keine Geheimnisse im Code, geringste Rechte, kein offener Port; bei bezahlten Diensten harte Obergrenze. |
| 13 | **Wenige echte Entscheidungspunkte** | Der Agent arbeitet durchgehend autonom; der Mensch wird nur an wenigen, klar definierten Checkpoints gebraucht. Alles andere ist Statusinfo. |

---

## 3. Arbeitsmodell: Mensch + KI-Agent

### 3.1 Rollenteilung

Der Agent ist **kein Zeile-für-Zeile dirigierter Code-Generator**, sondern ein Ingenieur mit Werkzeugen, Gedächtnis und der Fähigkeit zu iterieren. Drei Rollen, klar getrennt:

| | Mensch (Eigentümer) | Architekten-Chat | Executor-Session (Agent) |
|---|---|---|---|
| **Aufgabe** | Richtung, Prioritäten, die wenigen echten Entscheidungen, elevierte Schritte | plant, entscheidet, liefert fertige Prompts, reviewt Reports | baut, testet, committet, berichtet, hält an Go/No-Go-Punkten an |
| **Eingriff** | High-Level-Ziele, Freigaben an Checkpoints | zerlegt in Tranchen, formuliert das Konzept | arbeitet end-to-end pro Runde, meldet Status |
| **Werkzeug** | Urteil, Freigabe („deploy") | Chat, Konzept-Dokumente | Dateisystem, Shell, Git, DB, Tests, Logs |

**Architekt ≠ Executor.** Planung/Entscheidung und Umsetzung/Test sind getrennte Rollen — auch wenn dasselbe Modell beide spielen kann. Das ist eine Form des **Writer ≠ Reviewer**-Musters: Eine *frische* Sitzung (oder ein Sub-Agent) prüft härter als die, die den Code geschrieben hat. Dasselbe gilt für Tests — eine Instanz schreibt Tests, eine andere den Code.

### 3.2 Die Evolution des Arbeitsmodus (eine wichtige Lektion)

Die beiden Projekte dokumentieren eine echte Reifung, die man bei der nächsten Projektgründung berücksichtigen sollte:

- **Phase „Single Step Rule" (ChatGPT-Ära, frühes capsule).** Pro Runde *genau ein* Schritt; Mensch prüft Output, gibt dann den nächsten Schritt; vollständige Datei statt Diff-Schnipsel; skeptisch arbeiten, erst messen, dann ändern. Stark bei Kontrolle, langsam bei Durchsatz.
- **Phase „Autonomer Lauf" (Claude-Code-Ära, reifes capsule + boxscore).** Self-driven über einen Tranchen-Backlog; pro Tranche bauen → testen → committen → Worklog; nicht mid-run nachfragen; live-mutierende Schritte werden geparkt. Hoher Durchsatz, abgesichert durch Gates.

**Empfehlung:** Mit der Single-Step-Disziplin starten, solange das Test-Fundament dünn ist; auf den autonomen Modus umstellen, sobald die Gates tragfähig sind. Die Gates sind die Voraussetzung für Autonomie — ohne sie kein autonomer Lauf.

### 3.3 Onboarding-Disziplin (jede frische Session)

Eine neue Executor-Session startet **read-only** und macht sich arbeitsfähig, *bevor* sie irgendetwas ändert:

1. **Session-Brief / Arbeitsregeln vollständig lesen** (ein Dokument, das allein arbeitsfähig macht — `CLAUDE.md`).
2. **Read-only verifizieren:** `git log`/HEAD = erwarteter Stand; `git status` clean bis auf bekannte Artefakte; Health-Endpoints liefern `200`.
3. **Rolle bestätigen** (ein Satz: was das Produkt ist, eigene Rolle, die eisernen Regeln) — dann warten.
4. **Konfliktregel:** Widerspricht ein Dokument dem Repo-/Live-Zustand, gilt **Repo/Live**. Bei Unklarheit: **fragen statt raten.**

### 3.4 Das Protokoll für den autonomen Lauf

Wenn der Agent autorisiert lange durchläuft, gelten **Hard-Stops (ausnahmslos):**

- **Kein Live-DB-Write** (Tests nur gegen Kopie/tmp).
- **Kein Restart / Merge / Push / Promotion** (das sind Mensch-Schritte bzw. Checkpoints).
- **Frozen Zone unberührt** (öffentliche API-Verträge, geteilte Taxonomie, geteilter Lesepfad).
- **Keine neue Dependency / kein `pip install` / kein Mutieren des Live-Environments.**
- **Keine Secrets/PII**, **kein `git add -A`**.

Verhalten an den Grenzen:

- **Parken statt raten.** An einem Hard-Stop oder bei echter Design-Ambiguität → **PARKEN + Worklog**, nicht raten, nicht mid-run nachfragen. Der Architekten-Chat entscheidet später.
- **Rotes Test/Gate ohne klaren additiven Fix → PARKEN.**
- **Kontext-Budget ist der eigentliche Limiter.** Wird der Kontext knapp, sauber nach der letzten fertigen Tranche stoppen + HANDBACK schreiben. Lieber eine Tranche weniger, sauber übergeben, als eine halbe Tranche im Nebel.
- **Pro Tranche committen** (nie ein Riesen-Commit am Ende).
- **Lauf endet auf `main`** (Arbeitskopie zurückgesetzt; die Arbeit lebt auf dem Branch).

**Stop-Regel allgemein:** Bei rotem Check oder echter Unklarheit → STOPP, Befund melden, kein Fix/Workaround ohne Freigabe. *Anhalten ist eine Stärke, kein Versagen.*

---

## 4. Claude Code & die Werkzeugkette

### 4.1 `CLAUDE.md` — die „operative Verfassung"

Beide Projekte haben eine `CLAUDE.md` im Repo-Root, die der Agent **automatisch lädt**. Sie ist das Langzeitgedächtnis und der Arbeitsvertrag. Bewährter Aufbau:

- **Hierarchie der Wahrheiten** an den Anfang: welches Dokument bei Widerspruch gilt (z. B. Methodik > Engineering-Manifest > Architektur-Dossier > Projekt-Stand).
- **Projekt in einem Absatz** (Stack, Topologie, öffentliche Endpunkte).
- **Entscheidungslog** (bei `boxscore`: E1–E14) — jede Grundsatzentscheidung nummeriert, mit Kern und verbindlicher Konsequenz.
- **Standard-Kommandos** der Umgebung (siehe 4.2).
- **Die eisernen Regeln** (Gates nie aufweichen, nie in `staging`/`prod` schreiben, keine Secrets committen, kein `git add -A`).
- **GOTCHAs & bekannte Verstöße — ehrlich dokumentiert.** `capsule` listet offen auf, welche Marker gerade „0 Tests" selektieren, welche Idempotenz fehlt, welcher Token „untracked aber nicht gitignored" ist. Diese radikale Ehrlichkeit über technische Schuld ist eine bewusste Methode: Der Agent stolpert nicht in bekannte Fallen.
- **Arbeitsmodus** (kleine Schritte, nur bei Entscheidung/Secret melden, Wartezeit = Arbeitszeit → nächstes unabhängiges Paket vorziehen).

> **Muster zum Übernehmen:** Die `CLAUDE.md` leitet sich aus einem kanonischen Stand-Dokument ab (`PROJEKT_STAND.md` / `PROJECT_STATE.md`) und macht dessen Entscheidungen für die *tägliche* Arbeit konkret. Änderungen an den Regeln nur mit ausdrücklicher Freigabe des Eigentümers.

### 4.2 Ein kanonischer Befehls-Einstiegspunkt

Statt vieler verstreuter Skripte gibt es **eine** Kommando-Oberfläche, die alles delegiert (ADR-0011). Bei `capsule`: ein `task_runner.py`, gewrappt in `capsule.cmd` / `capsule.ps1`. Beispiele:

```powershell
capsule.cmd quality-gates     # das Merge-Gate (compile, ruff-critical, pytest, secret-scan, live-smoke)
capsule.cmd test              # vollständige pytest-Suite
capsule.cmd server            # App lokal starten
capsule.cmd handoff           # Handoff-Artefakte erzeugen
capsule.cmd snapshot          # Snapshot für Chat-Umzug
capsule.cmd audit             # Projekt-Audit
capsule.cmd secret-scan --mode tracked
capsule.cmd release-evidence --release-id <id>
```

Der Wrapper löst `.venv\Scripts\python.exe` zuerst auf und fällt nur auf `python` zurück, wenn kein venv da ist. **Eine** vorhersagbare Befehls-Oberfläche für tägliche Arbeit, Onboarding und Release/Handoff.

### 4.3 VS-Code-Integration

`.vscode/tasks.json` **spiegelt exakt** die kanonischen Einstiegspunkte — kein zweiter, abweichender Workflow:

```json
{
  "version": "2.0.0",
  "tasks": [
    { "label": "capsule: quality-gates", "type": "shell", "command": "${workspaceFolder}\\capsule.cmd quality-gates" },
    { "label": "capsule: tests",         "type": "shell", "command": "${workspaceFolder}\\capsule.cmd test" },
    { "label": "capsule: server",        "type": "shell", "command": "${workspaceFolder}\\capsule.cmd server" },
    { "label": "capsule: handoff",       "type": "shell", "command": "${workspaceFolder}\\capsule.cmd handoff" },
    { "label": "capsule: snapshot",      "type": "shell", "command": "${workspaceFolder}\\capsule.cmd snapshot" },
    { "label": "capsule: audit",         "type": "shell", "command": "${workspaceFolder}\\capsule.cmd audit" }
  ]
}
```

**Prinzip:** Lokal (Terminal), VS Code (Task-Runner) und CI fahren *dieselben* Befehle. Ein Entwickler muss nichts „erfinden"; die Maschine und der Mensch tun dasselbe.

### 4.4 Git-Hooks als erste Verteidigungslinie

Ein **Pre-Commit-Hook** erzwingt Disziplin *vor* dem Commit (aus `tools/hooks/pre-commit`):

```bash
# 1) Secret-Scan über die gestageten Dateien
"$PY" tools/secret_scan.py --mode staged
# 2) ruff "kritisch" nur auf gestagete Python-Dateien (Syntax/Undefined-Name-Klassen)
"$PY" -m ruff check --select E9,F63,F7,F82 "${PY_FILES[@]}"
```

Damit kann ein Secret oder ein Syntaxfehler gar nicht erst in die Historie gelangen. Der Hook bevorzugt das venv-Python und wird per `install_git_hooks.ps1` eingerichtet.

### 4.5 Inventar der Werkzeugkette (vollständig)

Was in beiden Projekten zur Tool-Chain gehört — als Vorlage für künftige Projekte:

| Bereich | Werkzeuge / Artefakte |
|---|---|
| **Agent-Steuerung** | `CLAUDE.md` (auto-geladene Verfassung), Architekten-Chat ↔ Executor-Session, Worklog + HANDBACK |
| **Befehls-Oberfläche** | `task_runner.py` / `capsule.cmd` / `capsule.ps1`, gespiegelt in `.vscode/tasks.json` |
| **Editor** | VS Code mit Tasks; PowerShell als Standard-Shell (Windows-VPS) |
| **Sprache/Runtime** | Python **3.12** verbindlich, isoliertes `.venv`; Node LTS für Web/UX-Tests |
| **Tests** | pytest (+ Marker-Kategorien), Vitest (Web-Units), Playwright + axe + Lighthouse (UX) |
| **Lint/Format** | `ruff` (im Gate nur „kritische" Selektion; voller Lauf im berührten Code) |
| **Quality Gate** | `run_quality_gates.py` (compile · ruff-kritisch · pytest · secret-scan · live-smoke) |
| **Sicherheit** | `secret_scan.py` (staged/tracked), `security_inventory.py`, `security_hygiene_report.py`, Dependabot |
| **Diagnose** | `quality_gate_diagnose.py`, `ops_report_index.py`, `runs_report.py` |
| **Handoff** | `handoff_make.py` / `.ps1`, `handoff_snapshot.ps1`, `release_evidence.py`, `final_readiness_report.py` |
| **Ops (VPS)** | PowerShell-Skripte für Runner-Setup, Deploy, Backup, Restore-Probe, Watchdog, Health |
| **CI/CD** | GitHub Actions (Cloud-Runner *oder* self-hosted VPS-Runner), Branch-Protection-Config im Repo |
| **Release-Manifest** | `product-state.json` (Quelle der `/status`-Seite) |
| **Doku** | `docs/` mit Methodik, ARD, ADRs, Runbooks, Worklogs, Release-Notes |

---

## 5. Dokumenten-getriebene Entwicklung

Dokumente tragen das Gedächtnis über Sitzungen, Abstürze und Neustarts hinweg. **Git ist die Drehscheibe:** jede Änderung — Code *und* generierte Inhalte — fließt über Git; die Historie ist Versions- und Herkunftsspur. **Architekturwissen darf nie exklusiv im Chat liegen.**

### 5.1 Der Doku-Kanon

| Dokument | Rolle |
|---|---|
| **Projekt-Stand / „Verfassung"** | Was wird gebaut (ein Absatz) + **Entscheidungslog** (jede Grundsatzentscheidung nummeriert, mit Kern und Begründung). Wird fortgeschrieben, nie weggeworfen. |
| **Roadmap / Phasenplan** | Bausteine, Reihenfolge, **Definition of Done je Phase**, Abhängigkeiten, Eigentümer-Checkpoints. |
| **Architektur-Referenz (ARD)** | Das kanonische Architekturdokument. Pflicht-Lektüre *vor* architekturwirksamen Änderungen; bei jeder solchen Änderung zu erweitern. |
| **Datenstrategie** | Quellenkatalog, kanonische Schlüssel, „Wahrheits-Quelle je Feld", Quer-Check-Matrix, Schema-Evolution. |
| **Release-Management + Release-Notes** | Scope, Change-Umfang, Testnachweise, bekannte Einschränkungen. Releases sind **Pflichtartefakte**. |
| **ADRs** | Jede Architekturentscheidung explizit, nummeriert, mit Kontext/Entscheidung/Konsequenz. |
| **Runbook / Betriebshandbuch** | Was läuft wann, wo die Logs liegen, Rollback/Restore, **besonders: was nach einem Neustart zu tun ist** — am besten **außerhalb des Servers** abgelegt. |
| **Agent-Arbeitsregeln** (`CLAUDE.md`) | Projektkonventionen, Standard-Befehle, Stolpersteine, die eisernen Regeln. |
| **Worklog + HANDBACK** | Append-only Tranchen-Protokoll + finale Übergabe = das durable Gedächtnis eines Laufs. |

### 5.2 Doku-Governance (die harte Regel)

Bei **architektur-/infra-/security-/API-/persistenz-/release-wirksamen** Änderungen sind die betroffenen Referenzdokumente **im selben Arbeitsblock** zu aktualisieren. **Eine Änderung ohne konsistente Doku gilt als unvollständig.** Das ist Teil der Definition of Done.

### 5.3 ADRs in der Praxis

`capsule` führt ~28 ADRs in `docs/adr/` mit einem `ADR-INDEX.md`. Jedes ADR ist nummeriert (`ADR-NNNN-titel.md`) und behandelt eine Entscheidung: Co-Hosting zweier Frameworks, SQLite+Dateisystem-Split, Public-Exposure (Cloudflare/ngrok), CI-Required-Checks, Branch-Protection, Deep-Health-Checks, SQLite-WAL-Modus, OpenAI-Client-Resilienz, Logging-Konsolidierung, …

> **Lektion zur Governance-Hygiene:** Der ADR-Index dokumentiert *offen* eine Altlast — die Nummern 0001–0005 wurden in zwei parallelen Serien doppelt vergeben. Statt es zu verstecken, steht im Index der Hinweis und die Regel „neue ADRs ab der nächsten freien eindeutigen Nummer". **Bekannte Schuld wird benannt, nicht kaschiert** — das ist durchgängiges Muster.

---

## 6. Die Tranche — Bau- und Planungseinheit

Jede Änderung wird als **Tranche** geplant und umgesetzt.

### 6.1 Der Bauzyklus je Tranche

**Erkunden → Planen → Umsetzen → Prüfen → Committen → Worklog.**

1. **Erkunden (read-only).** Relevante Quellen lesen — ausdrücklich *noch nicht* coden. Bei Unbekanntem eine **Recon** mit Datei-/Zeilen-Belegen. Lieber einmal zu viel den echten Code prüfen als aus dem Gedächtnis bauen.
2. **Planen.** Die Tranche klein und klar abgrenzen. Konzept festhalten.
3. **Umsetzen.** Additiv, im Stil des umgebenden Codes (Kommentar-Dichte, Namen, Idiome übernehmen).
4. **Prüfen.** Compile + Lint-kritisch + Tests **gegen Kopie-/tmp-Daten** (nie gegen Live). Jeder Bugfix bringt einen **Regressionstest** mit.
5. **Committen — explizit.** Nur die gewollten Dateien stagen (`git add <pfad> …`); **nie `git add -A`**. **Conventional Commits.**
6. **Worklog.** Ein Append-only-Eintrag: was gebaut, welche Dateien, Testergebnis, Entscheidungen/Parks.

### 6.2 Jede Tranche muss klein genug sein, dass sie

- nachvollziehbar reviewbar ist,
- testbar ist,
- bei Problemen eingrenzbar ist,
- ohne unnötigen Seiteneffekt zurückgenommen werden kann.

**Große Sammelrefactorings ohne klaren Zwischenzustand sind unzulässig.**

### 6.3 Definition of Done

Eine Tranche ist fertig, wenn: **Scope umgesetzt · relevante Tests grün · keine offenen bekannten Brüche im Scope · Doku aktualisiert · Zielrelease zugeordnet · bei Bedarf Handoff/Snapshot erstellt.**

### 6.4 Branch-Strategie (eine teuer gelernte Regel)

- Feature-Branch **immer von aktuellem `main`** (z. B. `feat/<thema>`). Zweigt er von *altem* `main` ab, fehlt ihm seither gemergter Code — **ein Deploy auf so einen Branch rollt diesen Code zurück.**
- `main` ist **jederzeit auslieferbar** und der **saubere Rollback-Anker**.
- Höchstens wenige aktive, kurzlebige Branches; häufige Integration. **Trunk-based.**

### 6.5 Conventional Commits

Format: `type(scope): kurze Beschreibung` — Imperativ, klein, ohne Punkt.

- **Typen:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `perf`, `build`, `style`, `revert`.
- **semver-Wirkung:** `fix`→patch, `feat`→minor, `!` / `BREAKING CHANGE`→major.
- `capsule` nutzt zusätzlich ein **Tranche-Präfix**: `T-XYZ(scope): kurzbeschreibung (vX.Y.Z)` — jeder Commit ist einer Tranche *und* einem Zielrelease zugeordnet.

Beispiele:
```
feat(pipeline): add nflverse schedule adapter
fix(web): correct breadcrumb on week hub
ci: run four test categories as parallel jobs
```

---

## 7. Architektur für Robustheit & Resilienz

Diese Muster machen ein System überhaupt erst auto-deploybar und betreibbar.

### 7.1 Eine Wahrheit je Datensorte

Lege fest, welches System für welche Information maßgeblich ist. Beispiel-Mapping (`capsule`):

- **Zahlen/Bestand → die DB** (SQLite bzw. DuckDB).
- **Generierte Texte/Doku → Git.**
- **Vokabular/Taxonomie → Ontologie-Dateien** (`*.md` + `*.yaml`), *nicht* DB-Spaltenwerte.
- **Aussehen → Design-Tokens.**

Bei Konflikt entscheidet eine vorab definierte Vorrang-Quelle; eine Abweichung jenseits Toleranz ist ein **Fehler** (Stopp + Alarm), kein stilles Überschreiben.

### 7.2 Medallion + Adapter für Daten

`raw → staging → marts` (roh → bereinigt/typisiert → geschäftsfertig).

- **Roh ist die Versicherung** (nie transformieren).
- **In der bereinigten Schicht verstecken sich die Bugs** (hier am meisten testen).
- Jede neue Quelle = **ein neuer Adapter** mit Feld-Contract (`fetch → validate → parse`), **ohne Umbau des Kerns**.

### 7.3 Idempotenz überall

Jeder Lauf (Ingest, Build, Deploy, Generierung) darf beliebig oft wiederholt werden und führt zum selben Ergebnis — ohne Dubletten, ohne Doppelkosten.

### 7.4 Strikte Trennung Dev / Staging / Prod

Der Agent editiert *nur* den Arbeitsbereich. In Prod gelangt Code **ausschließlich über den Deploy-Pfad — nie von Hand.** Bei `boxscore` ist das als Verzeichnislayout hart verdrahtet:

```
C:\boxscore\repo\      ← Arbeitsbereich (dev) — HIER wird editiert
C:\boxscore\staging\   ← Staging-Instanz (nur via Auto-Deploy aus Git)
C:\boxscore\prod\      ← Produktion (nur via Auto-Deploy aus Git)
C:\boxscore\data\      ← Datenbank & abgeleitete Daten (Laufzeit, nicht im Repo)
C:\boxscore\logs\      ← strukturierte Logs (Laufzeit)
C:\boxscore\backups\   ← Backups (Laufzeit)
```

### 7.5 Der eingefrorene Vertrag (Frozen Zone)

Verträge mit mehreren Konsumenten (öffentliche API, geteilte Taxonomie, geteilter Lesepfad) sind **eingefroren und maschinell gepinnt**: ein Snapshot-/Contract-Test schlägt fehl, sobald sich die Form ändert. **Nur additive Erweiterungen**; Breaking Change → neue Version (`/api/v3`), bewusste Entscheidung. (Bei `capsule` ist die `/api/v2` der *eine* kanonische Vertrag für Web *und* die parallele React-Native/Expo-App — ein Grund, ihn einzufrieren.)

### 7.6 Additive Schema-Evolution (erprobtes Muster)

Neue Tabelle/Spalte: `_CREATE_…_SQL` + Guard (`if not table_exists`) + Wiring in der zentralen `ensure_schema()` + Index + eigene Migrationsversion (`record_migration`). Verifizieren gegen **frische tmp-DB**: alle Tabellen + Indizes + Migration vorhanden, Bestand unberührt. Beim Live-Deploy legt `ensure_schema` das **additiv** an — kein Daten-Backfill, kein Restore beim Rollback nötig.

### 7.7 Non-blocking Error Design

Nutzer-sichtbare Endpunkte degradieren *strukturiert*: Fehler → **HTTP 200 + `{"ok": false, "error": …}`** (überlebt Proxy-5xx-Rewrites), **nie** 500/Traceback. Best-effort-Seiteneffekte (Cost-Logging, Audit-Historie) laufen in eigener Connection, schlucken Fehler und können den Hauptpfad **nie** brechen.

### 7.8 Feature-Flags

Gemerged ≠ aktiv. Funktionen hinter Schaltern ausliefern, unabhängig vom Deploy aktivieren. (Bei `boxscore` z. B. `feature.weeklyAutomation`, `feature.autoDeploy` als „in-dev" im Release-Manifest.)

### 7.9 Das Produkt kennt sich selbst — die `/status`-Seite

Eine **Status-Seite** zeigt live: deployte Version, Funktionen (live vs. in Entwicklung), Datenfrische, letzter Alarm, API-Gesundheit. Quelle ist eine Versionskonstante / ein Release-Manifest. Beispielstruktur aus `boxscore/product-state.json`:

```json
{
  "name": "boxscore", "version": "0.8.3", "phase": "P5",
  "environments": {
    "staging":    { "url": "...:8080", "deployedVersion": "0.8.3", "deployedAt": "2026-06-09" },
    "production": { "url": "...:8081", "deployedVersion": "0.8.3", "deployedAt": "2026-06-09" }
  },
  "features": [
    { "key": "ci-four-gates", "title": "CI: vier Testkategorien als parallele Merge-Gates", "status": "live", "flag": null },
    { "key": "auto-deploy-on-merge", "title": "Merge→Auto-Deploy", "status": "in-dev", "flag": "feature.autoDeploy" }
  ],
  "changelog": [ { "version": "0.8.3", "date": "2026-06-09", "type": "feat", "summary": "..." } ],
  "data": { "source": "nflverse", "lastIngestAt": "2026-06-09", "seasons": 28, "games": 7548 }
}
```

Der **Smoke-Test prüft, dass `/status` die erwartete Version nennt** (Daten == Auslieferung) — siehe 12.4.

### 7.10 Anmutige Entartung statt Totalausfall

Fehlt eine optionale Quelle, läuft das Produkt degradiert weiter. **Selbsterhaltung vor Selbstheilung.**

---

## 8. Test-Strategie (das Herzstück)

### 8.1 Philosophie

- **Tests sind das Fundament, das Autonomie und Auto-Deploy erst erlauben.** Ohne sie kein autonomer Lauf.
- **„Confidence per minute".** Die richtige Metrik ist nicht Testanzahl, sondern wie viel Vertrauen die Suite *pro Minute Laufzeit* liefert.
- **Gates sind nicht verhandelbar.** Vor dem Merge müssen alle Kategorien grün sein. Bei Flakiness: **Ursache fixen, nicht das Gate aufweichen.**

### 8.2 Die Form folgt der Architektur

Unit für reine Logik; **Integration als Schwerpunkt** bei API-/Datenprojekten; **wenige E2E** für kritische Nutzerpfade. Statische Analyse (Lint, Typen) ist die Basis.

### 8.3 Die vier Test-Kategorien (als paralleles Merge-Gate)

| # | Kategorie | Prüft | Werkzeuge |
|---|---|---|---|
| 1 | **Technische Funktion** | Logik, Units, Komponenten | pytest / Vitest |
| 2 | **Daten-Retrieval / Integration** | Fetch korrekt, Upstream-Schema stabil | Adapter-**Contract-Tests** gegen aufgezeichnete **Fixtures**; echte Quelle nur unter `network`-Marker |
| 3 | **Daten-/Geschäfts-Konsistenz** | Dubletten, Summen, Invarianten, **„Text == DB"** | SQL-Assertions, Quer-Checks, Frische-Checks |
| 4 | **Website / UX** | Navigation, Suche, Barrierefreiheit, Layout, Performance | Playwright (rollenbasiert), axe (WCAG 2.2 AA), Visual-Regression, Link-Check, Lighthouse-Budget |

Parallelität: pytest-xdist, Vitest, Playwright-Sharding, CI-Matrix. Netzwerktests sind mit dem `network`-Marker isoliert und laufen **nicht** im Standard-Gate (deterministische, reproduzierbare CI).

> **Praktische Umsetzung der Kategorisierung (capsule):** Jeder pytest-Test bekommt über `tests/conftest.py` (`pytest_collection_modifyitems`) genau *eine* Kategorie. Neue Integration-/Konsistenz-Tests setzen den Marker explizit (`pytestmark = [pytest.mark.integration]`); alles andere wird per Datei klassifiziert, Default `technical`. So partitionieren die drei Python-Kategorien die gesamte Suite — und die **required `quality-gates`-Pipeline fährt zusätzlich die volle Suite**, sodass kein Test durch eine Marker-Lücke durchrutschen kann.

### 8.4 Hermetische Tests — das praktische Rückgrat

Der Standard-Gate-Lauf ist **deterministisch und offline**. Konkrete, erprobte Hebel:

- **Abhängigkeiten injizierbar machen.** Externe Calls laufen über injizierbare Schnittstellen — HTTP-Transport, OpenAI-/LLM-Client, **DNS-Resolver**, Cost-Recorder, Zeit. Tests reichen Fakes/Mocks/Recorded-Transports herein → kein echter externer Call im Lauf, aber **realer Code-Pfad** (Redirects, Size-Caps, Timeouts werden echt durchlaufen).
- **Isolierte Daten je Test.** Jeder Test setzt `…_DB_PATH → tmp` (+ Standard-Env) → `reload_settings` → `ensure_schema` → Test-Client. Pro Test eine frische DB; die **Live-DB wird nie berührt.**
- **Contract gegen Fixtures.** Externe Schnittstellen über einen **expliziten, versionierten, maschinenlesbaren Contract** (erwartete Felder/Typen/Statuscodes). Im Gate gegen aufgezeichnete Fixtures; gegen die echte Quelle nur periodisch / unter `network`-Marker (fängt Upstream-Drift früh). Oft übersehene Konsumenten: **autonome KI-Agenten** und nachgelagerte Pipelines.
- **Bei jedem Bugfix ein Regressionstest.**

### 8.5 Datenqualität als Tests

Frische-Checks (kommen die Daten an?) · Schema-/Spaltentests in der bereinigten Schicht (Typen, Nicht-Null, erlaubte Werte) · **Quer-Checks zwischen Quellen** über kanonische IDs (Konflikt jenseits Toleranz = Rot) · Geschäftsregel-Assertions in der geschäftsfertigen Schicht.

### 8.6 Das Quality-Gate (ein Kommando)

Ein einziger Einstiegspunkt fährt die Pflicht-Schritte: **compile/compileall · Lint-kritisch · pytest · Secret-Scan · Live-Smoke auf ephemerem Port.** Regeln: deterministisch, parallelisierbar, Richtwert Haupt-Gate **< ~10 Minuten**.

> **„Lint-kritisch" ≠ vollständiges Lint:** Die Gate-Selektion ist bewusst eng (nur Syntax-/Undefined-Name-Klassen, z. B. ruff `E9,F63,F7,F82`); stilistische Funde (ungenutzte Importe) brechen das Gate nicht — aber im *berührten* Code räumt man sie auf. So bleibt das Gate schnell und blockiert nie aus kosmetischen Gründen.

### 8.7 Gate gegen eine Kopie der Live-Daten

Für den Gesamt-Gate-Lauf (inkl. Live-Smoke) wird `…_DB_PATH` auf eine **konsistente Online-Kopie** der Live-DB gezeigt (per DB-eigener Online-Backup-API erzeugt — nur *Lesen* der Live-DB). So läuft der Smoke gegen realistische Daten, **ohne die Live-DB je zu schreiben.** `ensure_schema` legt neue Tabellen auf der *Kopie* an — praktischer Beweis, dass die additive Migration auch auf befüllten Daten greift.

---

## 9. UX: Design und sein Test

### 9.1 Design-Disziplin

- **Design-Tokens als einzige Quelle der Wahrheit fürs Aussehen.** Geschichtet: **Kern-Tokens → semantische Tokens → Komponenten-Tokens**. Eine Änderung oben propagiert überall hin. **Neue Seiten erfinden keine Ästhetik** — sie verwenden die bestehenden Komponenten/Tokens (Karten-, Touch-Target-, Spacing-Klassen).
- **Feste Templates je Seitentyp**, starke Querverlinkung, **Mobile-first**, Touch-Targets ≥ 44 px.
- **Barrierefreiheit von Anfang an** (Kontrast 4.5:1 normal / 3:1 groß, semantisches Markup, Tastaturbedienung).

### 9.2 Automatisierte UI-Tests (Gate-Kategorie 4)

Playwright **rollenbasiert** (`getByRole` / `getByLabel` — zugleich a11y-Signal und weniger flaky) · axe gegen WCAG 2.2 AA · Visual-Regression (Screenshot-Baselines) · Link-Integrität · **Lighthouse-Budget als Gate** (LCP < 2,5 s · INP < 200 ms · CLS < 0,1).

> **Betriebs-Detail:** Die UX-Kategorie läuft **nur in der GitHub-CI** (Node/Playwright-Browser werden auf dem Prod-VPS *nicht* installiert). Das hält den VPS schlank und trennt Build-/Test-Last sauber von der Laufzeit.

### 9.3 Die ehrliche Grenze

Eine grüne Maschine ist **nicht** dasselbe wie gute UX (Scanner fangen nur ~30–40 % der a11y-Verstöße). Tests sind das **Regressionsnetz**; das *Urteil über die Erfahrung* bleibt beim Menschen — an den Checkpoints. Geschmacks-/Layout-Entscheidungen (Board-Layout, Export-Formate) werden **nicht geraten**, sondern offen für User-Feedback gehalten.

---

## 10. KI-Verifikations-Gates

**Das Prinzip.** Wo eine KI Inhalte/Code/Entscheidungen erzeugt, **ersetzt automatische Verifikation gegen eine Quelle der Wahrheit das menschliche Review.**

- **Jede Aussage gegen die Wahrheit prüfbar:** jede Zahl im Text == DB; jede referenzierte Entität ist real; Quellen erreichbar, Schema valide. **Rot = kein Publish** → Alarm + automatischer Regenerierungsversuch. (Bei `boxscore` publiziert ein Content-Agent Wochen-Recaps *nur*, wenn jede Zahl als „Claim" gegen die DuckDB grün ist — hunderte Claims pro Lauf.)
- **Output gegen den Bestand validieren.** Liefert ein LLM strukturiertes JSON mit Verweisen (z. B. `selected_item_ids`), wird es **hart gegen den realen Katalog validiert**: unbekannte IDs werden gedroppt/geflaggt, der Ausgabevertrag wird erzwungen (`response_format=json_object`), „weiß nicht" → Feld leer statt halluzinieren. So zeigt das Produkt nie auf nicht-existente Dinge.
- **Grounding statt Re-Compute.** Den Kontext kompakt **als Text** ins Prompt geben (vorhandene Felder) statt teurer Re-Analyse — token-sparsam, deterministisch, billig.
- **Resilienter Modell-Client.** Timeout, beschränkte Retries mit Backoff, Circuit-Breaker, getypte Ergebnisse (Erfolg/Fehlerklasse/Tokens/Kosten); wirft nie nach außen. (Eigenes ADR: „OpenAI Client Resilience".)
- **Kosten-Idempotenz & Stichprobe vor Masse.** Verifizierte Einheiten nicht erneut per bezahlter API erzeugen; eine Einheit + Kostenschätzung zur Freigabe, dann skalieren.

> Überträgt sich auf alles KI-Generierte: Code (gegen Tests), Zusammenfassungen (gegen Quelle), Klassifikationen (gegen Stichprobe). **Vertraue nie der Plausibilität — prüfe gegen etwas Maßgebliches.**

---

## 11. Debugging

Beide Projekte behandeln Debugging als **diszipliniertes, messgetriebenes Verfahren** — nicht als Raten.

### 11.1 Das Root-Cause-First-Protokoll

1. **Reproduzieren** (minimaler Fall).
2. **Eingrenzen** (welches Modul / welche Datei / welcher Layer).
3. **Beobachten** (Logs, Exceptions, Exit Codes).
4. **Hypothese** (genau *eine* zur Zeit).
5. **Minimaler Fix** (kleinste mögliche Änderung).
6. **Verifizieren** (Run + erwartetes Ergebnis).
7. **Dokumentieren** (PROJECT_STATE / RUNBOOK, wenn relevant).

**Keine Vermutungsfixes:** keine „ich glaube, das ist es"-Änderungen ohne Messung. Erst Beobachtung → Hypothese → minimaler Fix → Verifikation. **Transparenz-Regel:** Ist die Ursache unklar, das *sagen*, den exakten Datei-Abschnitt anfordern, **inspizieren statt spekulieren**. Nie mehrere logische Belange in einem Schritt ändern (Change → Run → Inspect → Commit).

### 11.2 PowerShell-/Windows-Spezifika (real gelernt)

- Bei zickenden Skripten **Parser/Token prüfen** statt blind `-replace`. Bei String-/Quote-Problemen den Script-Teil **isolieren oder neu schreiben** — strukturierter Neuaufbau schlägt zehn kleine Replacements.
- **Keine Smart Quotes** (Unicode-Anführungszeichen). String-Interpolation beachten: `"$var:"` ist gefährlich → `"{0}:" -f $var` oder `${var}`.
- **Encoding konsistent UTF-8**; bei merkwürdigem Verhalten Datei auf versteckte Unicode-Zeichen prüfen. (In CI-Skripten, die unter Windows PowerShell 5.1 laufen, bewusst **ASCII-only** in ausgeführten Codeblöcken — UTF-8-ohne-BOM wird sonst als ANSI fehldekodiert.)

### 11.3 Automatisierte Fehler-Diagnose (Gate-Triage)

Jeder Quality-Gate-Lauf emittiert zusätzlich zu Step-Logs und Summaries eine **Diagnose-Schicht** (`quality_gate_diagnose.py`), die typische Fehlerklassen automatisch erkennt:

- PowerShell-Execution-Policy-Blocks,
- Encoding-Probleme,
- pytest-Assertion-Failures,
- Runtime-Smoke-Failures,
- Scanner-Findings.

Damit muss niemand Rohlogs durchwühlen — die Triage zeigt sofort die Klasse des Problems. Ergänzend bauen `ops_report_index.py` und `runs_report.py` (mit `--markdown`) kompakte Indizes über jüngste Gate-Läufe und Release-Evidence.

### 11.4 Observability — zweistufige Health-Checks

Zwei Health-Schichten, zwei Verträge (ADR-0021):

| Endpoint | Auth | Liefert | Zweck |
|---|---|---|---|
| `GET /healthz` | keine | `200 {"status":"ok"}` | Prozess lebt |
| `GET /api/v2/health` | keine | `200 {"status":"ok"}` | API-Router gemountet |
| `GET /healthz/deep` | keine | 200 ok / 503 degraded + Probe-Payload | DB + FS + (opt.) OpenAI |
| `GET /api/v2/health/deep` | `X-API-Key` | dito, auth-gated | für externe Monitore mit Key |

Die Probes (`check_db`, `check_filesystem`, `check_openai`) liefern je `{ name, status, latency_ms, detail?, meta? }` mit `status ∈ ok | degraded | skipped`. **Wichtig:** Der OpenAI-Probe ist **per Default aus** (kein Kosten-Risiko, auch nicht für Metadaten); aktiviert wird er nur auf dem VPS via `WARDROBE_HEALTH_OPENAI_PROBE=1`. Der 503-Body hat **dieselbe Form** wie der 200-Body — die Diagnose liegt auf der Leitung, selbst wenn der Endpunkt Fehler signalisiert.

### 11.5 Logging mit klarer Präzedenz

`setup_logging(...)` löst Level und Pfade mit fester Reihenfolge auf (ADR-0024): **(1) explizites Keyword-Argument → (2) Environment-Variable (`WARDROBE_LOG_LEVEL` / `_DIR` / `_FILE`) → (3) Default**. `setup_logging` ist **idempotent** auf demselben aufgelösten Dateipfad — keine doppelten Handler. Strukturierte Logs landen in einem definierten Laufzeit-Verzeichnis (nicht im Repo).

---

## 12. Deployment & Betrieb — VPS-Fokus

Da VPS-Betrieb (zunächst Windows-VPS) das gewählte Zielumfeld ist, ist dieses Kapitel das praktisch wichtigste.

### 12.1 Das Zielbild (vollautomatisch)

```
Merge auf main → Build → Staging (echte zweite Instanz)
   → automatischer Smoke-Test in echter Umgebung
   → Beförderung auf Produktion → Smoke auf Prod  (+ Auto-Rollback bei rotem Prod-Smoke)
```

Idempotente, reproduzierbare Deploys (Release-Kopie + atomarer Swap). Nach jedem Deploy spiegelt die Status-Seite den neuen Stand. **Solange die Auto-Kette nicht scharf ist, deployt der Mensch über ein klar dokumentiertes Skript — das Ziel bleibt der handgriff-freie Pfad.**

`boxscore` hat diese Kette **realisiert**; `capsule` hat sie als Ziel und nutzt noch einen attendeten Pfad. Beide Wege sind unten dokumentiert.

### 12.2 Die atomare Deploy-Mechanik (boxscore — voll automatisiert)

Kern ist ein **Junction-Swap** (Windows-Verzeichnis-Link) auf versionierte Release-Ordner — atomar (best effort), instant rückrollbar:

- **Release-ID = Version + kurzer Git-SHA + Zeitstempel.** Der Zeitstempel macht wiederholte Deploys desselben Commits unterscheidbar (Voraussetzung für Rollback zwischen zwei Releases).
- **`deploy.ps1`** → `npm ci` + `npm run build` im Repo → `dist` nach `staging\releases\<id>` kopieren → `current`-Junction umschwenken. Caddy serviert `staging\current`.
- **`promote.ps1`** → kopiert **exakt das auf Staging geprüfte Artefakt** nach `prod\releases\<id>` (keine Neukompilierung — *es geht live, was den Smoke bestanden hat*) → `prod\current` umschwenken.
- **`rollback.ps1`** → schwenkt die `current`-Junction zurück auf die in `.previous` gemerkte Release. **Pflichtpfad bei rotem Smoke, kein Sonderfall.**
- **`smoke.ps1`** → prüft die zentralen Seiten auf HTTP 200 *und* dass `/status` die erwartete Version nennt (Daten == Auslieferung). Exit 0 = grün.

Robustheits-Details, die man übernehmen sollte:
- Beim Umschwenken **nur den Junction-Link entfernen, nie das Zielverzeichnis.**
- **Best-effort-Logging** (`deploy.log`): Ein nicht schreibbares Log darf einen *erfolgreichen* Deploy nie abbrechen.
- Release-Ordner bleiben liegen → Rollback ist ein reiner Link-Swap, kein Rebuild, kein Restore.

### 12.3 Die Auto-Deploy-CI-Kette (boxscore)

Zwei getrennte Workflows verhindern Kollisionen auf dem *einen* VPS:

- **`ci.yml` läuft nur auf Pull Requests** — die vier Kategorien als parallele Jobs + ein **Aggregat-`merge-gate`** (genau dieser Check wird für Auto-Merge verlangt). Ein zweiter Voll-Lauf bei push-to-main wäre redundant und kollidierte mit dem Deploy-Build (CPU-Contention → einmalig das Render-Zeit-Budget gerissen).
- **`deploy.yml` läuft bei push auf `main`** — Build → Staging → Smoke → Promote → Prod-Smoke → **Rollback bei Fehler** → **ntfy-Alarm**.

Der **Preflight** prüft, ob der Runner-Account (`NT AUTHORITY\NETWORK SERVICE`) bestehende Releases in `staging`/`prod` *überschreiben* darf (nicht nur neue Dateien anlegen — genau das schlug subtil fehl). Solange das Recht fehlt, **überspringt der Preflight den Deploy GRÜN** (kein roter Lauf je Merge) und der Owner deployt manuell. Danach läuft die Automatik von selbst. — Ein gutes Muster: **degradiere bei fehlendem Recht zu „grün übersprungen", nicht zu „rot".**

### 12.4 Das Attended-Promotion-Protokoll (capsule — der erprobte Ist-Pfad)

Solange Prod *eine* Instanz ist und Restarts elevierte Rechte brauchen (die der Agent bewusst **nicht** hat), läuft Deploy als 5-Phasen-Übergabe. Der Agent macht alles **außer** Restart/Merge/Push selbst; der Mensch gibt erst „deploy", dann führt er den **einen elevierten Schritt** (Restart) aus.

- **Phase 0 — Pre-Flight (read-only).** Branch-Tip = Deploy-SHA; aktueller `main` = Rollback-Anker (notieren); `git status` clean bis auf bekannte Artefakte; **Gate am Deploy-SHA re-bestätigen**; Live gesund (Health + Version); **ALT-Marker-Baseline** festhalten (was vor dem Deploy *fehlt*: neue Route 404, neue Tabelle/UI nicht da). Rot → STOPP vor Backup/Checkout.
- **Phase 1 — Backup mit bewiesener Restore-Probe.** `restore_ok: true` **und** `matches_source: true` (Zählwerte stimmen). *Ein ungetestetes Backup ist kein Backup.*
- **Phase 2a — Checkout + Pre-Restart Disk-Verify.** `git checkout <branch>` ändert nur die Disk — der laufende Prozess serviert bis zum Restart weiter den alten Tree (kein Outage). Dann **read-only verifizieren, dass die Arbeitskopie den Ziel-Code wirklich TRÄGT** (Schlüsseldateien/Routen/Marker auf der Disk, *nicht* nur den Branch-Diff). Fehlt ein Punkt → `git checkout main`, melden, nicht übergeben.
- **HANDOFF.** Alles grün → STOPP. Der Mensch bekommt das **exakte elevierte Restart-Snippet** + die Marker zur Bestätigung. Der Restart ist sein Schritt.
- **Phase 3 — Live-Smoke + echte Probe.** Nach dem Restart read-only: Health, **NEU-Marker** (Gegenstück zur ALT-Baseline), Regressionen bestehender Features. Dann **eine echte End-to-End-Probe** der neuen Funktion (der einzige bewusste Live-Write, attended). Sauberes `{"ok":false}` ist kein Merge-Blocker; **500/Traceback/Crash → STOPP, kein Merge.**
- **Phase 4 — Promotion.** `git checkout main` → `git merge --no-ff <branch>` → **`git diff <branch> HEAD` muss LEER sein** (Disk = main == Live) → **kein zweiter Restart** (reines Bookkeeping) → `git push`.

Der einfache In-Place-Update-Pfad (`vps_update_from_git.ps1`) macht im Kern: Tasks stoppen → **den detached Python-Prozess auf dem Port killen** (sonst `WinError 10048` beim Bind — ein real gefixter Bug) → `git pull` → Bootstrap (pip) → **Quality Gates lokal auf dem VPS** → Tasks neu starten → **`Wait-CapsuleApiHealthy`: laut scheitern, wenn die API nicht wieder live ist.**

### 12.5 Die teuer gelernten Deploy-Lessons

1. **Deploy-Branch zuerst auf aktuelles `main`** (sonst rollt der Restart seither gemergten Code zurück).
2. **Disk-Verify, nicht Branch-Diff.** Ein Drei-Punkt-Diff zeigt nur, was der Branch *hinzufügt*, nicht was ihm *fehlt*. Vor dem Restart per `grep` bestätigen, dass die Arbeitskopie den Ziel-Code trägt.
3. **Marker-Verifikation nach dem Restart** prüft **deploy-spezifische** Marker (nicht generische Routen, die in altem *und* neuem Code 200 liefern).
4. **Code-Identität bei „docs-only on top".** Lief das Gate am code-vollständigen Commit und hat der Deploy-SHA nur Docs obendrauf, per `git diff <gate-sha>..<deploy-sha>` bestätigen, dass *nur* Docs differieren — und das volle Gate am echten Deploy-SHA frisch nachziehen (deckt u. a. Secret-Scan über die neuen Docs).
5. **Working-Copy-Hygiene.** Nach einem reinen Build-Lauf *ohne* Deploy die Arbeitskopie wieder auf `main` nehmen — sonst serviert der Prozess zwar alten Code, frisch geladene Templates/Assets kämen aber schon vom Branch.

### 12.6 VPS-Härtung & Zugangsmodell (Windows-VPS)

Direkt aus den Runbooks — der **Soll-Zustand** für einen produktiven Windows-VPS:

- **Kein öffentliches RDP.** Admin-Zugang **ausschließlich über Tailscale-RDP** (privates Mesh-VPN). Öffentlicher Inbound auf 3389 ist providerseitig (Contabo-Firewall) geschlossen; Erwartung: `Test-NetConnection <ip> -Port 3389 → TcpTestSucceeded: False`.
- **Windows Defender Firewall aktiv**, alle Profile `Enabled = True`, `DefaultInboundAction = Block`, `DefaultOutboundAction = Allow`. Keine dauerhaften Sonderregeln (`TEMP-RDP-*`).
- **App bindet nur lokal** auf `127.0.0.1:<port>`. **Kein offener Inbound-Port** für die App.
- **Öffentlicher Zugang über Cloudflare Tunnel** (`cloudflared` als Windows-Service, `StartType = Automatic`). Web hinter **Cloudflare Access** (SSO).
- **Wichtige Trennung Web vs. API:** Die API-Subdomain für maschinelle Konsumenten (Custom GPT, Mobile-App) darf **nicht** auf eine interaktive Access-Loginseite umgeleitet werden — sie authentifiziert per Header (`X-API-Key`). Test ohne Header muss **Unauthorized JSON** liefern, *nicht* eine Cloudflare-Login-HTML-Seite.
- **VNC nur als temporärer Recovery-Weg**, danach wieder deaktivieren.
- **`.env` liegt auf dem Server**, nie im Repo. Der App-Auth-Key (`WARDROBE_API_KEY`) ist *nicht* der OpenAI-Key.

**Goldene Betriebsregel:** *Vor* Änderungen an Firewall, Tunnel, Access oder Diensten **immer zuerst sicherstellen, dass Tailscale-RDP funktioniert** — niemals mehrere Schutzschichten gleichzeitig blind ändern (sonst sperrt man sich aus).

**Reboot-Checkliste** nach sicherheitsrelevanten Änderungen: (1) VPS neu starten → (2) Tailscale-Ping → (3) Tailscale-RDP → (4) `cloudflared` läuft → (5) lokale API → (6) öffentliche Web-/API-Domains.

> **Methodisches Detail:** Die Runbooks enthalten einen Abschnitt **„Dinge, die nicht wieder passieren sollen"** (z. B. „Windows-Firewall dauerhaft deaktivieren", „öffentliches RDP breit öffnen", „Tailscale und VNC gleichzeitig aufgeben, bevor der neue Zugang validiert ist"). Post-Incident-Lernen wird *in das Runbook* zurückgeschrieben — nicht nur in einen Chat.

### 12.7 Dauerbetrieb — Ops-Agenten & Resilienz

- **Watchdog** (minütlich): Heartbeat/Health; abgestürzter Dienst wird automatisch neu gestartet.
- **Backup (täglich) + Restore-Probe (regelmäßig):** Wiederherstellbarkeit wird **bewiesen** (`restore_ok` *und* `matches_source`). Bei `boxscore` validiert: „7548 Spiele wiederhergestellt".
- **Dead Man's Switch** (täglich): alarmiert, wenn etwas **Fälliges *nicht* passiert** ist.
- **Health-/Integritäts-Check** (täglich): DB-Konsistenz, kleinster Ping bezahlter APIs, Rest-Kontingente, Datenfrische → Status-Seite.
- **Alarmierung, die hilft statt rauscht.** Fehler **klassifiziert** (401/403, Guthaben, 429/529 mit Retry+Backoff und Alarm erst nach N Fehlversuchen, Netz, Stale) → **Push in Klartext mit Handlungsempfehlung** (z. B. via ntfy). Erfolg meldet sich kurz, alles Übrige schweigt; jeder Alarm zusätzlich ins Log und als „letzter Alarm" auf die Status-Seite.
- **Neustart-Ablauf gehört explizit ins Runbook** (Autostart, geplante Aufgaben, Watchdog als Netz), **außerhalb des Servers** abgelegt.


---

## 13. Sicherheit & Kosten

### 13.1 Sicherheit & Secrets

- **Keine Geheimnisse im Repo.** `.gitignore` blockt `.env`, Keys, Zertifikate, Token-Dateien; Keys liegen auf dem Server / als CI-Secrets — **nie im Code, nie im Chat.** Zufallsstrings/Tokens immer **kopieren, nie abtippen**, und in Doku/Commits **nie zitieren**.
- **Kein blindes `git add -A`.** Explizit adden; bekannte untracked/driftende Artefakte nie stagen. (Realer Stolperstein in `capsule`: ein `vps-settings.ps1` mit ngrok-Token war „untracked, aber nicht gitignored" — deshalb die harte Regel.)
- **Geringste Rechte.** Die autonome Sitzung läuft **ohne erhöhte Rechte.** Wo Admin nötig ist, bereitet der Agent ein **exaktes, einmalig auszuführendes elevated Skript** vor; der Mensch führt es bewusst aus.
- **Kein offener Inbound-Port.** Zugriff über privates Netz (Tailscale); öffentlicher Tunnel (+ Access/SSO) nur bei echtem Bedarf. **Pervasive Security:** Teil von Design *und* Tests — `capsule` hat eigene `test_security_*`-Tests (Secret-Scan, Inventory, Contracts, Hygiene-Report).
- **Secret-Scan im Gate** (und im Pre-Commit-Hook). Falsch-Positive (z. B. Token-*Counts*) werden mit klarer Begründung **lokal** suppressed — nie pauschal und nie über den engen Anlass hinaus.
- **Supply-Chain-Hygiene automatisiert:** Dependabot für `pip` und `github-actions`, wöchentlich, mit Labels `dependencies`/`security`.

### 13.2 Kosten-Disziplin (bei bezahlten KI-/API-Diensten)

- **Harte Obergrenze** (Prepaid ohne Auto-Reload = physische Kostengrenze).
- **Schätzung vor jedem teuren Lauf**, **Stichprobe vor Masse**, **idempotente Wiederholung ohne Doppelkosten.**
- **Cost-Logging je Call** (Modell, Tokens, geschätzte Kosten, op-Label) als Fundament für Cap/Alarm; Rest-Kontingent loggen, **Alarm unter Schwellwert.** Kosten in Credits verstehen, nicht in HTTP-Requests. (Beispiel-Realkosten aus `boxscore`-Changelog: eine Recap-Regeneration über 22 Wochen ≈ 1,88 $.)

---

## 14. Handoff-Management & durables Gedächtnis

Handoffs sind der Mechanismus, mit dem Wissen Sessions, Kontext-Resets und Chat-Umzüge überlebt. Sie sind **Pflicht** an Session-Abbruch (relevante Stelle), Übergabe in einen neuen Chat, Release-/Meilensteinpunkten, Architektur-/Betriebsänderungen. Sie **ersetzen nicht** die kanonische Doku in `docs/`, sie ergänzen sie.

### 14.1 Worklog (append-only, pro Lauf, auf dem Branch)

Ein Eintrag je Tranche: was gebaut, welche Dateien, Testresultat, Entscheidungen/Parks. Das ist das **Arbeitsgedächtnis** — überlebt Session-Abbruch und Kontext-Reset.

### 14.2 HANDBACK (am Ende eines Laufs)

Enthält: Branch + finaler SHA · Tranchen-Status (fertig/geparkt) · Gate-Resultat (passed/skipped) · Park-Liste · getroffene Entscheidungen/offene Ambiguitäten · **Promotion-Rezept + Smoke-Marker** (was nach dem Restart zu prüfen ist) · ggf. Rollback-Hinweis.

### 14.3 Der Pflicht-Inhalt jedes Handoffs (Manifest)

Ein Handoff muss so geschrieben sein, dass ein neuer Chat **ohne Rekonstruktion aus diffusen Einzelständen** weiterarbeiten kann. Mindestinhalt:

1. **Ziel / Kontext** — woran wird gearbeitet, warum relevant?
2. **Ist-Stand** — Commit/Branch, technischer Stand, Betriebsannahmen.
3. **Letzter validierter Zustand** — letzter erfolgreicher Gate-Lauf, Artefaktpfade, bekannte Grenzen.
4. **Änderungsumfang** — betroffene Dateien/Module, Doku-Änderungen, Deploy-Impact.
5. **Offene Punkte** — Fehler, Entscheidungen, Risiken, nächste Blocker.
6. **Nächster konkreter Schritt** — **genau ein** robuster Startpunkt; kein allgemeines „weitermachen", sondern ein umsetzbarer Folgebefehl.

**Qualitätsregeln:** keine unpräzisen Zustandsbehauptungen · keine unbelegten „sollte gehen"-Formulierungen · kein Handoff als reiner Chat-Roman · **immer mit einem technisch belastbaren Einstiegspunkt enden.**

### 14.4 Chat-Handoff-Template (zum Kopieren)

```text
## 1. Ziel des aktuellen Arbeitsblocks
## 2. Technischer Ist-Stand
   - Commit / Branch:
   - Letzter erfolgreicher Gate-Lauf:
   - Lokaler Serverstatus:
   - VPS-Status:
   - Öffentliche URL / Tunnelstatus:
## 3. Was wurde zuletzt konkret geändert?
## 4. Relevante Dateien / Module
## 5. Doku- und Governance-Stand
   - PROJECT_STATE aktualisiert: ja/nein
   - RUNBOOK aktualisiert: ja/nein
   - relevante ADR(s):
## 6. Offene Punkte / Risiken
## 7. Nächster robuster Schritt
   <genauer nächster Befehl oder konkrete nächste Aufgabe>
## 8. Was ausdrücklich NICHT erneut getan werden soll
```

### 14.5 Lesereihenfolge für den Übernehmer

1. `docs/PROJECT_STATE.md` → 2. `docs/HANDOFF_MANIFEST.md` → 3. `docs/RUNBOOK.md` → 4. `docs/ARCHITECTURE.md` → 5. `docs/DEVELOPER_WORKFLOW.md`.

### 14.6 Automatisierung & operatives Wissen

Handoff/Snapshot/Release-Evidence sind über die kanonische Befehls-Oberfläche erzeugbar (`capsule.cmd handoff` / `snapshot` / `release-evidence`). **Operatives Wissen darf nicht verloren gehen:** Test-Skripte, Secret-Scan, Backup-/Recovery-Tools, Run-Reports, Start-/Ops-Skripte werden dokumentiert, auch wenn sie nicht für Endnutzer sind.

---

## 15. CI/CD & Governance

### 15.1 Zwei Runner-Modelle (bewusste Wahl)

| | `capsule` | `boxscore` |
|---|---|---|
| **Runner** | GitHub-hosted (`ubuntu-latest`) | **Self-hosted** Windows-Runner auf dem VPS |
| **Pflicht-Gate** | volle `quality-gates`-Suite (deterministisch) | Aggregat `merge-gate` über vier parallele Kategorien |
| **Deploy** | manuell/attended (Ziel: auto) | **Auto-Deploy** bei push auf `main` |
| **UX-Tests** | eigener Cloud-Job (Playwright/axe/Lighthouse) | Kategorie-4-Job (Astro-Build + Playwright + axe) |

**Wann was?** Cloud-Runner sind einfacher, sauberer isoliert und brauchen keinen Server — ideal, solange kein Auto-Deploy-Zugriff auf die Live-Maschine nötig ist. Ein **self-hosted Runner auf dem VPS** ist der Schlüssel, wenn der Agent **selbst** auf Staging/Prod deployen soll (er hat dann FS-/Service-/Git-Zugriff vor Ort, Git/GitHub bleibt die Drehscheibe).

### 15.2 Branch-Protection als Code

Die Schutzregeln liegen versioniert im Repo (`.github/branch-protection.required-checks.json`) — Single-Owner-Setup:

```json
{
  "required_status_checks": ["quality-gates", "quality-gates (windows / py3.12)", "packaging-contracts"],
  "strict_status_checks": true,
  "required_review_count": 0,
  "require_conversation_resolution": true,
  "restrict_force_pushes": true,
  "allow_deletions": false
}
```

> **Skalierungs-Hinweis im Repo selbst:** „Bei Team-Erweiterung Upgrade auf `required_review_count=1` + `require_code_owner_reviews=true`." Die Governance ist also bereits auf Wachstum vorbereitet.

### 15.3 PR-Template als DoD-/Evidence-Checkliste

Jeder PR fragt strukturiert ab: **Summary** (was/warum/Risiko) · **Validation** (Quality-Gates lokal grün, gezielte Tests, kein undokumentierter Schema-/API-Drift, Release-Evidence aktualisiert) · **Evidence** (letzter Gate-Lauf, Logs/Artefakte, Screenshots/API-Samples) · **Governance** (Required-Checks mit der Branch-Protection-Config abgeglichen, ADR ergänzt/aktualisiert, Handoff-/Snapshot-Impact bedacht).

### 15.4 Nightly- & periodische Workflows

Über das Merge-Gate hinaus laufen geplante Jobs: `perf-baseline-nightly`, `security-hygiene-nightly`, `ops-nightly-health`. Damit werden Performance-Drift, Sicherheits-Hygiene und Betriebs-Health *kontinuierlich* überwacht, nicht nur bei Änderungen.

### 15.5 Release-Artefakte sind Pflicht

Releases sind **explizite Pflichtartefakte**, nicht implizit: Release-Notes (Scope, Change-Umfang, Testnachweise, bekannte Einschränkungen), Release-Evidence-Bundle, Readiness-Report. Jede Änderung gehört zu einem **Zielrelease** (im Commit-Subject vermerkt).

---

## 16. Bauplan für ein neues Projekt

Die empfohlene Reihenfolge, um ein neues Projekt nach dieser Methodik aufzusetzen:

1. **Fundament legen.** Agent-Arbeitsregeln (`CLAUDE.md`), Projekt-Stand (Ziel + Entscheidungslog), Roadmap. **Tech-Stack bewusst festschreiben.**
2. **P0 — Gerüst.** Repo, **Gate mit allen Test-Kategorien**, ein einziger Gate-Einstiegspunkt, Verzeichnisse (Dev/Staging/Prod getrennt), Status-Seiten-Skelett + Versionskonstante, CI-Workflows, Branch-Protection-Config, Pre-Commit-Hook.
3. **P1 — Vertikaler Schnitt (Experience-first).** *Eine* Sache komplett end-to-end, alle Gates grün, Deploy-Pfad läuft. **Erst dann verbreitern.**
4. **In die Breite & Tiefe.** Weitere Quellen (je Quelle = Adapter + Contract + Quer-Checks), weitere Seiten/Funktionen — alle **additiv** zur Frozen Zone.
5. **Automatik & Ops.** Verifikations-Gates für KI-Inhalte, Cost-Logging + Cap, Ops-Agenten (Watchdog/Backup/Restore-Probe/Dead-Man's-Switch/Health), Alerting.
6. **Härtung.** Visual-Baselines, Performance-Budgets, Rollback-Drills, **Auto-Deploy scharf schalten.**
7. **Checkpoints sparsam setzen.** Nur bei **Urteil, Geld oder Unumkehrbarkeit.**

**Wiederverwendbarer Startpunkt:** `boxscore` referenziert eine „Blaupause" (`joes-journal`) als Stack-Vorlage — es lohnt sich, ein eigenes **Template-Repo** zu pflegen, das P0 bereits enthält (Gate, Befehls-Oberfläche, Doku-Kanon, CI, Hooks), und neue Projekte davon abzuleiten.

---

## 17. Reifegrad-Vergleich der beiden Projekte

Die beiden Projekte sind nützlich *gerade weil* sie unterschiedlich weit sind — sie zeigen denselben Plan in zwei Ausbaustufen.

| Dimension | `capsule` (Ursprung der Methodik, organisch gewachsen) | `boxscore` (saubere Greenfield-Umsetzung) |
|---|---|---|
| **Stack** | FastAPI + Flask co-hosted, SQLite, OpenAI Vision | Astro SSG + TypeScript, DuckDB |
| **Methodik-Doku** | Ursprung (`METHODOLOGY.md`, ENGINEERING_MANIFEST, ~28 ADRs) | erbt sie als Entscheidungslog E1–E14 |
| **Test-Kategorien** | Kat. 1 stark; 2/3 „dünn", 4 anfangs abwesend (offen dokumentiert) | alle vier als parallele Gates realisiert |
| **CI** | Cloud-Runner, volle Suite als Pflicht | self-hosted VPS-Runner, vier parallele Gates |
| **Deploy** | attendet (5-Phasen-Protokoll), Auto als Ziel | Auto-Deploy: Staging→Smoke→Prod→Rollback |
| **Staging** | (noch) keine zweite Instanz | echte zweite Instanz von Anfang an |
| **Status-Seite** | als Ziel | live (`product-state.json`) |
| **Besonderheit** | radikale Ehrlichkeit über Tech-Schuld/GOTCHAs | Build-Budget-Gate, Verifikations-Gates für KI-Recaps |

**Die wichtigste übertragbare Lektion aus dem Vergleich:** `capsule` zeigt, dass man auch in einem *gewachsenen, noch unfertigen* System diszipliniert arbeiten kann, indem man **den Ist-Zustand und die bekannten Lücken schonungslos dokumentiert** (im `CLAUDE.md`, in ADRs, im Manifest). `boxscore` zeigt das **Zielbild**, wenn man von Anfang an „Experience-first + Gates + Auto-Deploy" baut. Für ein neues Projekt: nach `boxscore` aufsetzen, mit `capsule`-Ehrlichkeit betreiben.

---

## 18. Master-Checkliste

**Arbeitsmodell** — Arbeitsregeln/Projekt-Stand/Roadmap vorhanden · Architekt ≠ Executor · Onboarding read-only · Erkunden→Planen→Umsetzen→Prüfen · Stop-Regel bei Rot/Unklarheit.

**Tranchen** — klein/reviewbar/eingrenzbar/rücknehmbar · build→test→commit→worklog · Conventional Commits · DoD inkl. Doku · Branch von aktuellem `main`.

**Architektur** — Eine Wahrheit je Datensorte (Konflikt = Fehler) · `raw→staging→marts` + Adapter/Contract · Idempotenz · Frozen Zone (gepinnt, nur additiv) · additive Schema-Migration · non-blocking Errors · Feature-Flags · Status-Seite · Degradation.

**Tests** — 4 Kategorien als Gate, **nie aufweichen** · hermetisch (injizierte Transports/Clients/Resolver, tmp-DB pro Test) · Contract gegen Fixtures · Datenqualität · ein Gate-Kommando · Gate gegen **Kopie** der Live-Daten · Regressionstest je Bugfix · „confidence per minute".

**KI-Verifikation** — gegen Wahrheit prüfbar (rot = kein Publish) · Output gegen Bestand validieren · Grounding statt Re-Compute · resilienter Client · Kosten-Idempotenz · Stichprobe + Schätzung vor Masse.

**Debugging** — Root-Cause-First (reproduzieren→eingrenzen→beobachten→1 Hypothese→minimaler Fix→verifizieren→dokumentieren) · keine Vermutungsfixes · automatisierte Gate-Diagnose · zweistufige Health-Checks · Logging mit klarer Präzedenz, idempotent.

**Deploy & Ops** — Auto-Kette (Staging→Smoke→Prod + Rollback) bzw. Attended-Promotion (Pre-Flight → Backup+Restore-Probe → Checkout+Disk-Verify → HANDOFF → Smoke+echte Probe → merge --no-ff+push) · Junction-Swap/atomarer Release-Wechsel · Deploy-Lessons · Watchdog/Backup/Dead-Man's-Switch/Health · Alarme klassifiziert/Push/geloggt/Status-Seite · Restart-Ablauf im (externen) Runbook.

**VPS-Härtung** — kein öffentliches RDP (Tailscale-only Admin) · Windows-Firewall an, Inbound block · App bindet nur lokal · Cloudflare Tunnel als Service · API-Subdomain header-auth (nicht Access-Login) · VNC nur Recovery · vor jeder Schutz-Änderung Tailscale-RDP prüfen · Reboot-Checkliste · „Dinge, die nicht wieder passieren sollen".

**Sicherheit & Kosten** — keine Secrets im Repo · explizite Adds, nie `add -A` · geringste Rechte (elevated nur als bewusstes Owner-Skript) · kein offener Port · Secret-Scan im Gate + Pre-Commit-Hook · Dependabot · harte Kostenobergrenze + Low-Credit-Alarm.

**Gedächtnis/Handoff** — Worklog append-only + HANDBACK (SHA, Status, Gate, Parks, Promotion-Rezept) · Handoff-Manifest mit *einem* belastbaren nächsten Schritt · Lesereihenfolge für Übernehmer · Doku-Governance (Änderung ohne konsistente Doku = unvollständig) · operatives Wissen dokumentiert.

**Autonomer Lauf** — Hard-Stops · parken statt raten · rotes Gate → parken · Kontext-knapp → sauber stoppen + HANDBACK · pro Tranche committen · Ende auf `main`.

---

## 19. Anhang: Werkzeug- & Befehls-Referenz

### 19.1 Konkrete Verfahren (Cheat-Sheet)

| Verfahren | Kurz | Wozu |
|---|---|---|
| **Recon-first** | read-only Untersuchung mit Datei:Zeile-Belegen vor dem Bauen | gegen falsche Annahmen; verifizierbar statt vertrauensselig |
| **Hermetische Injektion** | Transport/LLM-Client/DNS-Resolver/Recorder als Parameter; Tests reichen Fakes | offline-deterministisches Gate, realer Code-Pfad |
| **tmp-DB pro Test** | `…_DB_PATH→tmp` → `reload_settings` → `ensure_schema` → Client | Live-DB nie berührt; volle Isolation |
| **Gate-Kopie** | konsistentes Online-Backup der Live-DB als Gate-DB | Smoke gegen reale Daten, ohne Live zu schreiben |
| **Additive Migration** | `_CREATE_…_SQL` + Guard + ensure_schema-Wiring + Index + `record_migration` | Schema wächst rückwärtskompatibel; Rollback ohne Restore |
| **Frozen-Zone-Pin** | Snapshot-/Contract-Test bricht bei Form-Änderung | mehrkonsumentige Verträge stabil; nur additive Änderung |
| **Non-blocking Endpoint** | Fehler → HTTP 200 + `{"ok":false}`; best-effort-Seiteneffekte gekapselt | kein 500/Traceback; Hauptpfad unzerstörbar |
| **Output-gegen-Bestand** | LLM-IDs hart gegen den realen Katalog validieren, JSON erzwingen | nie auf nicht-existente Entitäten zeigen; kein Halluzinieren |
| **Junction-Swap** | `current`-Link auf `releases/<id>`; `.previous` für Rollback | atomarer Release-Wechsel, instant Rollback ohne Rebuild |
| **Disk-Verify** | per `grep` bestätigen, dass die *Arbeitskopie* den Ziel-Code trägt | Branch-Diff zeigt nicht, was *fehlt* |
| **ALT/NEU-Marker** | vor Deploy festhalten, was *fehlt*; nach Restart prüfen, dass es *da* ist | deploy-spezifische Smoke-Verifikation |
| **Backup-Restore-Probe** | `restore_ok` **und** `matches_source` (Zählwerte) | bewiesene Wiederherstellbarkeit |
| **Code-Identitäts-Diff** | `git diff <gate-sha>..<deploy-sha>` = nur Docs? | Gate-Aussage auf den echten Deploy-SHA übertragen |
| **Worklog + HANDBACK** | append-only je Tranche + finale Übergabe | durables Gedächtnis über Sessions/Resets |
| **Gate-Diagnose** | `quality_gate_diagnose.py <run-dir>` klassifiziert Fehlerklassen | schnelle Triage statt Rohlog-Wühlen |

### 19.2 Empfohlene Repo-Struktur (Monorepo)

```
repo/
├── CLAUDE.md                 ← auto-geladene Agent-Verfassung
├── <app-code>/               ← Pakete (api/, dashboard/, ontology/, persistence/, ingest/, runtime/ …)
├── pipeline/ | web/          ← Datenpipeline bzw. Frontend (je nach Projekt)
├── content/                  ← generierte Inhalte (versioniert, Git = Herkunftsspur)
├── tests/                    ← die vier Testkategorien (+ conftest.py, support/, fixtures/)
├── ui-tests/                 ← Playwright + axe + Lighthouse (nur CI)
├── tools/                    ← task_runner, quality-gates, secret-scan, handoff, ops, hooks/
├── deploy/ | ops/            ← VPS-/Deploy-Skripte (PowerShell), Runner-Setup, Backup, Watchdog
├── docs/                     ← Methodik, ARD, adr/, Runbooks, Worklogs, Release-Notes, Handoffs
├── product-state.json        ← Release-Manifest (Quelle der /status-Seite)
├── .vscode/tasks.json        ← spiegelt die kanonische Befehls-Oberfläche
├── .github/                  ← workflows/, branch-protection.required-checks.json, dependabot.yml, PR-Template
├── pyproject.toml | pytest.ini | requirements*.txt
└── .gitignore                ← blockt .env, Keys, .venv, logs, __pycache__, Snapshots
```

### 19.3 Standard-Befehle (Windows / PowerShell, übertragbar)

```powershell
# venv & Einstieg
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# das Merge-Gate (compile, ruff-kritisch, pytest, secret-scan, live-smoke)
python .\tools\run_quality_gates.py            # oder: capsule.cmd quality-gates

# Tests (volle Suite bzw. Kategorien)
python .\tools\task_runner.py test
python .\tools\task_runner.py test-technical | test-integration | test-consistency
python -m pytest -m "data_consistency and not network"   # boxscore-Stil

# Diagnose & Ops-Reports
python .\tools\quality_gate_diagnose.py .\docs\_ops\quality_gates\run_YYYYMMDD-HHMMSS
python .\tools\ops_report_index.py
python .\tools\runs_report.py --since-hours 48 --markdown

# Handoff / Snapshot / Release-Evidence
capsule.cmd handoff
capsule.cmd snapshot
capsule.cmd release-evidence --release-id <id>

# VPS-Deploy (boxscore, atomar)
.\ops\deploy\deploy.ps1                    # Build → staging\releases\<id> → Junction-Swap
.\ops\deploy\smoke.ps1 -Instance staging
.\ops\deploy\promote.ps1                   # validiertes Artefakt → prod
.\ops\deploy\smoke.ps1 -Instance prod
.\ops\deploy\rollback.ps1 -Instance prod   # Pflichtpfad bei rotem Smoke

# VPS-Update (capsule, in-place)
powershell -ExecutionPolicy Bypass -File .\deploy\windows-vps\vps_update_from_git.ps1

# VPS-Härtung: Prüfkommandos
Get-NetFirewallProfile | Format-Table Name, Enabled, DefaultInboundAction, DefaultOutboundAction -Auto
Get-Service cloudflared | Format-Table Name, Status, StartType -Auto
Test-NetConnection <public-ip> -Port 3389     # erwartet: TcpTestSucceeded: False
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

### 19.4 Die fünf Sätze, die alles zusammenhalten

1. **Gates werden nie aufgeweicht, um Tempo zu machen.**
2. **Nichts ist fertig, weil es plausibel aussieht — erst, wenn ein Test es gegen die Wahrheit geprüft hat.**
3. **In Prod gelangt Code ausschließlich über den Deploy-Pfad — nie von Hand.**
4. **Eine Änderung ohne konsistente Doku gilt als unvollständig.**
5. **Der Mensch wird nur bei Urteil, Geld oder Unumkehrbarkeit gebraucht — alles andere ist autonom und Statusinfo.**

---

*Dieses Playbook ist werkzeug-nah, aber projekt-unabhängig. Die konkrete Tool-Wahl ist austauschbar; die Prinzipien und Verfahren bleiben. Es ist ein **lebendes Dokument** — fortschreiben wie jedes andere, kein Denkmal.*

*Erstellt auf Basis der Repositories `andreaskeis77/capsule` und `andreaskeis77/boxscore`.*
