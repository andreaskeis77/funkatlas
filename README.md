# FunkAtlas

Private Multi-Netz-WLAN-Analyseplattform für das Haus Keis. Nachfolger des
Legacy-Projekts `wlan` (Harvest, kein Fork).

- Orientierung: [docs/ROADMAP.md](docs/ROADMAP.md) (Meilensteine in Feature-Sprache)
- Fachliche Referenz: [docs/GROBKONZEPT.md](docs/GROBKONZEPT.md)
- Arbeitsregeln: [CLAUDE.md](CLAUDE.md) · Methodik: [docs/INDEX.md](docs/INDEX.md)

## Einstieg

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\tools\install_git_hooks.ps1

.\funkatlas.cmd gate   # das Merge-Gate (compile, ruff-kritisch, pytest offline, secret-scan)
.\funkatlas.cmd test   # volle Offline-Testsuite
```

Eiserne Regeln: Router strikt read-only (nur `Get*`) · Gate hermetisch (kein
echter Netz-Call, `network`-Tests opt-in) · keine Secrets/PII im Repo ·
`config/devices.yaml` bleibt lokal.
