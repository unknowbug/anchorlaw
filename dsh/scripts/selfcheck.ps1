# selfcheck.ps1 — Maintenance self-check for the Anchorlaw DSH project.
#
# Mirrors the Anchorlaw self-reference iron rule: the project must be able to
# verify itself. Checks:
#   1. python + anchorlaw-scanner + anchorlaw availability
#   2. skill manifest validity (DSH naming/frontmatter) via tests/test_manifest.py
#   3. scanner self-scan of the project's own python sources (ERR must be 0)
#   4. installed preset + skills presence under ~/.dsh

$ErrorActionPreference = 'Continue'

$srcRoot = Split-Path -Parent $PSScriptRoot
$fail = 0

Write-Host "== Anchorlaw DSH self-check =="

# 1. toolchain
Write-Host ""
Write-Host "[1] toolchain"
python -c "import anchorlaw_scanner, anchorlaw; print('  OK anchorlaw-scanner + anchorlaw importable')" 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: anchorlaw packages not importable"; $fail = 1 }

# 2. skill manifest
Write-Host ""
Write-Host "[2] skill manifests"
python (Join-Path $srcRoot 'tests\test_manifest.py') 2>&1
if ($LASTEXITCODE -ne 0) { $fail = 1 }

# 3. scanner self-scan (own python sources: tests/ + scripts tooling)
Write-Host ""
Write-Host "[3] scanner self-scan"
python -m anchorlaw_scanner check (Join-Path $srcRoot 'tests') 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: ERR-level patterns in own sources"; $fail = 1 }

# 4. installed artifacts
Write-Host ""
Write-Host "[4] installed artifacts"
$dshHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\anchorlaw'
if (Test-Path (Join-Path $presetDir 'agent.cordis.yml')) {
  Write-Host "  OK preset: $presetDir"
} else {
  Write-Host "  FAIL: preset not installed — run scripts/install.ps1"; $fail = 1
}
$userSkills = Join-Path $dshHome 'skills'
$count = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'anchor-*' }).Count
Write-Host "  OK user skills: $count anchor-* directories"
if ($count -lt 11) { Write-Host "  FAIL: expected 11 anchor skills"; $fail = 1 }

Write-Host ""
if ($fail -eq 0) { Write-Host "== ALL CHECKS PASSED ==" } else { Write-Host "== CHECKS FAILED ==" }
exit $fail
