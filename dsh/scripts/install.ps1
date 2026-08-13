# install.ps1 — Install/sync the Anchorlaw DSH project into the DSH runtime.
#
# Two modes:
#   Host-level (default): installs the anchorlaw preset (composition + plugin +
#   embedded skills) to ~/.dsh/.agent-presets/anchorlaw/ and the 11 anchor-*
#   skills to ~/.dsh/skills/ (user-global — every session sees them).
#   Project-level (-Project <dir>): Reasonix-style per-project deployment —
#   installs the 11 anchor-* skills to <dir>/.dsh/skills/ (DSH native
#   project-scoped root, rank 100), so a session opened inside <dir> loads
#   them and a session outside does not. The plugin file is also copied to
#   <dir>/.dsh/plugins/ for future project-level plugin support; DSH currently
#   has no project-level plugin mechanism (suggestion filed upstream:
#   deepseek-ai/deepseek-harness discussion #306), so the anchorlaw_* tools
#   remain available through the anchorlaw preset (host-level).
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

param(
  # Project directory for project-level (Reasonix-style) install.
  [string]$Project = ''
)

$ErrorActionPreference = 'Stop'

$srcRoot  = Split-Path -Parent $PSScriptRoot
$dshHome  = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$presetDir = Join-Path $dshHome '.agent-presets\anchorlaw'
$userSkills = Join-Path $dshHome 'skills'

if ($Project) {
  # ── Project-level install (Reasonix-style per-project deployment) ──────────
  $proj = (Resolve-Path -Path $Project -ErrorAction Stop).ProviderPath
  $projSkills  = Join-Path $proj '.dsh\skills'
  $projPlugins = Join-Path $proj '.dsh\plugins'

  Write-Host "== Anchorlaw DSH project install =="
  Write-Host "project : $proj"
  Write-Host "skills  : $projSkills (project-scoped, rank 100 — visible only in this project's sessions)"

  if (-not (Test-Path (Join-Path $proj '.git'))) {
    Write-Host "  note: $proj has no .git — DSH falls back to the session cwd as project root;"
    Write-Host "        open sessions directly in this directory for the skills to resolve."
  }

  # Skills → project-scoped root (<project>/.dsh/skills/anchor-*)
  New-Item -ItemType Directory -Path $projSkills -Force | Out-Null
  Copy-Item -Path (Join-Path $srcRoot 'skills\*') -Destination $projSkills -Recurse -Force

  # Plugin file also lands in the project, ready for future project-level plugin
  # loading (not auto-loaded by DSH today).
  New-Item -ItemType Directory -Path $projPlugins -Force | Out-Null
  Copy-Item -Path (Join-Path $srcRoot 'plugins\anchorlaw-tools.js') -Destination $projPlugins -Force

  Write-Host ""
  Write-Host "Installed (project-scoped):"
  Get-ChildItem -Path $projSkills -Directory | ForEach-Object { Write-Host "  $($_.Name)" }
  Write-Host "  plugins\anchorlaw-tools.js"
  Write-Host ""
  Write-Host "Next: open a DSH session in this project directory — the 11 anchor-* skills load here"
  Write-Host "      and nowhere else. The anchorlaw_* TOOLS still come from the anchorlaw preset"
  Write-Host "      (DSH has no project-level plugin mechanism yet; upstream suggestion:"
  Write-Host "      deepseek-ai/deepseek-harness discussion #306)."
  exit 0
}

# ── Host-level install (default) ─────────────────────────────────────────────

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
