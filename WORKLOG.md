# WORKLOG — FunkAtlas (append-only)

## 2026-07-14 · Lauf 1 (M0) · T0.1 „Gerüst + Gate"

- **Gebaut:** `pyproject.toml` (D4-Dependency-Set OHNE fritzconnection, per Go) ·
  `src/funkatlas/` (\_\_init\_\_ Version-Single-Truth, settings mit FUNKATLAS_-Prefix
  und env>dotenv>Default, config mit VEREINHEITLICHTEM Key-Merge, schema mit
  ensure_schema/WAL/busy_timeout/now_utc_iso/device_id-Spalten, gate mit 4 Schritten,
  \_\_main\_\_ CLI) · tools/ (task_runner mit COMMANDS→USAGE-Generierung, precommit_check,
  hooks/pre-commit, install_git_hooks.ps1) · funkatlas.cmd/.ps1 · .gitattributes ·
  .vscode/tasks.json · .github/workflows/ci.yml · .env.example · README ·
  tests (conftest mit Kill-Switch vor Import + tmp_db; unit: version/settings/config/
  gate_secrets/task_runner_usage; consistency: schema) · frische .secrets.baseline.
- **D5-Fixes in dieser Tranche (mit Regressionstest):** Config-Merge vereinheitlicht
  (Test `test_partial_yaml_keeps_unlisted_defaults` pinnt das Legacy-Silent-Drop-Verhalten
  als behoben) · `new_secrets` POSIX-pfadnormalisiert (Test
  `test_windows_and_posix_paths_are_equivalent`) · USAGE-Drift konstruktiv unmöglich
  (USAGE aus COMMANDS generiert + Test).
- **Red gesehen:** `test_malformed_yaml_yields_defaults` schlug zunächst fehl, weil der
  „kaputte" YAML-String gültiges YAML war (`{':': 'not yaml ::['}`) — Test auf echt
  malformiertes YAML korrigiert. Beweis, dass der Test etwas einschränkt.
- **Tests:** 18 passed (offline). **Gate:** GESAMT: PASS (compile · ruff-kritisch ·
  pytest · secret-scan). Hooks installiert (core.hooksPath → tools/hooks).
- **Entscheidungen/Parks:** Baseline-Falsch-Positiv (Plan-Doku Zeile 69) akzeptiert
  und in PROJECT_STATE dokumentiert. Keine Parks.
