# ROADMAP — FunkAtlas

**Das Orientierungsdokument. Meilensteine in Feature-Sprache: was du nach jedem Schritt kannst.**

> **So liest du dieses Dokument.** Jeder Meilenstein beschreibt ein *für dich sichtbares Ergebnis* — nicht die Technik dahinter. Status: ⬜ offen · 🔨 in Arbeit · ✅ fertig (mit Datum). Die Reihenfolge folgt deinen Prioritäten (Durchsatz > Latenz/Videocalls > Roaming > Abbrüche).
>
> **So bleibt es aktuell (Pflege-Regel).** Claude Code schreibt dieses Dokument **im selben Arbeitsblock** fort, in dem ein Meilenstein-Fortschritt passiert — eine Änderung ohne aktualisierte Roadmap gilt als unvollständig. Technik-Details leben in `docs/PROJECT_STATE.md` und im Worklog; hier steht nur, was du davon *hast*.
>
> **Das „Wo stehen wir?"-Ritual.** Wenn du in irgendeiner Session fragst „Wo stehen wir?", ist die Antwort immer: (1) letzter fertiger Meilenstein, (2) was gerade in Arbeit ist, (3) was als Nächstes kommt — in dieser Sprache. Technik nur auf Nachfrage. Zusätzlich zeigt das Dashboard ab M3 eine **Projekt-Seite** mit genau diesem Stand (Version, Features live / in Arbeit) — du kannst den Projektstatus also auch einfach im Browser nachschauen.

---

## Überblick

| # | Meilenstein | Danach kannst du … | Status |
|---|---|---|---|
| M0 | Projektfundament | (noch nichts sehen — aber alles Weitere steht auf sicherem Boden) | ⬜ |
| M1 | Erste Messwerte | zum ersten Mal echte Zahlen deines WLANs sehen | ⬜ |
| M2 | Zentrale & zweites Gerät | Messwerte beider Laptops in einem gemeinsamen Datenpool sammeln | ⬜ |
| M3 | Dashboard v1 | dein Netz im Browser sehen — auch vom Handy | ⬜ |
| M4 | Durchsatz & Call-Tauglichkeit | „Reicht die Leitung gerade für Teams?" mit einem Blick beantworten | ⬜ |
| M5 | Router-Innensicht Kreis A | sehen, wer an welchem AP hängt — ohne FRITZ!Box-Oberfläche | ⬜ |
| M6 | Störungs- & Roaming-Detektiv | nachschauen, *warum* es um 20:14 Uhr gehakt hat | ⬜ |
| M7 | Work-Kreis-Innensicht | 5G-Signal & Datenverbrauch (160-GB-Budget) live verfolgen | ⬜ |
| M8 | Umfeld & Kanäle | sehen, welche Nachbar-Netze auf euren Kanälen funken | ⬜ |
| M9 | Hauskarte | Signalstärke je Raum auf deinem Bauplan sehen | ⬜ |
| M10 | Empfehlungen mit Beweis | Optimierungen umsetzen und den Effekt *gemessen* bestätigt bekommen | ⬜ |
| M11 | Handy misst mit | mit dem Android-Handy an jedem Punkt im Haus messen | ⬜ |

---

## Die Meilensteine im Detail

### M0 — Projektfundament ⬜
**Danach kannst du:** noch nichts Sichtbares — aber jede spätere Funktion entsteht abgesichert (Tests, Qualitäts-Gate, saubere Regeln) und die bewährten FRITZ!Box-Bausteine aus dem Vorgängerprojekt sind übernommen.
**Inhalt:** Privates Repo `funkatlas`, Arbeitsregeln (`CLAUDE.md`), Qualitäts-Gate, geerntete FRITZ-Adapter aus `wlan`.
**Fertig, wenn:** das Gate auf dem Gerüst `GESAMT: PASS` meldet und die geernteten Bausteine ihre Tests bestehen.
*Agent-Notiz: 1–2 Tranchen · nacht-tauglich: ja · Checkpoint: keiner.*

### M1 — Erste Messwerte ⬜
**Danach kannst du:** auf LaptopAndi die ersten echten Zahlen sehen: Signalstärke, Band, verbundener AP, Ping-Zeiten — und über Nacht laufen lassen für eine erste Ruhe-Referenz.
**Inhalt:** Mess-Programm (Probe) v0: WLAN-Status + Ping/DNS, Speicherung lokal (Datenbank + `logs/`).
**Fertig, wenn:** eine Nacht Messreihe vorliegt und der „logs == Datenbank"-Test grün ist.
*Agent-Notiz: 2–3 Tranchen · nacht-tauglich: ja · Checkpoint: keiner.*

### M2 — Zentrale & zweites Gerät ⬜
**Danach kannst du:** Messwerte von LaptopAndi **und** dem Dell in einem gemeinsamen Datenpool sammeln — auch wenn ein Gerät zeitweise im jeweils anderen WLAN-Kreis unterwegs war (Puffer + Nachlieferung).
**Inhalt:** Zentrale Empfangsstelle auf LaptopAndi, Probe auf dem Dell, Offline-Warteschlange.
**Fertig, wenn:** beide Geräte liefern, der Nachliefer-Mechanismus im Test doppelfrei arbeitet und der Datenaustausch-Vertrag (Probe ↔ Zentrale) eingefroren ist.
*Agent-Notiz: 2–3 Tranchen · nacht-tauglich: ja · Checkpoint: keiner.*

### M3 — Dashboard v1 ⬜
**Danach kannst du:** dein Netz im Browser sehen — Zeitreihen je Gerät und Netz (Signal, Verbindungsrate, Ping), von jedem Endgerät im Haus aufrufbar, auch vom Handy. Dazu die **Projekt-Seite**: Version, welche Funktionen live sind, woran gerade gebaut wird.
**Inhalt:** Selbst gebautes Dashboard, hoher Anspruch an Usability/Design (dein Wunsch F11).
**Fertig, wenn:** die maschinellen UX-Prüfungen grün sind **und du** beim Geschmacks-Checkpoint „passt" sagst.
*Agent-Notiz: 3–4 Tranchen · nacht-tauglich: teilweise · **Checkpoint: Geschmack (Andreas).***

### M4 — Durchsatz & Call-Tauglichkeit ⬜
**Danach kannst du:** sehen, was zwischen den Geräten und ins Internet wirklich durchgeht (beide Kreise, budgetiert gegen dein 160-GB-Volumen) — und eine **Videocall-Ampel**: sind Jitter, Paketverlust und Upload gerade gut genug für Teams/Meet? Auch rückblickend („wie war es gestern 10–11 Uhr?").
**Inhalt:** Durchsatzmessung im Haus (kostet kein Mobilfunkvolumen), dosierte Internet-Speedtests mit Budget-Wächter, Call-Qualitäts-Kennzahlen.
**Fertig, wenn:** der Budget-Wächter im Test bei Erreichen des Limits zuverlässig stoppt und die Ampel gegen definierte Schwellwerte prüfbar ist.
*Agent-Notiz: 3 Tranchen · nacht-tauglich: ja · Checkpoint: Budget-Höhe bestätigen (Geld-Nähe).*

### M5 — Router-Innensicht Kreis A ⬜
**Danach kannst du:** ohne FRITZ!Box-Oberfläche sehen: DSL-Gesundheit über Zeit, welches Gerät an welchem AP/Band hängt, das Ereignisprotokoll der Box — plus **Geräte-Detektiv**: unbekannte Geräte wie „linux" und die anonyme MAC im Work-Kreis werden eingesammelt und zuordenbar.
**Inhalt:** FRITZ-Collector für die 7590 (geerntete, bewährte Bausteine), Geräte-Registry.
**Fertig, wenn:** die Adapter-Verträge gegen aufgezeichnete Testdaten grün sind und Live-Daten der echten Box eintreffen.
*Agent-Notiz: 2–3 Tranchen · nacht-tauglich: ja · Checkpoint: TR-064-Zugang verifizieren (einmalig, Mensch).*

### M6 — Störungs- & Roaming-Detektiv ⬜
**Danach kannst du:** bei „gerade hat es gehakt" nachschauen, was los war: AP-Wechsel, Abbrüche und Schwellwert-Verletzungen werden als Ereignisse markiert und mit den Zeitreihen verknüpft. Dazu automatische **Vergleichsrunden**: die Probe wechselt (dokumentiert, mit Standort-Angabe) zwischen ULVT18 und work_mobile_office und misst beide nacheinander.
**Inhalt:** Ereignis-Erkennung, „Was war um …?"-Sicht, gesteuerte Netzwechsel-Messrunden (deine Freigabe F9).
**Fertig, wenn:** eine synthetische Störungs-Sequenz im Test korrekt als Ereigniskette erkannt wird.
*Agent-Notiz: 3 Tranchen · nacht-tauglich: ja (Vergleichsrunden ideal nachts) · Checkpoint: keiner.*

### M7 — Work-Kreis-Innensicht ⬜
**Danach kannst du:** den Netgear M3 durchleuchten: 5G-Signalqualität über Zeit, Datenverbrauch live gegen dein 160-GB-Budget, angemeldete Geräte — und dieselbe Innensicht für die 6850.
**Inhalt:** Netgear-Collector (beginnt bewusst mit einer Erkundung der Geräte-Schnittstelle, streng nur-lesend), 6850-Collector.
**Fertig, wenn:** Erkundungsnotiz vorliegt und die Collector-Verträge gegen aufgezeichnete Testdaten grün sind.
*Agent-Notiz: 3 Tranchen (inkl. Spike) · nacht-tauglich: nach Spike · Checkpoint: keiner.*

### M8 — Umfeld & Kanäle ⬜
**Danach kannst du:** sehen, welche Nachbar-Netze es gibt, wie stark sie sind und ob sie sich mit euren Kanälen beißen — die Grundlage für spätere Kanal-Empfehlungen.
**Inhalt:** Umgebungs-Scan von jedem Messgerät, Kanalbelegungs-Auswertung.
**Fertig, wenn:** die Scan-Auswertung (deutsch/englisch robust) ihre Tests besteht.
*Agent-Notiz: 2 Tranchen · nacht-tauglich: ja · Checkpoint: keiner.*

### M9 — Hauskarte ⬜
**Danach kannst du:** deinen Bauplan im Dashboard sehen, Messungen einem Raum zuordnen („ich messe gerade im Büro Karen") und eine **Signal-Heatmap je Netz und Etage** aufbauen — inklusive der Frage, wie gut das 1. OG wirklich versorgt ist (dort steht kein Kreis-A-AP).
**Inhalt:** Bauplan hinterlegt (EG, 1. OG, Dachboden), Raumliste, Standort-Tagging, Heatmap.
**Fertig, wenn:** Messrunden mit Raum-Tag in der Karte erscheinen und die Heatmap gegen Beispieldaten getestet ist.
*Agent-Notiz: 3–4 Tranchen · nacht-tauglich: teilweise · **Checkpoint: Karten-Darstellung (Geschmack).***

### M10 — Empfehlungen mit Beweis ⬜
**Danach kannst du:** konkrete, begründete Vorschläge bekommen („6850-Backhaul auf 5 GHz umstellen", „Kanalwechsel", „SSID-Aufräumen auf Gerät X") — **du** setzt um (die Router bleiben für das System tabu), und FunkAtlas misst Vorher/Nachher und sagt dir mit Zahlen, ob es etwas gebracht hat.
**Inhalt:** Empfehlungs-Modul + Experiment-Schleife (Basislinie → Änderungs-Marker → Nachher-Messung → Urteil). Dein Zusatz aus F8 ist hier Gesetz: jede Empfehlung wird am Messergebnis verifiziert.
**Fertig, wenn:** ein komplettes Experiment (mit echter Änderung deiner Wahl) den Vorher/Nachher-Report erzeugt.
*Agent-Notiz: 3 Tranchen · nacht-tauglich: Auswertung ja, Umsetzung Mensch · **Checkpoint: jede Umsetzung (Andreas).***

### M11 — Handy misst mit ⬜
**Danach kannst du:** mit dem Android-Handy an jedem Punkt im Haus messen — dieselben Daten, derselbe Datenpool, ideal für die Hauskarte.
**Inhalt:** Android-Probe gegen den eingefrorenen Datenaustausch-Vertrag aus M2.
**Fertig, wenn:** das Handy Messrunden liefert, ohne dass der Vertrag angefasst werden musste (Frozen-Zone-Beweis).
*Agent-Notiz: eigenes Mini-Projekt (Kotlin) · Checkpoint: Go vor Start.*

---

## Was bewusst NICHT auf der Roadmap steht

Automatische Router-Umkonfiguration (das System bleibt reiner Sensor; ändern tust du) · iOS-Messungen (Apple sperrt die nötigen Schnittstellen) · Cloud-Anbindung (alles bleibt im Haus).

## Änderungslog

- **2026-07-13:** v1 der Roadmap aus Grobkonzept v0.2 + Interview-Runde 1 (F1–F15). Reihenfolge nach Prioritäten F6 (Durchsatz, Videocalls zuerst).
