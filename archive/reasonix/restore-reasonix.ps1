# restore-reasonix.ps1 — Restore the archived Reasonix version to the repo root.
#
# For maintainers who FORK this repository and want to keep iterating on the
# Reasonix host format (Anchorlaw itself stopped maintaining it after v0.18;
# only the DSH host adaptation is maintained — see archive/reasonix/README.md).
#
# Run from the REPO ROOT. Restores:
#   archive/reasonix/skills/   -> .reasonix/skills/
#   archive/reasonix/AGENTS.md -> AGENTS.md
#   archive/reasonix/metadata/ -> .reasonix/metadata/
#
# Idempotent: existing targets are backed up as *.bak, never silently overwritten.

$ErrorActionPreference = 'Stop'

$src = Join-Path $PSScriptRoot 'reasonix'
if (-not (Test-Path $src)) {
  Write-Host "FAIL: archive dir not found: $src"
  exit 1
}

function Backup-Target([string]$path) {
  if (Test-Path $path) {
    $bak = "$path.bak"
    if (Test-Path $bak) { Remove-Item $bak -Recurse -Force }
    Move-Item $path $bak -Force
    Write-Host "  backed up existing -> $bak"
  }
}

Write-Host "== Restore Reasonix version =="

# 1. .reasonix/skills
$targetSkills = Join-Path (Get-Location) '.reasonix\skills'
if (Test-Path (Join-Path $src 'skills')) {
  Backup-Target $targetSkills
  New-Item -ItemType Directory -Path (Split-Path $targetSkills) -Force | Out-Null
  Copy-Item -Path (Join-Path $src 'skills') -Destination $targetSkills -Recurse -Force
  $count = @(Get-ChildItem $targetSkills -Directory -ErrorAction SilentlyContinue).Count
  Write-Host "  OK .reasonix/skills restored ($count skills)"
}

# 2. AGENTS.md
if (Test-Path (Join-Path $src 'AGENTS.md')) {
  Backup-Target (Join-Path (Get-Location) 'AGENTS.md')
  Copy-Item (Join-Path $src 'AGENTS.md') (Join-Path (Get-Location) 'AGENTS.md') -Force
  Write-Host "  OK AGENTS.md restored (Reasonix entry)"
}

# 3. .reasonix/metadata
$targetMeta = Join-Path (Get-Location) '.reasonix\metadata'
if (Test-Path (Join-Path $src 'metadata')) {
  Backup-Target $targetMeta
  New-Item -ItemType Directory -Path (Split-Path $targetMeta) -Force | Out-Null
  Copy-Item -Path (Join-Path $src 'metadata') -Destination $targetMeta -Recurse -Force
  Write-Host "  OK .reasonix/metadata restored"
}

Write-Host ""
Write-Host "Restore complete. The Reasonix working copy is at the repo root;"
Write-Host "iterate from here (this archive is no longer updated by upstream)."
