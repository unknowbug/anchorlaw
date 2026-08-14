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
#   deepseek-ai/deepseek-harness discussion #306).
#   Host-level install additionally mounts the 4 anchorlaw_* tools globally:
#   it appends an `insert` row to <dshHome>/profiles/<profile>/cordis.patch.yml
#   (the ONLY user patch layer DSH reads; ~/.dsh/cordis.patch.yml is ignored by
#   the host) and copies the plugin to <profile>/plugins/anchorlaw/.
#
# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

param(
  # Project directory for project-level (Reasonix-style) install.
  [string]$Project = '',
  # DSH profile name for the global tool mount. Empty = auto-detect every
  # profile directory under <dshHome>/profiles holding a package.json (never a
  # hard-coded default).
  [string]$Profile = ''
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

# 4. Global tool mount — DSH reads ONLY a profile's own patch layer
#    (<dshHome>/profiles/<profile>/cordis.patch.yml; baseUrl = profile dir,
#    hot-reloaded). ~/.dsh/cordis.patch.yml is NOT read by the host. The
#    anchorlaw plugin row is appended as an `insert` patch so the four
#    anchorlaw_* tools are available in every session (global layer).
#
#    Profiles: -Profile <name> mounts one profile explicitly; otherwise EVERY
#    profile directory under <dshHome>/profiles holding a package.json is
#    mounted, so whichever profile the host runs, the tools are there. No
#    profile found skips the mount with a hint — there is NO hard-coded
#    default profile name.
#
#    GATE: never mount a plugin whose tool schemas are not compiled JSON
#    Schema. A flat per-property spec (defineTool input style) is projected
#    verbatim to the LLM without a top-level type and breaks EVERY session
#    ("Invalid schema for function ... got 'type: null'"). The check must pass
#    before any patch is written (2026-08-13 incident guard).
$mountProfiles = @()
if ($Profile) {
  $mountProfiles = @($Profile)
} else {
  $profilesDir = Join-Path $dshHome 'profiles'
  if (Test-Path $profilesDir) {
    $mountProfiles = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
      $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json'))
    } | ForEach-Object { $_.Name })
  }
}

if ($mountProfiles.Count -eq 0) {
  Write-Host "  skip global tools: no DSH profile found under $(Join-Path $dshHome 'profiles')"
  Write-Host "        (create one with 'dsh plugin --profile <name> add <package>', then re-run install.ps1)"
} else {
  node (Join-Path $srcRoot 'tests\check_plugin_schema.mjs') 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "plugin tool-schema check failed - refusing to mount global tools"
  }
  foreach ($profileName in $mountProfiles) {
    $profileDir = Join-Path $dshHome "profiles\$profileName"
    $patchPath = Join-Path $profileDir 'cordis.patch.yml'
    $profilePluginDir = Join-Path $profileDir 'plugins\anchorlaw'

    # Plugin file travels with the profile (resolved relative to baseUrl = profile dir)
    New-Item -ItemType Directory -Path $profilePluginDir -Force | Out-Null
    Copy-Item -Path (Join-Path $srcRoot 'plugins\anchorlaw-tools.js') -Destination (Join-Path $profilePluginDir 'anchorlaw-tools.js') -Force

    # Idempotent YAML merge: drop any prior anchorlaw-tools-global insert row, then append ours.
    $py = @'
import io, os, yaml
path = os.environ['ANCHORLAW_PATCH_PATH']
try:
    with io.open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
except FileNotFoundError:
    data = None
rows = list(data) if isinstance(data, list) else []
rows = [r for r in rows if not (
    isinstance(r, dict) and any(
        (e or {}).get('id') == 'anchorlaw-tools-global' for e in (r.get('insert') or [])))]
rows.append({'insert': [{'id': 'anchorlaw-tools-global',
                         'name': './plugins/anchorlaw/anchorlaw-tools.js',
                         'config': {}}]})
out = ('# Managed by install.ps1 - global anchorlaw tools for this profile '
       '(anchorlaw-tools-global). Re-run install.ps1 to refresh; do not hand-edit.\n' +
       yaml.safe_dump(rows, allow_unicode=True, sort_keys=False))
with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
'@
    $tmpPy = Join-Path $env:TEMP 'anchorlaw-patch-merge.py'
    Set-Content -Path $tmpPy -Value $py -Encoding UTF8
    $env:ANCHORLAW_PATCH_PATH = $patchPath
    python $tmpPy
    $mergeCode = $LASTEXITCODE
    Remove-Item $tmpPy -Force -ErrorAction SilentlyContinue
    Remove-Item Env:ANCHORLAW_PATCH_PATH -ErrorAction SilentlyContinue
    if ($mergeCode -ne 0) { throw "failed to merge profile patch $patchPath" }
    Write-Host "  OK global tools: $patchPath (anchorlaw-tools-global)"
  }
}

Write-Host ""
Write-Host "Installed:"
Get-ChildItem -Path $presetDir -Recurse -File | ForEach-Object { Write-Host "  $($_.FullName.Replace($presetDir, 'preset'))" }
if ($mountProfiles.Count -gt 0) {
  foreach ($profileName in $mountProfiles) {
    Write-Host "  global: $(Join-Path $dshHome "profiles\$profileName\cordis.patch.yml") (anchorlaw-tools-global)"
  }
}
Write-Host ""
Write-Host "Next: run scripts/selfcheck.ps1 to verify; open a NEW session (or wait for profile hot-reload)"
Write-Host "      and the 4 anchorlaw_* tools are available in every session."
