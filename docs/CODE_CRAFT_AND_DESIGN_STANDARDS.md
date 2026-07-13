# Engineering-Handwerk & Code-Standards

**Companion zu `ENGINEERING_PLAYBOOK.md`, `MULTI_AGENT_AND_LONGRUN_STRATEGY.md` und `EXECUTION_PLANNING_AND_GUARDRAILS.md` — wie autonome Agenten *guten* Code und gute Oberflächen produzieren.**

> **Zweck.** Dieses Dokument gibt die Methodik und die **Vorgaben** für das Handwerk selbst: Test-First und verwandte Entwicklungs-Ansätze, UX-/Usability-Methodik, Code-Level-Standards, Code-Dokumentation, sowie Software-Architektur & Design-Patterns. Durchgängig als **Direktiven für autonome Agenten** formuliert — jede Vorgabe ist möglichst *maschinell selbst-prüfbar*, damit ein Agent sie ohne Mensch durchsetzen kann. Geerdet an den real bewährten Mustern aus `capsule` und `boxscore`. Projekt-unabhängig.
>
> **Leitsatz.** **Guter Code ist korrekt, verifizierbar, additiv und langweilig.** Nicht clever, nicht maximal abstrakt — sondern für den nächsten Agenten (und Menschen) sofort verständlich, durch Tests gegen die Wahrheit gesichert, und ohne Seiteneffekte rücknehmbar.
>
> **Die drei Handwerks-Fallen bei starken Modellen** (gegen die alles hier verteidigt): (1) **vacuous tests** — Tests, die immer grün sind; (2) **Über-Engineering** — Abstraktionen/Patterns ohne Bedarf; (3) **geratener Geschmack** — UI, die der Agent nicht autonom verantworten kann. Jede Sektion adressiert diese.
>
> **Sprachkonvention.** Doku/Kommunikation Deutsch; Code/Identifier/Commits/Docstrings Englisch.

---

## Inhaltsverzeichnis

0. [Was „gut" bedeutet — die Code-Qualitäts-Achsen](#0-was-gut-bedeutet--die-code-qualitäts-achsen)
1. [Test-First als Default-Methodik](#1-test-first-als-default-methodik)
2. [Das Methodik-Portfolio (welcher Ansatz wann)](#2-das-methodik-portfolio-welcher-ansatz-wann)
3. [UX-/Usability-Methodik für autonome Entwicklung](#3-ux-usability-methodik-für-autonome-entwicklung)
4. [Code-Vorgaben — wie man guten Code schreibt](#4-code-vorgaben--wie-man-guten-code-schreibt)
5. [Code-Dokumentation (rudimentär, aber ausreichend)](#5-code-dokumentation-rudimentär-aber-ausreichend)
6. [Architektur & Design-Patterns](#6-architektur--design-patterns)
7. [Vorgaben für autonome Agenten (Direktiven-Destillat)](#7-vorgaben-für-autonome-agenten-direktiven-destillat)
8. [Master-Checkliste](#8-master-checkliste)

---

## 0. Was „gut" bedeutet — die Code-Qualitäts-Achsen

Bevor Methoden: woran misst ein Agent (und ein Mensch) „guten Code"? An fünf Achsen, in dieser Priorität:

1. **Korrektheit** — tut, was er soll, *bewiesen durch einen Test gegen die Wahrheit* (nicht durch Plausibilität).
2. **Verständlichkeit** — der nächste Agent/Mensch versteht ihn ohne den Autor. Namen, Struktur, Idiome des Umfelds.
3. **Additivität / Rücknehmbarkeit** — erweitert, ohne bestehende Verträge zu brechen; ohne Seiteneffekt zurücknehmbar.
4. **Testbarkeit** — die Form erlaubt hermetische Tests (injizierbare Abhängigkeiten, reiner Kern).
5. **Sparsamkeit** — die *einfachste* Lösung, die das Problem löst. Keine Abstraktion auf Vorrat (YAGNI).

> Diese Reihenfolge ist eine Konfliktregel: Bei Zielkonflikt gewinnt die höhere Achse. „Eleganz" steht bewusst *nicht* auf der Liste — sie ist ein Nebenprodukt von 2 und 5, kein Ziel.

---

## 1. Test-First als Default-Methodik

### 1.1 Der Zyklus (Red → Green → Refactor)

Für jede Einheit mit definierbarem Vertrag:

1. **Red** — den Test *zuerst* schreiben und ihn **fehlschlagen sehen.** Das ist nicht optional: Ein nie-rot-gewesener Test beweist nicht, dass er etwas einschränkt.
2. **Green** — die *kleinste* Implementierung, die den Test grün macht.
3. **Refactor** — aufräumen (Namen, Duplikate, Struktur), Tests bleiben grün.

### 1.2 Warum TDD und KI-Agenten zusammengehören

Der Test ist die **ausführbare Spec.** Ein autonomer Agent hat damit eine *objektive Wahrheit*, gegen die er arbeitet — das ist „verifizierbar statt vertrauensselig" in Reinform. Red-Green-Refactor läuft autonom; das grüne Gate *beweist* „done". Ohne diese ausführbare Wahrheit ist autonome Entwicklung blindes Raten.

### 1.3 Die zwei Fallen — und ihre Abwehr

- **Vacuous tests** (Test immer grün / an die Implementierung angepasst): Abwehr = **die Red-Phase ist Pflicht** (Test muss erst fehlschlagen), und **Writer ≠ Reviewer** (Test-Autor-Agent ≠ Implementierungs-Agent, aus der Multi-Agent-Strategie). Optional als Härtung: **Mutation-Testing** stichprobenartig (kleine Code-Mutation einbauen → ein guter Test muss rot werden; bleibt er grün, ist er wertlos).
- **Test gegen die Implementierung statt gegen den Vertrag** (testet *wie*, nicht *was*): Abwehr = Tests prüfen **beobachtbares Verhalten / öffentliche Schnittstelle**, nicht interne Zwischenschritte.

### 1.4 Jeder Bugfix bringt einen Regressionstest

Ein Bug ist ein fehlender Test. Reihenfolge: **erst den fehlschlagenden Test schreiben, der den Bug reproduziert** (Red), *dann* fixen (Green). So kann derselbe Bug nie unbemerkt zurückkehren.

### 1.5 Wann *nicht* strikt TDD

TDD ist der Default für *Logik mit definierbarem Vertrag*. Es ist **nicht** das richtige Werkzeug für: genuin exploratives Arbeiten, wo die *Form* noch unklar ist (→ erst Spike, dann stabilisieren mit Tests), reine UI-Ästhetik (→ §3), und Wegwerf-Prototypen. Für diese: **explore-first**, dann die stabile Erkenntnis mit Tests einfrieren.

---

## 2. Das Methodik-Portfolio (welcher Ansatz wann)

Test-First ist die Basis, aber nicht der einzige methodische Hebel. Welcher Ansatz für welche Arbeit:

| Methodik | Kernidee | Am besten für | Nicht für |
|---|---|---|---|
| **TDD (Red-Green-Refactor)** | Test zuerst, treibt das Design | Logik, Business-Regeln, Daten-Transforms, alles mit klarem In/Out | unklare Form, reine UI-Ästhetik |
| **Contract-/API-Design-First** | Den Vertrag (Schema/Felder/Statuscodes) *vor* der Implementierung festschreiben und maschinell pinnen | mehrkonsumentige Schnittstellen (öffentliche API für Web *und* App), geteilte Taxonomie | rein internes Wegwerf-Stück |
| **Acceptance-/Behavior-First (BDD-Geist)** | Nutzer-sichtbares Verhalten als Akzeptanzkriterium *vor* dem Bau | Features mit klarem Nutzer-Outcome; Success-Factors der Roadmap | tiefe Algorithmen ohne Nutzer-Sicht |
| **Property-Based Testing** | Invarianten statt Einzelbeispiele; das Framework sucht Gegenbeispiele | Daten-/Parser-/Konsistenz-Logik (Round-Trips, „Summe stimmt immer", Idempotenz) | UI, einfache CRUD-Wrapper |
| **Type-Driven** | Illegale Zustände *unrepräsentierbar* machen (Typen/Schemas erzwingen Gültigkeit) | Domänen-Modelle, Zustandsmaschinen, Vertrags-Payloads | dynamische, lose Glue-Skripte |
| **Explore → Stabilize (Spike)** | Erst die Form herausfinden (read-only/Wegwerf), *dann* mit Tests einfrieren | genuin Neues/Unklares; Tech-Evaluierung | Bekanntes mit klarem Vertrag (da direkt TDD) |

**Faustregel:** *Kennst du den Vertrag?* → TDD/Contract-First. *Kennst du das Nutzer-Outcome?* → Acceptance-First. *Hast du Invarianten?* → Property-Based. *Weißt du die Form noch nicht?* → erst Spike, dann Tests. Mehrere kombinieren sich (z. B. Contract-First für die API + TDD für ihre Logik + Property-Based für die Konsistenz-Checks).

---

## 3. UX-/Usability-Methodik für autonome Entwicklung

Die schwierigste Dimension, weil **Geschmack nicht autonom verantwortbar** ist. Die Methodik trennt darum sauber: *was die Maschine garantieren kann* (Struktur, Barrierefreiheit, Konsistenz, Regression) von *was ein Mensch entscheiden muss* (Ästhetik, Layout-Geschmack, Format-Wahl).

### 3.1 Das Prinzip: dem Agenten ein Ziel geben, nicht „entwirf was Schönes"

Ein Agent rät keine Ästhetik. Er bekommt ein **Ziel** und arbeitet darauf hin:

- **Design-Tokens als einzige Quelle der Wahrheit fürs Aussehen** — geschichtet (Kern → semantisch → Komponenten). Eine Änderung oben propagiert überall. **Neue Seiten erfinden keine Ästhetik**, sie verwenden bestehende Tokens/Komponenten.
- **Component-Driven** — eine Bibliothek wiederverwendbarer Komponenten; der Agent komponiert, statt jedes Mal neu zu gestalten. Garantiert Konsistenz.
- **Referenz/Wireframe-First** — für *neue* Oberflächen liefert der Mensch einen Referenzpunkt (Skizze, Vorbild, grobe Struktur). Der Agent setzt *die Referenz* um, statt Geschmack zu erfinden.
- **Feste Templates je Seitentyp** + starke Querverlinkung + **Mobile-First** + Touch-Targets ≥ 44 px.

### 3.2 Accessibility-First (maschinell erzwingbar)

Barrierefreiheit ist *kein* Geschmack, sondern prüfbar — also Pflicht und automatisierbar: semantisches/rollenbasiertes Markup (zugleich a11y-Signal *und* test-stabil), Kontrast 4.5:1 (normal) / 3:1 (groß), Tastaturbedienung, WCAG 2.2 AA via axe im Gate. Das ist der Teil der „guten UX", den der Agent **selbst garantieren** kann.

### 3.3 Teste den Vertrag, nicht die Pixel

UI-Tests (Gate-Kategorie 4) prüfen *Struktur und Verhalten*, nicht Schönheit: Playwright **rollenbasiert** (`getByRole`/`getByLabel`), axe (WCAG), **Visual-Regression** (Screenshot-Baselines fangen *unbeabsichtigte* Änderungen), Link-Integrität, **Lighthouse-Budget** (LCP < 2,5 s / INP < 200 ms / CLS < 0,1). Performance ist messbar → also ein Gate, kein Geschmack.

### 3.4 Die ehrliche Grenze = ein Checkpoint

Eine grüne Maschine ist nicht gute UX (Scanner fangen nur ~30–40 % der a11y-Verstöße; Ästhetik ist Urteil). Darum: Geschmacks-/Layout-/Format-Entscheidungen werden **nicht geraten**, sondern als **Mensch-Checkpoint** offen gehalten und für Feedback geöffnet. Die Tests sind das *Regressionsnetz*; das Urteil über die Erfahrung bleibt beim Menschen.

### 3.5 Der UX-Arbeitsfluss eines autonomen Agenten

```
Referenz/Wireframe (Mensch)  →  Tokens & Komponenten anwenden (Agent)
   →  rollenbasierte Struktur + a11y (Agent, maschinell geprüft)
   →  Visual-Baseline + Lighthouse-Gate (Agent)
   →  GESCHMACKS-CHECKPOINT (Mensch: sieht es richtig aus / fühlt es sich gut an?)
   →  Feedback eingearbeitet, Baseline aktualisiert
```

---

## 4. Code-Vorgaben — wie man guten Code schreibt

Verbindliche Standards, möglichst **maschinell selbst-prüfbar** (damit ein Agent sie ohne Mensch durchsetzt). Geordnet nach den Qualitäts-Achsen aus §0.

### 4.1 Korrektheit & Verifizierbarkeit
- Nichts gilt als fertig ohne Test gegen die Wahrheit. **Correctness vor Cleverness.**
- **Idempotenz** überall, wo ein Lauf wiederholbar sein muss (Ingest, Build, Migration, Generierung) — kein Doppel-Effekt, keine Doppelkosten.

### 4.2 Struktur & Verständlichkeit
- **Kleine, kohäsive Funktionen**, eine Verantwortung; tiefe Verschachtelung vermeiden (früh returnen).
- **Hohe Kohäsion, lose Kopplung.** Module kennen so wenig voneinander wie möglich.
- **Explizit vor implizit.** Sprechende Namen; keine magischen Werte (benannte Konstanten); klare Signaturen.
- **Im Stil des Umfelds schreiben** — Kommentar-Dichte, Namens-Idiome, Muster des umgebenden Codes übernehmen. Konsistenz schlägt persönlichen Stil.
- **Reiner Kern, unreiner Rand.** Geschäftslogik rein/deterministisch; I/O, Netz, Zeit, Zufall an den Rand — über injizierbare Schnittstellen (das macht §1 hermetisch testbar).

### 4.3 Additivität (gegen invasive Änderungen)
- **Additiv vor invasiv.** Neue Felder/Tabellen/Routen additiv; bestehende Verträge unberührt. Breaking Change = bewusster, versionierter Akt (neue API-Version), nie nebenbei.
- **Additive Schema-Evolution** als festes Muster (`_CREATE_…_SQL` + Guard + zentrale `ensure_schema()` + Index + Migrationsversion), verifiziert gegen frische tmp-DB.

### 4.4 Fehlerbehandlung
- **Non-blocking Error Design:** nutzer-sichtbare Endpunkte degradieren strukturiert — Fehler → `HTTP 200 + {"ok": false, "error": …}` (überlebt Proxy-5xx-Rewrites), **nie** 500/Traceback.
- **Best-effort-Seiteneffekte gekapselt** (Cost-Logging, Audit-Historie): eigene Connection, Fehler geschluckt, Hauptpfad nie gebrochen.
- **Anmutige Entartung:** fehlt eine optionale Quelle, läuft das Produkt degradiert weiter statt zu crashen.

### 4.5 Sparsamkeit (gegen Über-Engineering — die Agenten-Falle)
- **YAGNI.** Keine Abstraktion/Konfigurierbarkeit „für später". Bau, was *jetzt* gebraucht wird.
- **Regel der Drei:** Ein Pattern/eine Abstraktion wird erst eingeführt, wenn dieselbe Variation **dreimal** real auftritt — nicht antizipativ.
- **Begründungs-Pflicht:** Führt ein Agent ein Design-Pattern oder eine neue Abstraktion ein, gehört *eine Zeile Begründung* in den Commit/Worklog (welche konkrete Duplikation/Variation es auflöst). Ohne Begründung → kein Pattern.
- **Kein toter Code, keine ungenutzten Importe** im *berührten* Code (im Gate als ruff-kritisch eng selektiert; Stilfunde im Umfeld aufräumen).

### 4.6 Maschinelle Durchsetzung
- **Lint/Typen als Basis** (statische Analyse vor jedem Gate).
- **Gate-Lint „kritisch"** eng selektiert (Syntax/Undefined-Name); voller Lint im berührten Code.
- **Secret-Scan + explizite Adds** (`git add <pfad>`, nie `-A`).

---

## 5. Code-Dokumentation (rudimentär, aber ausreichend)

Das Ziel ist das **Minimum, das Autonomie überlebt**: genug, dass die nächste Session/der nächste Agent ohne den Autor weiterarbeiten kann — *nicht* mehr, denn überflüssige Doku driftet und lügt mit der Zeit.

### 5.1 Die Ebenen (von „immer" bis „nur wenn nötig")

| Ebene | Vorgabe |
|---|---|
| **Selbst-dokumentierender Code** | *Die* Grundlage. Sprechende Namen, klare Struktur — Code, der sich selbst erklärt, braucht weniger Kommentar. |
| **Docstring auf jeder öffentlichen/exportierten Schnittstelle** | Pflicht. Was sie tut, Inputs/Outputs, was sie wirft/zurückgibt bei Fehlern. Interne Helfer nur, wenn nicht offensichtlich. |
| **„Warum"-Kommentare** | Für nicht-offensichtliche Entscheidungen: *warum so und nicht anders* (Workaround, Reihenfolge-Zwang, Encoding-Eigenheit). Nie das *Was* der Zeile wiederholen. |
| **Modul-/Datei-Header** | Ein bis zwei Sätze: Zweck des Moduls, Rolle im System. |
| **Vertrags-/Präzedenz-Notizen** | Wo eine Auflösungsreihenfolge oder ein Vertrag gilt (z. B. „kwarg > env > default", „item_images zuerst, dann FS-Fallback") — kurz dokumentiert, weil nicht aus dem Code ablesbar. |
| **ADRs** | Architektur-Entscheidungen separat (Kontext/Entscheidung/Konsequenz). Code-Kommentare erklären *Zeilen*; ADRs erklären *Entscheidungen*. |

### 5.2 Was *nicht* dokumentiert wird
Offensichtlichen Code (`i += 1  # increment i`), Restatement der Signatur, auskommentierten Altcode (gehört gelöscht — Git ist das Gedächtnis), Doku, die den Code dupliziert (driftet garantiert).

### 5.3 Die Anti-Drift-Regel
Doku lebt **neben** dem Code und wird **im selben Arbeitsblock** aktualisiert. Eine Code-Änderung mit veralteter Doku gilt als **unvollständig** (Doku-Governance). Bei architektur-/API-/persistenz-/security-wirksamen Änderungen sind die kanonischen Referenzdokumente (ARD, ADRs, Runbooks) mitzuziehen.

> **Merksatz:** Dokumentiere *Verträge und Begründungen*, nicht *Mechanik*. Die Mechanik steht im (lesbaren) Code; die Tests beweisen sie.

---

## 6. Architektur & Design-Patterns

### 6.1 Die Meta-Regel

**Patterns dienen Testbarkeit, Additivität und „eine Wahrheit je Datensorte" — nicht der Eleganz.** Ein Pattern wird eingeführt, *weil eine konkrete Variation/Duplikation es verlangt* (Regel der Drei, §4.5), nie antizipativ. Das ist die wichtigste Architektur-Direktive für autonome Agenten — sie verhindert die Über-Engineering-Falle.

### 6.2 Der bewährte Pattern-Katalog (aus `capsule` & `boxscore`)

Diese Muster haben sich in den realen Projekten getragen — sie sind der empfohlene Startsatz, weil jedes ein konkretes Methodik-Ziel bedient:

| Pattern | Wozu / warum es zur Methodik passt | Beleg im Code |
|---|---|---|
| **Adapter (je Datenquelle)** | Jede neue Quelle = ein Adapter mit Feld-Contract (`fetch → validate → parse`), **ohne Kern-Umbau** → additiv + isoliert testbar | `pipeline/adapters`, „neue Quelle = neuer Adapter" |
| **Dependency Injection** | Externe Calls (HTTP-Transport, LLM-Client, DNS-Resolver, Zeit, Cost-Recorder) als Parameter → **hermetische Offline-Tests** bei realem Code-Pfad | injizierbare Transports/Clients in der Test-Strategie |
| **Facade** | Eine schmale Komposition vor mehreren Subsystemen (z. B. zwei Frameworks co-hosted) → ein klarer Einstiegspunkt | `src.api.v2.facade` |
| **Repository** | Datenzugriff hinter einer Schnittstelle → Persistenz vom Rest entkoppelt, testbar | `test_dashboard_repository` |
| **Medallion (`raw → staging → marts`)** | Roh = Versicherung (nie transformieren); bereinigte Schicht = wo die Bugs sind (am meisten testen); geschäftsfertig = Konsumenten | Datenpipeline-Schichtung |
| **Circuit Breaker / resilienter Client** | Timeout + beschränkte Retries mit Backoff + Fehlerklassen + getypte Ergebnisse; **wirft nie nach außen** | OpenAI-Client-Resilienz (eigenes ADR) |
| **Feature Flags** | Gemerged ≠ aktiv → Deploy und Aktivierung entkoppelt; `main` immer auslieferbar | `product-state.json`-Flags |
| **Frozen Zone / Contract-Pin** | Mehrkonsumentige Verträge (öffentliche API für Web *und* App) maschinell gepinnt; nur additiv erweiterbar | `/api/v2` als *ein* kanonischer Vertrag |
| **Non-blocking Error Envelope** | Fehler als `{"ok": false}` statt 500 → Hauptpfad unzerstörbar | `error_contract` |
| **Strategy (zweispurig)** | Austauschbare/parallele Verfahren nebeneinander (Markt-Konsens *neben* eigenem Modell) | Predictions: Markt vs. eigenes Elo-Modell |

### 6.3 Architektur-Prinzipien (über Einzel-Patterns hinaus)
- **Separation of Concerns / Ports-and-Adapters-Neigung:** Geschäftslogik im Zentrum (rein, testbar), I/O an den Rändern (Adapter). Erlaubt hermetische Tests und additive Erweiterung.
- **Eine Wahrheit je Datensorte** (Zahlen → DB, Texte → Git, Vokabular → Taxonomie, Aussehen → Tokens). Konflikt = Fehler, kein stilles Überschreiben.
- **Additiv vor invasiv** auf Architektur-Ebene: neue Tabelle/Route/Modul statt Eingriff in geteilten Code → maximiert die parallelisierbare Fläche (Multi-Agent-Strategie).
- **Das Produkt kennt sich selbst:** Status-Seite + Versionskonstante/Release-Manifest als Architektur-Bestandteil, nicht als Nachgedanke.

### 6.4 Die Anti-Pattern-Warnung
Cargo-Cult-Patterns (ein Pattern, „weil man das so macht"), spekulative Generalität (Konfigurierbarkeit für nie eintretende Fälle), tiefe Vererbungshierarchien (Komposition bevorzugen), God-Objects/God-Modules. Ein Agent neigt zu allen vieren — die Regel der Drei + Begründungs-Pflicht sind die Gegenmittel.

---

## 7. Vorgaben für autonome Agenten (Direktiven-Destillat)

Die handlungsleitende Kurzform für `CLAUDE.md` — jede Direktive mit ihrem Selbst-Check:

| Direktive | Selbst-Check (maschinell, wo möglich) |
|---|---|
| **Test zuerst, fehlschlagen sehen, dann implementieren** | Existiert ein Test, der *vor* dem Code rot war? |
| **Test-Autor ≠ Implementierer** (bei Multi-Agent) | Verschiedene Rollen/Sessions? |
| **Teste Vertrag/Verhalten, nicht Interna** | Prüft der Test die öffentliche Schnittstelle? |
| **Jeder Bugfix bringt einen reproduzierenden Regressionstest** | War der Regressionstest erst rot? |
| **Correctness vor Cleverness; YAGNI** | Ist es die einfachste Lösung, die das Gate besteht? |
| **Pattern nur bei realer Variation (Regel der Drei) + 1 Zeile Begründung** | Steht die Begründung im Commit/Worklog? |
| **Additiv vor invasiv; Frozen Zone unberührt** | Bestehende Verträge unverändert? Contract-Test grün? |
| **Reiner Kern, I/O an den Rand (injizierbar)** | Läuft der Test offline/hermetisch? |
| **Fehler strukturiert (`{"ok":false}`), nie 500/Traceback** | Smoke zeigt sauberes JSON statt Crash? |
| **Docstring auf jeder neuen öffentlichen Schnittstelle; „Warum"-Kommentar bei Nicht-Offensichtlichem** | Öffentliche Funktion ohne Docstring? |
| **Doku im selben Arbeitsblock (sonst unvollständig)** | ARD/ADR/Runbook bei wirksamer Änderung mitgezogen? |
| **Im Stil des Umfelds; kein toter Code/ungenutzte Importe im berührten Code** | ruff-kritisch grün im Diff? |
| **UI: Tokens/Komponenten nutzen, a11y maschinell, Geschmack = Mensch-Checkpoint** | axe + Visual-Baseline + Lighthouse grün? Checkpoint gesetzt? |
| **Explizite Adds, kein `git add -A`; keine Secrets** | Secret-Scan (staged) grün? |

---

## 8. Master-Checkliste

**Qualitäts-Achsen** — Korrektheit > Verständlichkeit > Additivität > Testbarkeit > Sparsamkeit; bei Konflikt gewinnt die höhere Achse; Eleganz ist Nebenprodukt, kein Ziel.

**Test-First** — Red (fehlschlagen sehen) → Green (kleinste Lösung) → Refactor · Test = ausführbare Spec für den Agenten · Vacuous-Test-Abwehr (Red-Pflicht, Writer≠Reviewer, optional Mutation-Test) · Vertrag statt Interna testen · Bugfix = reproduzierender Regressionstest · explore-first nur bei unklarer Form.

**Methodik-Portfolio** — Vertrag bekannt → TDD/Contract-First · Nutzer-Outcome bekannt → Acceptance-First · Invarianten → Property-Based · illegale Zustände → Type-Driven · Form unklar → Spike-then-stabilize · Ansätze kombinieren.

**UX** — dem Agenten ein Ziel geben (Tokens/Komponenten/Referenz), nicht „entwirf schön" · Accessibility-First maschinell erzwingen · Vertrag statt Pixel testen (Rollen/axe/Visual-Baseline/Lighthouse) · Geschmack = Mensch-Checkpoint · UX-Arbeitsfluss endet am Geschmacks-Checkpoint.

**Code-Vorgaben** — Correctness vor Cleverness · kleine kohäsive Funktionen, lose Kopplung · explizit vor implizit · reiner Kern/unreiner Rand · additiv vor invasiv · non-blocking Errors · YAGNI + Regel der Drei + Begründungs-Pflicht · kein toter Code · Lint/Typen als Basis.

**Dokumentation** — selbst-dokumentierender Code als Basis · Docstring auf öffentlichen Schnittstellen · „Warum" statt „Was" · Modul-Header · Verträge/Präzedenz notieren · ADRs für Entscheidungen · nichts Offensichtliches dokumentieren · Anti-Drift (gleicher Arbeitsblock).

**Architektur & Patterns** — Patterns dienen Testbarkeit/Additivität/eine-Wahrheit, nicht Eleganz · bewährter Katalog (Adapter, DI, Facade, Repository, Medallion, Circuit Breaker, Feature Flags, Frozen Zone, Error Envelope, Strategy) · Ports-and-Adapters-Neigung · additiv maximiert parallele Fläche · Anti-Pattern (Cargo-Cult, spekulative Generalität, tiefe Vererbung, God-Objects) vermeiden.

---

*Companion zu `ENGINEERING_PLAYBOOK.md`, `MULTI_AGENT_AND_LONGRUN_STRATEGY.md`, `EXECUTION_PLANNING_AND_GUARDRAILS.md`. Lebendes Dokument. Die Patterns sind an `capsule`/`boxscore` geerdet; die Prinzipien — guter Code ist korrekt, verifizierbar, additiv und langweilig; Tests als ausführbare Spec; Patterns nur bei realem Bedarf; Geschmack als Mensch-Checkpoint — bleiben werkzeug-unabhängig.*
