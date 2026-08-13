# install.ps1 — Install/sync the Anchorlaw DSH project into the DSH runtime.
#
# Source of truth: E:\PYTHON\Anchorlaw\dsh
#   preset/agent.cordis.yml + preset/preset.yml   → ~/.dsh/.agent-presets/anchorlaw/
#   plugins/anchorlaw-tools.js                    → ~/.dsh/.agent-presets/anchorlaw/plugins/
#   skills/*                            → ~/.dsh/.agent-presets/anchorlaw/skills/  (preset-embedded)
#                                                 → ~/.dsh/skills/                           (user-global)
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

$ErrorActionPreference = 'Stop'

$srcRoot  = Split-Path -Parent $PSScriptRoot
$dshHome  = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\anchorlaw'
$userSkills = Join-Path $dshHome 'skills'

Write-Host "== Anchorlaw DSH install =="
Write-Host "source : $srcRoot"
Write-Host "preset : $presetDir"
Write-Host "skills : $userSkills"

# 1. Preset composition + metadata
New-Item -ItemType Directory -Path $presetDir -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'preset\agent.cordis.yml') -Destination $presetDir -Force
Copy-Item -Path (Join-Path $srcRoot 'preset\preset.yml')       -Destination $presetDir -Force

# 2. Local plugin file (travels with the preset)
New-Item -ItemType Directory -Path (Join-Path $presetDir 'plugins') -Force | Out-Null
Copy-Item -Path (Join-Path $srcRoot 'plugins\anchorlaw-tools.js') -Destination (Join-Path $presetDir 'plugins') -Force

# 3. Skills: preset-embedded + user-global refresh
if (Test-Path (Join-Path $srcRoot 'skills')) {
  $presetSkills = Join-Path $presetDir 'skills'
  Remove-Item -Path $presetSkills -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -Path (Join-Path $srcRoot 'skills') -Destination $presetSkills -Recurse -Force
  Copy-Item -Path (Join-Path $srcRoot 'skills\*') -Destination $userSkills -Recurse -Force
}

Write-Host ""
Write-Host "Installed:"
Get-ChildItem -Path $presetDir -Recurse -File | ForEach-Object { Write-Host "  $($_.FullName.Replace($presetDir, 'preset'))" }
Write-Host ""
Write-Host "Next: open a new session on the 'anchorlaw' preset, or run scripts/selfcheck.ps1 to verify."
