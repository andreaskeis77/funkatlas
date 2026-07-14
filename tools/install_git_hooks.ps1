# Point git at the versioned hooks directory (hooks live in the repo, not .git/hooks).
$ErrorActionPreference = 'Stop'
git config core.hooksPath tools/hooks
Write-Host "core.hooksPath -> tools/hooks (pre-commit active)"
