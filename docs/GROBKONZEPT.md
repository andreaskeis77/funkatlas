# Grobkonzept — FunkAtlas · v0.2

**Multi-Netz-WLAN-Analyseplattform für das Haus Keis — Stand nach Interview-Runde 1 (13.07.2026). Ersetzt v0.1.**

> **Status.** Konzept-Stufe des Methodik-Lebenszyklus (Konzept → Ausführungsplanung → Checkpoint → autonomer Lauf). Die Interview-Antworten F1–F15 sind als Entscheidungen **E1–E14** fixiert. Nächster Schritt: Repo-Anlage + Plan-Pass für M0/M1 (Anhang A).
>
> **Feature-Sicht:** `ROADMAP.md` (Meilensteine M0–M11 in Owner-Sprache). Dieses Dokument ist die fachlich-technische Referenz dahinter.
>
> **Sprachkonvention.** Doku Deutsch; Code/Identifier/Commits Englisch.

---

## 1. Entscheidungslog (aus Interview-Runde 1)

| # | Entscheidung | Kern / Konsequenz |
|---|---|---|
| **E1** | Name **FunkAtlas**; privates GitHub-Repo `funkatlas`; Umsetzung vollständig via Claude Code | Repo privat wegen Topologie + Bauplänen. (F15) |
| **E2** | **Nachfolger von `wlan`, kein Fork** | Harvest der bewährten Bausteine (FRITZ-Adapter, Schema-Muster, logsink, Supervisor, Task-Runner, Gate, Fixtures) inkl. aller GOTCHAs. |
| **E3** | Stack: Python 3.12 · SQLite/WAL (Medallion) · FastAPI · APScheduler · **kein Docker** | Probe muss nativ ans WLAN-Interface; eine Container-/VM-Schicht würde die Messung selbst verfälschen. Zudem YAGNI. (F10) |
| **E4** | Messgeräte v1: **LaptopAndi** (Dev + Probe + Zentrale) und **Dell** (Probe) | Weitere Geräte werden passiv über die Router-Sicht beobachtet. (F1, F3) |
| **E5** | Dashboard **selbst gebaut**, server-rendered; hoher Usability-/Design-Anspruch | Design-Tokens, a11y maschinell im Gate; **Geschmacks-Checkpoints durch Andreas** sind Pflicht-Stationen. (F11) |
| **E6** | Prioritäten: **Durchsatz > Latenz/Jitter (Videocalls) > Roaming > Abbrüche**; Charakter der Probleme: „läuft meist, hakt sporadisch" | Dauer-Zeitreihen + Ereignis-Korrelation statt Einmal-Messung; Roadmap-Reihenfolge danach geschnitten. (F6, F7) |
| **E7** | **Empfehlungs-Modul JA — nur mit Beweis** | Experiment-Schleife: Empfehlung → Umsetzung durch Mensch → Vorher/Nachher-Messung → Verdict. Verifizierbar statt vertrauensselig. (F8) |
| **E8** | Probe **darf das Client-WLAN wechseln** für Vergleichsrunden — nur mit dokumentiertem Standort; Router bleiben strikt read-only (`Get*` only) | Netzwechsel = geplante, protokollierte Messrunde, nie stiller Nebeneffekt. (F9) |
| **E9** | **Nachtmessungen ja** | Ruhe-Referenz bei wenig Traffic; Energieoptionen von LaptopAndi werden in M1 als Runbook-Punkt geprüft. (F1, F13) |
| **E10** | Datenvolumen-Budget: congstar **160 GB/Monat**, M3 dauerhaft am Netzteil | Speedtest-Budget-Wächter (Default 8 GB/Monat für Messungen im Kreis B, konfigurierbar); iperf3 bleibt LAN-intern und kostet kein Volumen. (F5) |
| **E11** | **Klartext-Geräte-Registry nur lokal** (`config/devices.yaml`, gitignored); Repo/Fixtures pseudonymisiert; Haushalt informiert | Fachkern „wer hängt wo" braucht Klartext — er verlässt den Laptop nicht. (F14) |
| **E12** | **Standorte aus dem Bauplan** (E13-Raumliste); Grundriss-Koordinaten/Heatmap in M9 | Baupläne (EG, 1. OG; Dachboden = ganze Fläche über 1. OG) liegen vor → `assets/floorplans/`. (F4) |
| **E13** | **Doku-/Reporting-Konvention:** `ROADMAP.md` (Feature-Sprache) + `PROJECT_STATE.md` (Stand + Entscheidungen) + Projekt-Seite im Dashboard; Owner-Kommunikation in Meilenstein-Sprache, Technik nur auf Nachfrage | Wird als Reporting-Regel in die Projekt-`CLAUDE.md` geschrieben — gilt für jede Session. (Meta-Wunsch) |
| **E14** | TR-064-Zugang 7590: vermutlich vorhanden („nichts gelöscht") | Verifikation = erster Live-Schritt in M5; bis dahin hermetisch gegen Fixtures. (F12) |
| **E15** | `wlan.exe` wurde nie auf dem Dell in Betrieb genommen (verifiziert 13.07.2026: kein Prozess, kein Task, kein Health) | Keine Altdaten zu übernehmen; Dell ist sauberes Probe-Ziel; M5 sammelt frisch. |

**Mini-Punkt geschlossen (13.07.2026):** `wlan.exe` läuft **nicht** auf dem Dell — verifiziert (kein Prozess, kein Autostart-Task, Health-Endpunkt ohne Antwort). Es gibt keine Altdaten; das Legacy-Projekt bleibt reine Code-Harvest-Quelle (→ E15).

---

## 2. Ist-Aufnahme

### 2.1 Topologie (Screenshots 13.07.2026)

```
KREIS A — Heimnetz                          KREIS B — Work
Telekom DSL 198,2↓/41,3↑ Mbit/s             congstar 4G/5G · 160 GB/Monat
  → FRITZ!Box 7590 · 192.168.178.1            → Netgear Nighthawk M3 · 192.168.1.1
    SSID ULVT18 (2,4+5 GHz)                     SSIDs ULVT18_work (5 GHz, leer!) + _2.4GHz
  → Mesh: FRITZ!Repeater 3000 AX (563 Mbit/s)   → FRITZ!Box 6850 LTE als WLAN-Client
  → 9 aktive Clients                               am 2,4-GHz-Netz (Link 192/192)  ← Engpass B1
                                                  SSID work_mobile_office → Clients
```

### 2.2 Standorte (Bauplan, E12)

| Gerät | Etage | Raum |
|---|---|---|
| FRITZ!Box 7590 | EG | Wohnen-Essen, Außenwand zur Terrasse |
| FRITZ!Repeater 3000 AX | 2. OG (Dachboden, ganze Fläche) | senkrecht über der 7590 |
| Netgear Nighthawk M3 | 1. OG | Büro Andi |
| FRITZ!Box 6850 LTE | 1. OG | Zimmer Hugo |

**Raumliste v1 (Standort-Tags):** EG: `wohnen-essen`, `kueche`, `diele`, `flur`, `terrasse`, `garage` · 1. OG: `buero-andi`, `buero-karen`, `zimmer-hugo`, `schlafzimmer`, `bad`, `dachterrasse` · 2. OG: `dachboden`.

**Räumliche Hypothesen (messbar, keine Urteile):**
- **H1:** Die Mesh-Säule 7590 (EG) ↔ Repeater (2. OG) überspringt das 1. OG — die Arbeits-Etage hat keinen Kreis-A-AP. Erwartung: Kreis-A-Clients im 1. OG zeigen schwache Werte bzw. hängen „schräg" am Repeater darüber oder der Box darunter.
- **H2:** 6850 ↔ Netgear sind Nachbarräume — der 2,4-GHz-Backhaul ist keine Distanz-Folge, sondern Konfigurations-/Verbindungswahl. Erwartung: Umstellung auf 5 GHz (M10-Experiment) verbessert den Work-Kreis deutlich.

### 2.3 Befunde B1–B8 (Kurzform)

**B1** Doppelter Funk-Hop Kreis B mit 2,4-GHz-Backhaul, Netgear-5-GHz leer — Haupt-Engpass-Kandidat. · **B2** LaptopAndi @ 2,4 GHz/117 Mbit/s via Repeater — Dev-Laptop bestätigt (E4). · **B3** SSID-Zoo auf Clients → unkontrolliertes Roaming; via BSSID-Historie messbar. · **B4** Randomisierte MACs + Generic-Namen („linux", `3E:B7:…`) → Geräte-Registry nötig (E11); Identifikation wird Feature (M5 „Geräte-Detektiv"). · **B5** MyFRITZ-Fernzugriff der 7590 aus dem Internet erreichbar — separates Härtungsthema, nicht Teil dieses Projekts. · **B6** M3 am Netzteil bestätigt (E10) — Nachtbetrieb ok. · **B7** Volumen 160 GB → Budget-Wächter (E10). · **B8** Router-UIs lokal via HTTP; Collectors bevorzugen TR-064-TLS (49443), wo verfügbar.

---

## 3. Harvest aus dem Legacy-Projekt `wlan`

Übernommen werden (E2): FRITZ-TR-064-Adapter (DSL/WAN/WLAN/Mesh/Hosts/Event-Log/Settings-Snapshot) mit allen GOTCHAs (SignalStrength = **Prozent, nicht dBm** · 0,1-dB-Einheiten · kbit/s-Syncraten · Byteraten nur aus TotalBytes-Delta · Repeater-TR-064 = 401 → Mesh-Sicht der Box · Windows-`ping` nie `text=True`) · Schema-Muster (SQLite/WAL, additive Migration, striktes UTC-`ts_utc`, Medallion `raw→stg→mart`) · `logsink` (JSONL nach `logs/`, Claude-lesbar) · Supervisor-Muster (**ein DB-Writer**, Heartbeat, `safe_job`) · Task-Runner/Gate/Hooks/CI-Skelett · sanitisierte Fixtures. Eiserne Regel bleibt: **read-only auf allen Routern.**

---

## 4. Systemarchitektur

```
┌─ Messgerät (LaptopAndi, Dell; später Android) ─┐      ┌─ Zentrale (LaptopAndi) ──────────────────────┐
│ probe/                                          │ HTTP │ core/                                        │
│  wlan-status (SSID/BSSID/Band/Kanal/Signal%/   │ ───► │  ingest-API (FastAPI, nur LAN, Token)        │
│   Link-Rate) · ping/jitter/loss · dns           │Token │  SQLite/WAL raw→stg→mart — EIN Writer        │
│  roaming-watcher (BSSID-Wechsel = Event)        │      │  scheduler → collectors:                     │
│  env-scan (Nachbar-WLANs)                       │      │   fritz-collector (7590, 6850) · netgear (M3)│
│  iperf3-client · speedtest (Budget-Wächter)     │      │  iperf3-server · analyze (Schwellen, Events, │
│  switch-runner (Netzwechsel-Runden, E8:         │      │   Experimente) · logsink → logs/ (JSONL)     │
│   nur geplant + Standort-Tag dokumentiert)      │      │  dashboard/ (server-rendered, Tokens, a11y,  │
│  offline-queue (lokale SQLite, store&forward)   │      │   Projekt-Seite aus product-state.json)      │
└──────────────────────────────────────────────────┘      └───────────────────────────────────────────────┘
```

**Kernentscheidungen (fixiert):**
1. **Zwei-Netze-Problem:** Store-and-Forward als Default — jede Probe puffert lokal und liefert nach, sobald die Zentrale erreichbar ist. Option „Overlay-Netz (z. B. Tailscale) verbindet beide Kreise dauerhaft" bleibt als bewusste Owner-Entscheidung für später notiert (neue Dependency = Checkpoint).
2. **Netzwechsel-Messrunden (E8):** Der `switch-runner` fährt geplante Vergleichsrunden (z. B. nachts: je Netz N Minuten messen) — jede Runde trägt Standort-Tag, Beginn/Ende und Grund im Protokoll; danach zurück ins Ausgangsnetz. Kein Wechsel außerhalb geplanter Runden.
3. **Experiment-Modul (E7):** Entität `experiments`: Basislinie (Zeitraum, Metrik-Snapshot) → **Änderungs-Marker** (was wurde wann von Hand geändert) → Nachher-Fenster → automatischer Vorher/Nachher-Report mit Verdict gegen definierte Erfolgs-Metriken. Jede Empfehlung aus M10 verweist auf ihr Experiment.
4. **Eine Wahrheit je Datensorte:** Messzahlen → SQLite · Rohbeleg/Export → `logs/` (append-only Projektion derselben Läufe) · Schwellwerte → `config/thresholds.yaml` · Geräte-Registry → `config/devices.yaml` (lokal, gitignored, E11) · Secrets → `.env` · Version → `__version__` · Projektstand → `product-state.json` (Quelle der Dashboard-Projekt-Seite).
5. **Hermetisches Gate:** Merge-Gate offline gegen Fixtures (auch wenn die Router erreichbar sind); echte Calls nur unter `network`-Marker; Live-Smoke ist ein bewusster separater Schritt.
6. **Frozen Zone (früh einfrieren, nur additiv):** Ingest-API-Contract Probe↔Core (Konsumenten: Windows-Probe, später Android) · `logs/`-Layout + JSONL-Feldnamen · Threshold-/Metrik-Taxonomie · `product-state.json`-Schema.

---

## 5. Datenmodell (Kern)

`devices` (Registry, Klartext lokal — E11) · `networks` (SSID/BSSID/Band/Kanal je Funkzelle; BSSID→AP-Mapping = Schlüssel der Roaming-Diagnose) · `locations` (Raumliste E12; M9: Grundriss-Koordinaten) · `runs` (Messrunde: device, location, network-context, ein `ts_utc`) · `metrics` (type/value/unit) · `events` (Roaming, Abbrüche, Schwellwert-Verletzungen, Router-Log) · `router_snapshots` (Status/Settings + Diff, redacted) · `neighbor_scans` · `experiments` (E7) · `switch_runs` (E8: geplante Netzwechsel-Runden mit Standort).

---

## 6. Meilensteine

Fachliche Referenz der Reihenfolge und Zuschnitte: **`ROADMAP.md`** (M0–M11, Feature-Sprache, Status-Pflege im selben Arbeitsblock). Die Agent-Metadaten je Item (DAG, Parallelisierbarkeit, Datei-Eigentum, maschinelle DoD, Run-Sizing) entstehen beim Plan-Pass je Meilenstein nach Methodik-Dokument 2 §7 — nicht vorab für alles (YAGNI).

---

## 7. Doku- & Orientierungssystem (E13)

| Artefakt | Für wen | Inhalt |
|---|---|---|
| `docs/ROADMAP.md` | **Andreas** | Meilensteine in Feature-Sprache, Status, „danach kannst du" — das Orientierungsdokument. |
| Dashboard-**Projekt-Seite** | Andreas | Version, Features live/in Arbeit, letzter + nächster Meilenstein (aus `product-state.json`) — Projektstand im Browser, ab M3. |
| `docs/PROJECT_STATE.md` | Andreas + Agent | Kanonischer Stand + Entscheidungslog E1…En, fortgeschrieben, nie weggeworfen. |
| `WORKLOG.md` / HANDBACK | Agent (+ Andreas bei Bedarf) | Tranchen-Protokoll, Technik-Detail. |
| `docs/` (ARD, ADRs, DATENSTRATEGIE, RUNBOOK) | Agent | Technische Referenz; Pflege im selben Arbeitsblock. |

**Reporting-Regel (kommt in die Projekt-`CLAUDE.md`):** Statusmeldungen an den Owner immer in Meilenstein-/Feature-Sprache mit Bezug auf `ROADMAP.md`; technische Tiefe nur auf Nachfrage. Antwortformat auf „Wo stehen wir?": zuletzt fertig / in Arbeit / als Nächstes.

---

## 8. Sicherheit & Datenschutz

Secrets nur in `.env` (nie Repo/Logs); least-privilege TR-064-User; TLS wo verfügbar (B8) · PII: Klartext nur in lokaler Registry (E11), Repo/Fixtures/`logs/`-Beispiele pseudonymisiert; Haushalt (Karen, Hugo) informiert — erfasst werden Verbindungs-Metriken, keine Inhalte · Repo privat (E1); Baupläne in `assets/floorplans/` (privates Repo) · Ingest/Dashboard binden nur ins LAN, Token-Auth, kein Inbound aus dem Internet · MyFRITZ-Exposure (B5) = separates Thema · Kosten: keine bezahlten APIs; knappes Gut = Datenvolumen → Budget-Wächter (E10).

---

## 9. Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Netgear-M3-Schnittstelle undokumentiert | M7 beginnt als read-only Spike; Adapter degradiert anmutig |
| Windows-Energieverwaltung unterbricht Nachtmessungen | Energieprofil-Checkliste im Runbook (M1); Heartbeat macht Lücken sichtbar |
| Speedtests vs. 160-GB-Volumen | harter Budget-Wächter (M4); iperf3 LAN-intern |
| Probe auf Arbeitslaptop beeinflusst Arbeit/Messung | leichte Takte als Default; Lastmessungen getaktet + im Datensatz gekennzeichnet |
| Netzwechsel-Runden stören laufende Nutzung | Runden nur geplant (Default: nachts), protokolliert, mit Rückkehr-Garantie ins Ausgangsnetz |
| Store-and-Forward-Lücken | Queue mit Zeitstempeln; Dashboard zeigt Datenfrische je Gerät |
| Randomisierte MACs brechen Zuordnung | Registry + je Messgerät ggf. „private MAC aus" als dokumentierte Owner-Entscheidung |

---

## Anhang A — Kickoff (drei Handgriffe + Prompt für Claude Code)

**Deine drei Handgriffe (einmalig):**
1. Privates GitHub-Repo **`funkatlas`** anlegen (leer, `main`).
2. Ins Repo legen: `docs/methodology/` (die fünf Methodik-Dokumente) · `docs/INDEX.md` · `CLAUDE.md`-Template in den Root · dieses Dokument als `docs/GROBKONZEPT.md` · `ROADMAP_FunkAtlas.md` als `docs/ROADMAP.md` · Baupläne nach `assets/floorplans/`.
3. Claude Code im Repo starten und den Prompt unten geben.

**Kickoff-Prompt (kopieren):**

```text
Onboarding (read-only): Lies vollständig CLAUDE.md, dann docs/INDEX.md, dann
docs/GROBKONZEPT.md und docs/ROADMAP.md. Bestätige Rolle in einem Satz.

Plan-Pass (read-only) für M0 + M1 nach docs/methodology/EXECUTION_PLANNING_AND_GUARDRAILS.md §2:
1. Recon: Grobkonzept §3–§5; Harvest-Quelle github.com/andreaskeis77/wlan
   (adapters, schema, logsink, supervisor, task_runner, fixtures) mit Datei:Zeile-Belegen.
2. Erzeuge den Execution Plan für M0 (Fundament + Harvest) und M1 (Probe v0):
   Tranche-Schnitt, Primitiv-Wahl (Default Single-Session), maschinelle DoD je Tranche,
   Guardrail-Bindung (Router strikt read-only · Gate hermetisch, kein echter Netz-Call ·
   explizite Adds · keine Secrets/PII · Klartext-Registry nie committen).
3. Fülle den PROJEKT-Block der CLAUDE.md aus dem Grobkonzept (inkl. Reporting-Regel E13:
   Owner-Kommunikation in Meilenstein-Sprache, Technik nur auf Nachfrage).
4. STOPP: Lege den Plan zur Diskussion vor (Go/No-Go durch Andreas) und challenge ihn
   aktiv (billigere Wege, Risiken, was NICHT parallelisiert werden sollte).
```

## Änderungslog

- **v0.2 · Nachtrag (2026-07-13):** E15 — Dell verifiziert: `wlan.exe` nie in Betrieb genommen; Mini-Punkt geschlossen.
- **v0.2 (2026-07-13):** Interview-Runde 1 eingearbeitet (E1–E14) · Bauplan-Standorte + Raumliste + Hypothesen H1/H2 · Experiment-Modul & Netzwechsel-Runden · Orientierungssystem (E13) · Docker-Entscheid (E3) · Kickoff-Anhang. Ersetzt v0.1.
- **v0.1 (2026-07-13):** Erstentwurf nach Analyse von Legacy-Repo, Methodik-Korpus und Screenshots.
