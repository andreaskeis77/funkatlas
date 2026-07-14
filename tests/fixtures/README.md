# Fixtures — Provenienz & Sanitisierung

Regel (E11): Fixtures im Repo sind **pseudonymisiert** — SSID/Profil →
`REDACTED_SSID`, BSSIDs/MACs → `aa:bb:cc:00:00:NN`, GUIDs → Nullen. Messwerte
(Signal, Kanal, Raten) bleiben real.

| Datei | Quelle | Encoding |
|---|---|---|
| `netsh_interfaces_de_connected.bin` | echte Aufnahme LaptopAndi, Win11 DE (2026-07-14), sanitisiert | UTF-8 (so von diesem Build geliefert) |
| `netsh_interfaces_de_connected_cp850.bin` | dieselbe Ausgabe, CP850-kodiert (ältere Builds) | CP850 |
| `netsh_interfaces_de_disconnected.bin` | konstruiert nach realem Win11-DE-Layout | UTF-8 |
| `netsh_interfaces_en_connected.bin` | synthetisch nach dokumentiertem Win11-EN-Layout | UTF-8 |
