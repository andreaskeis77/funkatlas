# Agent-Platform-Härtung & Improvement-Backlog

**Fünftes Dokument des Methodik-Korpus — der priorisierte Backlog, der die identifizierten Lücken schließt und den Kreis zu den vier bestehenden Dokumenten zieht.**

> **Zweck.** Dieses Dokument sammelt die konkreten Verbesserungen, die aus der Deep-Research-Analyse *und* unserer eigenen Gegenprüfung hervorgingen. Es ergänzt die vier Methodik-Dokumente um die Ebene, die dem Report zufolge noch fehlte: **Messbarkeit, Beweisbarkeit und Absicherung auf Produktionsniveau.** Jeder Eintrag ist ein umsetzbares Arbeitspaket mit *konkretem erstem Schritt* und *verifizierbarem Akzeptanzkriterium*.
>
> **Struktur.** Teil A = die **5 echten Lücken** aus dem Report (G1–G5). Teil B = die **5 Zusatzpunkte**, die auch der Report übersah (Z1–Z5). Die **Venue-Matrix** (Rest-Lücke aus Report-White-Spot #6, da Recovery sonst schon abgedeckt ist) ist in G4 eingegliedert, weil „welche Arbeit darf wo laufen" fundamental eine Trust-Boundary-Entscheidung ist.
>
> **Right-Sizing-Prinzip (aus unserer eigenen Methodik).** Der Report ist teils Enterprise-geprägt. Wir wenden **YAGNI + Regel der Drei** auf den Backlog *selbst* an: jeder Eintrag nennt die *20-%-Variante* für einen Solo-/VPS-Betrieb und was bewusst zurückgestellt wird. Sicherheit und Verifikation werden nicht zurückgestellt — Zeremonie und Enterprise-Vollausbau schon.
>
> **Sprachkonvention.** Doku/Kommunikation Deutsch; Code/Identifier/Commits Englisch.

---

## Wie man diesen Backlog liest

Jeder Eintrag folgt demselben Schema:

- **Lücke** — was fehlt (präzise, geerdet).
- **Warum (euer Kontext)** — warum es *für Solo-Betrieb, VPS, Bypass-Modus, neuestes Modell* zählt.
- **Erster Schritt** — der kleinste konkrete Einstieg (eine Tranche).
- **Akzeptanzkriterium** — maschinell/verifizierbar prüfbar, im Geist eurer „maschinen-prüfbaren DoD".
- **Priorität / Aufwand** — Welle 1–3 / grobe Größe (S/M/L).
- **Hakt ein in** — welches der vier bestehenden Dokumente es erweitert (Kreis schließen).
- **Right-Size (Solo/VPS)** — die 20-%-Variante; was zurückgestellt wird.

---

## Prioritäts-Überblick (drei Wellen)

| Welle | Fokus | Einträge | Begründung |
|---|---|---|---|
| **1 — Sofort** | größter Erkenntnisgewinn, wenig Umbau | **G1** Mini-Eval-Set · **G2** Agent-Telemetrie · **G4** Trust-Boundary- & Venue-Matrix | Messbarkeit + die dringendste Sicherheitslücke im Bypass-Modus; Telemetrie ist in Claude Code bereits eingebaut → billig schließbar |
| **2 — Kurzfristig** | Absicherung & autonomie-kritische Ränder | **G3** Release-Provenance (right-sized) · **Z1** Review-Triage · **Z2** Modell-Bump-Ritual · **Z5** Flaky-Quarantäne | schützt genau die Ränder, die *Autonomie + Nacht-Läufe + immer-neuestes-Modell* erzeugen |
| **3 — Reife & Konsolidierung** | Governance & Kreis schließen | **G5** Regel-Lebenszyklus + Konsolidierung (`docs/INDEX.md`, `CLAUDE.md`-Block, Agent-Platform-ADR) · **Z3** Daten/PII-Governance · **Z4** Produkt-Outcome-Schleife | verhindert Regelmüll, bindet alles an einer Stelle, misst Produktwirkung statt nur Lauf-Erfolg |

**Abhängigkeits-Hinweis:** G1 (Eval-Set) ist Voraussetzung für Z2 (Modell-Bump-Ritual) und für das fünfte Gate. G2 (Telemetrie) liefert die Daten für Z1 (Review-Triage) und Z5 (Flaky-Erkennung). Deshalb G1+G2 zuerst.

---

# Teil A — Die 5 echten Lücken (G1–G5)

## G1 — Eval-Operating-System für die Agentik

- **Lücke.** Wir haben starke *Regeln* (CLAUDE.md-Direktiven, Rollen, Hooks, Roadmap-Metadaten, Workflow-Skripte), aber **kein System, das misst, ob eine Regel netto etwas bringt**. „Confidence per minute" ist Test-*Philosophie*, kein Eval. Ohne diese Schicht droht **Regel-Akkumulation statt echter Verbesserung** — die Forschung zeigt, dass viele vermeintlich gute Agent-Skills neutral oder sogar schädlich sind.
- **Warum (euer Kontext).** Das ist der **größte Qualitätshebel** überhaupt und die Grundlage für das geplante fünfte Gate. Bei maximaler Autonomie entscheidet die Qualität eurer Regeln über die Qualität ganzer Nacht-Läufe.
- **Erster Schritt.** Eine `evals/`-Suite mit **8–12 realen Repo-Aufgaben** anlegen (je eine kurze Task-Beschreibung + Erfolgs-Check-Skript). Ein Runner, der jede Aufgabe **in frischer Session**, **mehrfach**, **einmal mit / einmal ohne** die zu testende Regel fährt und Passrate + Dauer + Tokens protokolliert (Anthropics `skill-creator`-Denke als Vorlage).
- **Akzeptanzkriterium.** Ein `eval-report` zeigt je Aufgabe A (mit Regel) vs. B (ohne) mit Passrate/Zeit/Tokens; eine neue Direktive/ein Skill wird **nur gemergt**, wenn der Report *keine* Passraten-Verschlechterung und *keinen* unbegründeten Token-Anstieg zeigt. → **Das ist das fünfte Gate: „Eval-Gate für Agentenartefakte".**
- **Priorität / Aufwand.** Welle 1 / M.
- **Hakt ein in.** `EXECUTION_PLANNING_AND_GUARDRAILS.md` (neues fünftes Gate neben dem Vier-Kategorien-Test-Gate) + `CODE_CRAFT_AND_DESIGN_STANDARDS.md` (Verifikations-Denke).
- **Right-Size (Solo/VPS).** Klein starten (8 Aufgaben reichen), Kontrollgruppe = derselbe Lauf ohne die Regel. Kein Eval-Framework-Zoo — ein Python-Skript + JSON-Report genügt. Zurückgestellt: statistische Signifikanz-Apparatur, große kuratierte Benchmarks.

## G2 — Agent-Telemetrie (Observability der Läufe)

- **Lücke.** Wir haben Worklogs, HANDBACKs, Morgen-Reports und Cost-Logging je Call — aber **keine durchgehende, maschinelle Telemetrie**: wo entstehen Zeit, Tokens, Kosten, Rework, Schleifen, Gate-Fehlschläge, Merge-Konflikte?
- **Warum (euer Kontext).** Mit wachsender Autonomie wird „was ist passiert" in Markdown zu dünn. Ohne Telemetrie verbessert ihr die Methodik *intuitiv* statt *empirisch*. **Gute Nachricht:** Claude Code hat OpenTelemetry **bereits eingebaut** — es emittiert Spans je Modell-Request/Tool-Ausführung, Metriken für Token/Kosten und Events für Tool-Entscheidungen (accept/reject) und Fehler/Retries, alle über eine `prompt.id` korreliert. **Nur Agent-SDK- und `claude -p`-Läufe honorieren eingehende Trace-Kontexte** — also genau euer Headless-Nacht-Orchestrator.
- **Erster Schritt.** In den Headless-Läufen `CLAUDE_CODE_ENABLE_TELEMETRY=1` + `OTEL_METRICS_EXPORTER=otlp` + `OTEL_LOGS_EXPORTER=otlp` setzen und an einen **self-hosted OTLP-Collector** exportieren (z. B. Collector → Prometheus/Loki → Grafana; passt zu eurer Self-Host-Präferenz und kann neben dem VPS laufen). Ein Basis-Dashboard: Tokens, Kosten, Dauer, Tool-Accept/Reject, Fehler/Retries je Lauf.
- **Akzeptanzkriterium.** Ein Dashboard zeigt je Lauf die Kennzahlen, über `prompt.id` korreliert; der **Nacht-Orchestrator-Report zieht diese Werte automatisch** statt manuell; ein Lauf mit auffälliger Schleifen-/Retry-Quote ist im Dashboard sichtbar.
- **Priorität / Aufwand.** Welle 1 / S–M (viel ist Konfiguration, kein Bau).
- **Hakt ein in.** `MULTI_AGENT_AND_LONGRUN_STRATEGY.md` (Orchestrator/Watchdog/Morgen-Report) + `ENGINEERING_PLAYBOOK.md` (Observability-Kapitel, das bisher nur *Produkt*-Health beschrieb — hier kommt *Agenten*-Observability dazu).
- **Right-Size (Solo/VPS).** Ein Collector + Grafana genügt; kein SIEM, kein Enterprise-AIDR. Privacy: `OTEL_LOG_USER_PROMPTS` **aus** lassen, solange Prompts sensibel sein könnten.

## G3 — Release-Provenance & Secret-Minimierung (Supply-Chain)

- **Lücke.** Wir haben Dependabot, Secret-Scan und ein eigenes Release-Evidence-Bundle — aber **kein SBOM, keine Build-Provenance/Attestation, keine OIDC-Kurzzeit-Credentials**. Der Stand der Technik geht weiter, gerade weil ein Teil der Änderungserzeugung bereits *automatisiert* ist (Agenten erzeugen PRs/Release-Kandidaten).
- **Warum (euer Kontext).** Aus „der Build war grün" wird der stärkere Satz „wir können nachvollziehen, *wo und wie* das Artefakt entstand". Relevanz ist aber **abgestuft**: SBOM lohnt immer (kennt eure Abhängigkeiten), OIDC nur wo aus CI gegen einen Cloud-Dienst authentifiziert wird, SLSA-Vollausbau ist für Solo Overkill.
- **Erster Schritt.** SBOM-Erzeugung pro Release in die CI aufnehmen (**CycloneDX** für den Python-/Node-Stack) und als Release-Artefakt anhängen. Wo CI gegen Cloud auth't: langlebige Secrets durch **GitHub-OIDC** (`id-token: write` + Provider-Trust) ersetzen.
- **Akzeptanzkriterium.** Jeder Release trägt ein maschinenlesbares SBOM als Artefakt; kein langlebiges Cloud-Secret mehr in GitHub-Secrets, wo OIDC möglich ist; (optional/später) eine Build-Provenance-Attestation für erzeugte Binaries/Container.
- **Priorität / Aufwand.** Welle 2 / M.
- **Hakt ein in.** `ENGINEERING_PLAYBOOK.md` (CI/CD- & Sicherheits-Kapitel: Supply-Chain-Hygiene → -Provenance).
- **Right-Size (Solo/VPS).** SBOM + OIDC zuerst (echter Nutzen, wenig Aufwand). **Zurückgestellt:** volle SLSA-L3-Kette, signierte Provenance-Ketten, Attestation-Verifikation im Deploy — erst relevant, wenn ihr veröffentlichte Artefakte/Container ausliefert oder das Team wächst. Der Self-hosted-VPS-Runner (boxscore) braucht OIDC *nicht* für den lokalen Deploy; nur der Cloud-Runner-Pfad (capsule) profitiert.

## G4 — Agentic Security: Trust-Boundary-Matrix (inkl. Venue-Matrix)

- **Lücke.** Wir haben generisches AppSec + Least-Privilege je Rolle + Frozen Zone — aber **keine explizite Agentic-Security-Schicht**. Sobald Agenten Tools, Hooks, MCP-Server, Auto-Memory, Skills und externe Systeme nutzen, entstehen neue Angriffsflächen: **Prompt-/Instruction-Injection** über Dokumente/Connectoren, **Kontext-/Memory-Poisoning**, **Tool-Missbrauch**, **Rollendrift** durch zu breite Tool-Rechte. Dazu fehlt die **Venue-Matrix** (Rest aus Report-#6): welche Arbeitsart darf in welcher Umgebung laufen.
- **Warum (euer Kontext).** Im **Bypass-Modus** ist das die *dringendste* Lücke: ohne menschliche Freigabe pro Aktion sind Trust-Boundaries und Sandbox das einzige, was einen injizierten oder driftenden Agenten stoppt. „Autonomie durch Guardrails" braucht eine *explizite Karte* dieser Grenzen.
- **Erster Schritt.** Eine `TRUST_BOUNDARIES.md` mit zwei Tabellen: **(a) Trust-Boundary-Matrix** — je Skill/Hook/MCP-Server/Connector/Rolle: vertrauenswürdige Quellen, was nur read-only konsumiert werden darf, verbotene Kommandos/Pfade, freigabepflichtige Aktionen, Injection-/Poisoning-Risiko. **(b) Venue-Matrix** — je Arbeitsart (Recon, Impl, Deploy, Data-Migration, Secret-gebundenes …): erlaubte Laufumgebung (lokal / VPS / CI / Cloud) mit Begründung.
- **Akzeptanzkriterium.** Beide Matrizen existieren und sind im **Execution Plan referenziert**; wo möglich in **Hook-/Managed-Settings-Regeln** übersetzt (z. B. Hook blockt verbotene Pfade/Kommandos via Policy-Stop); **Secret-gebundene Arbeit ist von Cloud-Umgebungen ausgeschlossen**; nicht-vertrauenswürdige Eingaben (externe Dokumente/Connector-Inhalte) sind als „untrusted" markiert und dürfen keine privilegierten Aktionen auslösen.
- **Priorität / Aufwand.** Welle 1 / M.
- **Hakt ein in.** `EXECUTION_PLANNING_AND_GUARDRAILS.md` (Guardrails + Execution Plan) + `MULTI_AGENT_AND_LONGRUN_STRATEGY.md` (Rollen-Tool-Scoping) + `ENGINEERING_PLAYBOOK.md` (Sicherheit).
- **Right-Size (Solo/VPS).** Eine Markdown-Matrix + ein paar Deny-Hooks genügen; kein Threat-Modeling-Tool-Stack, kein TM-BOM. Aber die **Injection-Grenze** (untrusted input → keine privilegierte Aktion) ist nicht verhandelbar, sobald Connectoren/MCP im Spiel sind.

## G5 — Lebenszyklus & Governance der Regeln selbst

- **Lücke.** Wenn Skills, Rollen, Subagenten, Hook-Policies und CLAUDE-Direktiven wachsen, fehlen **Eigentümer, Versionen, Gültigkeitsbereiche, Rezertifizierungs- und Sunset-Regeln**. Sonst werden alte oder projektspezifische „Skill-Wahrheiten" in neue Kontexte geschleppt und **degradieren die Agentenleistung** — genau das Problem, das die Forschung zeigt.
- **Warum (euer Kontext).** Schützt vor **Regelmüll** und vor dem falschen Reflex, jedes Problem mit „noch einer Instruktion" zu lösen. Gerade weil eure Methodik *dokumenten-getrieben* ist, muss die Regel-Ebene selbst gepflegt sein.
- **Erster Schritt.** Ein leichtes **Regel-Registry-Schema** einführen: jeder Skill/jede Rolle/jeder Hook/jede Direktive trägt (Frontmatter oder zentrale `rules-registry.md`): `owner`, `version`, `scope`, `last_validated`, `eval_suite` (Link zu G1), `next_review`, `sunset_criterion`.
- **Akzeptanzkriterium.** Ein Report listet **überfällige Reviews** (`next_review` < heute); ein neuer Regel-Eintrag **ohne diese Felder wird abgelehnt** (Lint/Hook); jede Regel verweist auf ihre Eval-Aufgabe (G1). Bei diesem Schritt entsteht auch die **Konsolidierung**: `docs/INDEX.md` (verknüpft alle fünf Dokumente + Lesereihenfolge), ein konsolidierter **`CLAUDE.md`-Block**, und ein **„Agent-Platform-ADR"**, das Eval-, Telemetrie-, Security- und Provenance-Regeln an einer Stelle bindet.
- **Priorität / Aufwand.** Welle 3 / M.
- **Hakt ein in.** Alle vier Dokumente (Governance-Ebene darüber) + dieses fünfte.
- **Right-Size (Solo/VPS).** `owner` ist erstmal immer dieselbe Person — der Wert liegt in `version`, `last_validated`, `eval_suite`, `sunset`. Kein Governance-Board, kein Freigabe-Workflow — nur die Metadaten + ein Überfälligkeits-Report.

---

# Teil B — Die 5 Zusatzpunkte (Z1–Z5)

*Diese fehlten auch im Deep-Research-Report — sie sind unsere eigene Ergänzung.*

## Z1 — Der Mensch-Review-Flaschenhals

- **Lücke.** Je mehr die Agenten autonom produzieren, desto mehr wird **dein Review/Merge/Checkpoint der limitierende Faktor** — nicht die Agenten. Fünf Nacht-Läufe = fünf Branches am Morgen. Es fehlt eine **Review-Triage-Strategie** und ein Weg, „Review-Schulden" zu vermeiden.
- **Warum (euer Kontext).** Das ist das Skalierungsproblem, das euer *eigenes Autonomie-Ziel* erzeugt. Ohne Triage wird der Morgen-Quercheck zum Engpass, der den ganzen Durchsatzgewinn auffrisst.
- **Erster Schritt.** Ein **Morgen-Digest** (vom Orchestrator erzeugt), der je Branch zusammenfasst: Gate-Status, Diff-Größe, berührte Frozen Zone (ja/nein), Kosten, Anzahl Parks. Dazu ein **Triage-Protokoll**: Reihenfolge nach *Risiko × Reichweite* (Frozen-Zone-/Prod-nahe Branches zuerst, rein additive/getestete zuletzt).
- **Akzeptanzkriterium.** Kein Merge ohne Triage-Durchlauf; der Digest existiert je Nacht-Lauf; Branches sind nach Review-Priorität sortiert; „Review-Schulden" (unreviewte Branches > N Tage) werden sichtbar getrackt.
- **Priorität / Aufwand.** Welle 2 / S (das manuelle Protokoll kann sofort starten, der Digest nutzt G2-Telemetrie).
- **Hakt ein in.** `EXECUTION_PLANNING_AND_GUARDRAILS.md` (Checkpoint/Morgen-Quercheck) + `MULTI_AGENT_AND_LONGRUN_STRATEGY.md` (Morgen-Report).
- **Right-Size (Solo/VPS).** Ein Markdown-Digest + eine Sortierregel genügen. Kein Review-Board, kein Tooling.

## Z2 — Modell-Versions-Regression („immer neuestes Modell")

- **Lücke.** Ihr nutzt *immer das neueste Modell*. Ein neuer Modell-Drop kann dieselbe `CLAUDE.md` **still anders interpretieren** — Verhaltens-Drift ohne Code-Änderung. Es fehlt ein Ritual, das das abfängt.
- **Warum (euer Kontext).** Direkt an eure Praxis gekoppelt: was gestern zuverlässig autonom lief, kann nach einem Modellwechsel subtil anders entscheiden. Ohne Check merkt ihr es erst im Nacht-Lauf.
- **Erster Schritt.** Ein **„Modell-Bump = Eval-Suite fahren"-Ritual** definieren: bei jedem Wechsel auf ein neues Modell wird die G1-Eval-Suite automatisch gegen altes *und* neues Modell gefahren.
- **Akzeptanzkriterium.** Ein Vergleichsreport altes vs. neues Modell existiert; **Verhaltens-Regressionen** (Passraten-Drop, Token-Explosion, neue Gate-Fehler) sind dokumentiert und adressiert, **bevor** der unbeaufsichtigte Nacht-Betrieb auf dem neuen Modell freigegeben wird.
- **Priorität / Aufwand.** Welle 2 / S (baut komplett auf G1 auf).
- **Hakt ein in.** `CODE_CRAFT_AND_DESIGN_STANDARDS.md` + `EXECUTION_PLANNING_AND_GUARDRAILS.md` (Freigabe autonomer Läufe).
- **Right-Size (Solo/VPS).** Reuse der G1-Suite; kein separater Apparat. Trigger kann manuell sein („neues Modell erschienen → Suite fahren → freigeben").

## Z3 — Daten-/PII-Governance (DSGVO)

- **Lücke.** Unsere Sicherheit dreht sich um Secrets/Zugang — aber **nicht** um Daten-Klassifizierung, PII-Minimierung ggü. LLM-Providern, Residency, Aufbewahrung, Consent. `capsule` schickt **Nutzer-Bilder an OpenAI Vision** — personenbezogene Daten an einen Dritt-Dienst.
- **Warum (euer Kontext).** EU-Sitz + personenbezogene Daten an einen US-Dienst = rechtliches Gewicht (DSGVO). Das gehört adressiert, nicht ignoriert. *(Hinweis: keine Rechtsberatung — dies markiert das Governance-Feld, nicht die juristische Lösung.)*
- **Erster Schritt.** Ein **Daten-Klassifizierungs-Dokument**: welche Datenarten verarbeitet das System, welche gehen an welchen Dritt-Dienst? Für LLM-Provider mit PII: AV-Vertrag/DPA-Status prüfen, eine **Minimierungs-Regel** (was NICHT gesendet wird), eine **Aufbewahrungs-/Löschregel**.
- **Akzeptanzkriterium.** Das Klassifizierungs-Dokument existiert; für jeden Dritt-Dienst mit PII ist der DPA-Status dokumentiert; eine Minimierungs-Regel ist definiert und wo möglich als Check verankert (z. B. keine unnötigen Metadaten/Identifikatoren im API-Payload); eine Lösch-/Retention-Regel ist festgelegt.
- **Priorität / Aufwand.** Welle 3 / M.
- **Hakt ein in.** `ENGINEERING_PLAYBOOK.md` (Sicherheit & Kosten → + Daten-Governance) + G4 (Trust-Boundaries).
- **Right-Size (Solo/VPS).** Ein klassifizierendes Markdown + die Minimierungs-/Löschregel genügen zunächst; kein DSGVO-Vollprogramm. Zieht bei Bedarf fachkundige (juristische) Prüfung hinzu.

## Z4 — Produkt-Outcome-Schleife

- **Lücke.** Die (neue) Telemetrie misst **Agenten-Läufe**. Es fehlt die Messung, ob das **gebaute Feature dem Nutzer wirklich dient** — Produkt-Nutzungs-Telemetrie gegen die Success-Factors. „Der Lauf war grün" ≠ „das Feature wirkt".
- **Warum (euer Kontext).** Eure Roadmaps nennen Success-Factors — aber die Schleife wird nicht geschlossen. Autonome Produktivität ohne Outcome-Messung baut effizient möglicherweise das Falsche.
- **Erster Schritt.** Je ausgeliefertem Success-Factor **eine messbare Produkt-Kennzahl** definieren (Nutzung/Erfolg) und aus **Produkt-Telemetrie** erheben — bewusst getrennt von der Agenten-Telemetrie (G2).
- **Akzeptanzkriterium.** Je Success-Factor existiert eine Kennzahl mit Datenquelle; ein periodisches Review prüft, ob gelieferte Features die Kennzahl bewegen; Roadmap-Items **ohne messbaren Outcome** werden markiert (und damit bewusst als „Bauchgefühl" ausgewiesen).
- **Priorität / Aufwand.** Welle 3 / M.
- **Hakt ein in.** `MULTI_AGENT_AND_LONGRUN_STRATEGY.md` (Agent-Ready-Roadmap: Success-Factors) + `EXECUTION_PLANNING_AND_GUARDRAILS.md` (DoD).
- **Right-Size (Solo/VPS).** Wenige Kern-Kennzahlen genügen; kein Analytics-Schwergewicht. Schon eine einfache Ereignis-Zählung + die `/status`-Datenfrische-Idee reichen als Start.

## Z5 — Flaky-Test-Handhabung im autonomen Kontext

- **Lücke.** Wir sagen „Ursache fixen, Gate nie aufweichen" — aber es gibt **keinen expliziten Flaky-Test-Quarantäne-Prozess**. Gefährlich autonom: ein flakiges Gate **trainiert den Agenten zum Retry-bis-grün**, was echte Fehler maskiert.
- **Warum (euer Kontext).** Im Bypass-/Nacht-Setup ist das ein scharfer Rand: Nicht-Determinismus + „Retry bis grün" = stille Fehler, die live gehen.
- **Erster Schritt.** Eine **Flaky-Policy**: erkannter Flaky-Test (wiederholter Lauf, nicht-deterministischer Ausgang) wird explizit als `@flaky`/Quarantäne markiert — mit **Ticket + Owner + Frist** — aus dem *blockierenden* Gate genommen, aber **sichtbar getrackt**. Ein Hook verbietet, ein Gate **allein durch Wiederholung** zu passieren (Retry nur nach Ursachen-Notiz).
- **Akzeptanzkriterium.** Flaky-Tests sind markiert und in einer Quarantäne-Liste mit Frist; der Agent kann ein rotes Gate **nicht** durch bloßes Retry grün bekommen (Policy-Stop); die Quarantäne-Liste wird periodisch abgebaut (Frist überfällig → Alarm).
- **Priorität / Aufwand.** Welle 2 / S–M.
- **Hakt ein in.** `ENGINEERING_PLAYBOOK.md` (Test-Strategie, „nie aufweichen") + `EXECUTION_PLANNING_AND_GUARDRAILS.md` (Guardrails: fail-safe statt fail-open).
- **Right-Size (Solo/VPS).** Ein Marker + eine Liste + ein Anti-Retry-Hook genügen. Kein Flaky-Detection-Service — periodische Wiederholung im CI reicht zur Erkennung.

---

## Alle Einträge auf einen Blick

| ID | Titel | Welle | Aufw. | Akzeptanz (Kurz) |
|---|---|---|---|---|
| **G1** | Eval-Operating-System (5. Gate) | 1 | M | Eval-Report A/B je Aufgabe; neue Regel nur bei Netto-Nicht-Verschlechterung |
| **G2** | Agent-Telemetrie (OTel) | 1 | S–M | Dashboard je Lauf (Tokens/Kosten/Loops/Tool-Decisions), `prompt.id`-korreliert, im Report automatisch |
| **G3** | Release-Provenance (right-sized) | 2 | M | SBOM je Release; OIDC statt langlebiger Cloud-Secrets |
| **G4** | Trust-Boundary- + Venue-Matrix | 1 | M | Beide Matrizen, im Execution Plan referenziert, wo möglich als Hook-Policy; Secret-Arbeit ≠ Cloud |
| **G5** | Regel-Lebenszyklus + Konsolidierung | 3 | M | Registry mit owner/version/eval/next_review/sunset; Überfälligkeits-Report; `docs/INDEX.md` + `CLAUDE.md`-Block + Agent-Platform-ADR |
| **Z1** | Review-Triage | 2 | S | Morgen-Digest je Branch; Merge nur nach Risiko×Reichweite-Triage |
| **Z2** | Modell-Bump-Ritual | 2 | S | Eval alt vs. neu bei Modellwechsel; Regressionen adressiert vor Nacht-Freigabe |
| **Z3** | Daten-/PII-Governance (DSGVO) | 3 | M | Klassifizierung + DPA-Status + Minimierungs-/Löschregel |
| **Z4** | Produkt-Outcome-Schleife | 3 | M | Kennzahl je Success-Factor; Items ohne Outcome markiert |
| **Z5** | Flaky-Quarantäne | 2 | S–M | Markierte Flaky-Liste mit Frist; kein „Retry-bis-grün" (Policy-Stop) |

## Empfohlene Sequenz (mit Abhängigkeiten)

```
WELLE 1 (Sofort)
  G2 Telemetrie ───────────────┐   (liefert Daten für Z1, Z5)
  G1 Eval-Set ─────────────────┼─┐ (Voraussetzung für Z2 + das 5. Gate)
  G4 Trust-Boundary + Venue ───┘ │ (dringendste Bypass-Lücke)
                                 │
WELLE 2 (Kurzfristig)            │
  Z1 Review-Triage ◄── nutzt G2  │
  Z5 Flaky-Quarantäne ◄── G2     │
  Z2 Modell-Bump-Ritual ◄────────┘ nutzt G1
  G3 Release-Provenance
                                 
WELLE 3 (Reife & Konsolidierung)
  G5 Regel-Lebenszyklus + docs/INDEX.md + CLAUDE.md-Block + Agent-Platform-ADR  ◄── verweist auf G1-Evals
  Z3 Daten-/PII-Governance
  Z4 Produkt-Outcome-Schleife
```

**Merksatz zur Reihenfolge:** Erst *messen* können (G1/G2), dann die *Ränder sichern* (G4 + Welle 2), dann *governen und den Kreis schließen* (G5 + Welle 3).

## Kreuz-Referenz — wie der Backlog den Kreis zu den vier Dokumenten schließt

| Bestehendes Dokument | Wird erweitert durch |
|---|---|
| **ENGINEERING_PLAYBOOK.md** | G2 (Agenten-Observability neben Produkt-Health) · G3 (Supply-Chain → Provenance) · Z3 (Daten-Governance) · Z5 (Flaky in Test-Strategie) |
| **MULTI_AGENT_AND_LONGRUN_STRATEGY.md** | G2 (Orchestrator-Metriken) · G4 (Rollen-Trust-Boundaries) · Z1 (Morgen-Digest/Triage) · Z4 (Success-Factor-Kennzahlen) |
| **EXECUTION_PLANNING_AND_GUARDRAILS.md** | **G1 (das fünfte Gate)** · G4 (Matrizen im Execution Plan + als Managed-Settings/Hooks) · Z1 (Checkpoint) · Z2 (Freigabe autonomer Läufe) · Z5 (fail-safe) |
| **CODE_CRAFT_AND_DESIGN_STANDARDS.md** | G1 (Verifikations-Denke) · Z2 (Modell-Regression) |
| **(neu, übergreifend)** | G5 (`docs/INDEX.md` + konsolidierter `CLAUDE.md`-Block + Agent-Platform-ADR bindet Eval/Telemetrie/Security/Provenance an einer Stelle) |

## Definition of Done für den Backlog selbst

Dieser Backlog gilt als „abgearbeitet", wenn: **das fünfte Gate (G1) scharf ist · Telemetrie je Lauf fließt (G2) · die Trust-Boundary- + Venue-Matrix existiert und in Execution Plan/Hooks wirkt (G4) · SBOM+OIDC stehen wo relevant (G3) · Review-Triage, Modell-Bump-Ritual und Flaky-Policy gelebt werden (Z1/Z2/Z5) · die Regel-Registry + Konsolidierung (`docs/INDEX.md`, `CLAUDE.md`-Block, Agent-Platform-ADR) existiert (G5) · Daten-Governance und Produkt-Outcome-Schleife angelegt sind (Z3/Z4).**

Jeder Eintrag folgt dabei der Hausregel: **klein schneiden, mit Test/Check absichern, Doku im selben Arbeitsblock, im Zweifel die 20-%-Variante.**

---

*Fünftes Dokument des Korpus. Companion zu `ENGINEERING_PLAYBOOK.md`, `MULTI_AGENT_AND_LONGRUN_STRATEGY.md`, `EXECUTION_PLANNING_AND_GUARDRAILS.md`, `CODE_CRAFT_AND_DESIGN_STANDARDS.md`. Lebendes Dokument — abgearbeitete Einträge werden als erledigt markiert (mit Datum + Beleg), neue Lücken additiv ergänzt. Die Prinzipien — messen bevor man optimiert, Ränder sichern bevor man skaliert, right-sizen statt Enterprise-Ballast — bleiben.*
