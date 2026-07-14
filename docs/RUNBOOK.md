# RUNBOOK — FunkAtlas (LaptopAndi, Probe v0)

## Starten & Stoppen

| Was | Befehl |
|---|---|
| Eine Messrunde (Smoke) | `funkatlas.cmd probe-once` |
| Dauerbetrieb im Terminal | `funkatlas.cmd probe` (Stopp: Strg+C) |
| Autostart installieren | `.\ops\autostart_install.ps1` (Task `funkatlas-probe`, startet bei Anmeldung, Neustart bei Absturz 3×) |
| Autostart entfernen | `.\ops\autostart_install.ps1 -Remove` |
| Sofort starten (Task) | `Start-ScheduledTask -TaskName funkatlas-probe` |
| Nachtlauf-Check morgens | `funkatlas.cmd heartbeat` → zeigt Anzahl, letzten Heartbeat und größte Lücke der letzten 24 h |

**Regel: genau EIN Probe-Prozess je Gerät** (ein DB-Writer). `probe` nicht parallel
zu einem laufenden `funkatlas-probe`-Task starten.

## Wo liegen die Daten

- Datenbank: `data/funkatlas.sqlite3` (SQLite/WAL, gitignored)
- Log-Projektion: `logs/metrics/<device_id>/<domain>/<YYYY-MM-DD>.jsonl` (append-only, gitignored)
- Messrhythmus: `config/scheduler.yaml` (Default: alle 60 s) · Ziele: `config/probes.yaml`

## ☑ E9-Energieprofil-Checkliste (VOR dem ersten Nachtlauf abhaken)

Windows-Energieverwaltung ist das größte Risiko für Nachtmessungen — Schlaf stoppt alles.
Einmalig prüfen/setzen, Häkchen setzen:

- [ ] **1. Netzteil an** — Nachtmessung nur im Netzbetrieb.
- [ ] **2. Kein Standby am Netz:** Einstellungen → System → Netzbetrieb & Energiesparen →
      „Im Netzbetrieb Energiesparmodus nach": **Nie**. (Bildschirm aus ist ok.)
- [ ] **3. Zuklapp-Verhalten** (falls Deckel nachts zu ist): Systemsteuerung → Energieoptionen →
      „Auswählen, was beim Zuklappen passiert" → Netzbetrieb: **Nichts unternehmen**.
- [ ] **4. WLAN-Adapter-Energiesparen AUS:** Geräte-Manager → Netzwerkadapter →
      Intel Wireless-AC 9560 → Energieverwaltung → „Computer kann das Gerät ausschalten,
      um Energie zu sparen" **abhaken** — sonst drosselt/trennt der Adapter im Leerlauf
      und verfälscht die Ruhe-Referenz.
- [ ] **5. Windows-Update-Neustarts:** Nutzungszeit prüfen (Einstellungen → Windows Update →
      Nutzungszeit) bzw. Updates für die Messnacht pausieren.
- [ ] **6. Probe läuft:** `funkatlas.cmd probe-once` liefert eine Zeile Summary ohne Fehler;
      dann Dauerbetrieb starten (Task oder Terminal).
- [ ] **7. Morgens:** `funkatlas.cmd heartbeat` — größte Lücke ≲ 2–3 min ⇒ saubere Nacht;
      große Lücken ⇒ Punkt 2–5 nochmal prüfen.

## Störungssuche

- **`heartbeat` meldet „Probe lief nicht":** Task registriert? Angemeldet geblieben?
  (Der Task läuft nur bei angemeldetem Benutzer — Abmelden stoppt die Messung.)
- **Große Heartbeat-Lücken:** fast immer Energieverwaltung (Checkliste oben) oder
  Windows-Update-Neustart.
- **Roter Gate-Lauf:** `funkatlas.cmd gate` lokal fahren; Ursache fixen, Gate nie aufweichen.

## Dinge, die nicht wieder passieren sollen

- Zweiten Writer auf dieselbe SQLite starten (zwei `probe`-Prozesse) — WAL toleriert genau einen.
- Dateien für andere Tools mit PowerShell `>` schreiben (erzeugt UTF-16; Baseline/JSONL
  immer UTF-8 ohne BOM — Lektion aus dem Vorgängerprojekt).
- Router „nur kurz live testen" — echte Router-Calls sind ein bewusster M5-Schritt (E14).
