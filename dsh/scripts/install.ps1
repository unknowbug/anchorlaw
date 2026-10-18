# install.ps1 — Install/sync the Anchorlaw DSH bundle into the DSH runtime.
#
# DSH >= 0.1.7: an agent preset is a `@deepseek-ai/dsh-agent-preset` declaration
# row carried by a BUNDLE PATCH. The legacy directory form
# (`$DSH_HOME/.agent-presets/<id>/`) is read by nothing — see
# packages/preset/agent-preset/skills/editing-cordis-compositions/SKILL.md.
#
# This script therefore:
#   1. verifies the bundle package in this directory (package.json + its patch)
#   2. installs the bundle into every target profile with
#      `dsh plugin --profile <p> add <bundle dir>` — pnpm installs it and the
#      plugin manager appends it to the profile's ordered `dsh.profile.bundles`
#      (reconcile() in @deepseek-ai/dsh-plugin-manager)
#   3. copies the 11 anchor-* skills to the user-global root `~/.dsh/skills`
#      (rank 400 — visible in every session of every project)
#   4. mounts the 4 anchorlaw_* tools globally (a profile patch row), so every
#      session — not only anchorlaw-preset sessions — sees them. The tools
#      registry is layered: a preset row and this global row do not collide.
#
# There is NO project-level mode. DSH has no project-level plugin/preset
# mechanism, so a project-scoped install could deliver the skills but never the
# preset persona or the 4 tools. Project-scoped skills remain available through
# DSH's own native root `<projectRoot>/.dsh/skills` (rank 100) — that needs no
# installer: any preset whose `skill-filesystem` keeps `includeDefaultRoots`
# (the default) discovers it.
#
# Two user patch layers exist and the home-level one outranks the per-profile one;
# this installer writes only the per-profile layer (see the 2026-09-18 note in
# step 3c below).

# Idempotent: safe to re-run after editing any source file. Requires full file
# access to the DSH home (outside the session workspace).

param(
  # DSH profile name for the bundle + global tool mount. Empty = auto-detect
  # every profile directory under <dshHome>/profiles holding a package.json
  # (never a hard-coded default).
  [string]$Profile = ''
)

$ErrorActionPreference = 'Stop'

$bundleDir  = Split-Path -Parent $PSScriptRoot          # this dsh/ subtree IS the bundle package
$dshHome    = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $HOME '.dsh' }
$userSkills = Join-Path $dshHome 'skills'

Write-Host "== Anchorlaw DSH bundle install =="
Write-Host "bundle : $bundleDir"
Write-Host "dshHome: $dshHome"

# ── 1. Verify the bundle package (fail-closed before touching anything) ──────
$manifestPath = Join-Path $bundleDir 'package.json'
if (-not (Test-Path $manifestPath)) { throw "bundle manifest missing: $manifestPath" }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$bundleName = $manifest.name
$patchRel = $manifest.dsh.bundle.patch
if (-not $bundleName) { throw "$manifestPath declares no name" }
if (-not $patchRel) { throw "$manifestPath declares no dsh.bundle.patch" }
$patchPath = Join-Path $bundleDir $patchRel
if (-not (Test-Path $patchPath)) { throw "bundle patch missing: $patchPath" }
Write-Host "  OK bundle: $bundleName  patch: $patchRel"

# The row gate must pass before anything is installed: a bundle whose preset rows
# do not resolve would install fine and then fail at session creation.
node (Join-Path $bundleDir 'tests\audit_preset_rows.mjs') 2>&1
if ($LASTEXITCODE -ne 0) { throw "preset row gate failed - refusing to install" }

# ── 2. Skills → user-global root ─────────────────────────────────────────────
$srcSkills = Join-Path $bundleDir 'skills'
if (Test-Path $srcSkills) {
  New-Item -ItemType Directory -Path $userSkills -Force | Out-Null
  Copy-Item -Path (Join-Path $srcSkills '*') -Destination $userSkills -Recurse -Force
  $n = @(Get-ChildItem $userSkills -Directory | Where-Object { $_.Name -like 'anchor-*' }).Count
  Write-Host "  OK user skills: $userSkills ($n anchor-*)"
}

# ── 3. Target profiles ───────────────────────────────────────────────────────
$profilesDir = Join-Path $dshHome 'profiles'
$mountProfiles = @()
if ($Profile) {
  $mountProfiles = @($Profile)
} elseif (Test-Path $profilesDir) {
  $mountProfiles = @(Get-ChildItem -Path $profilesDir -Directory | Where-Object {
    $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json'))
  } | ForEach-Object { $_.Name })
}

if ($mountProfiles.Count -eq 0) {
  Write-Host "  skip: no DSH profile found under $profilesDir"
  Write-Host "        (create one with 'dsh plugin --profile <name> add <package>', then re-run)"
} else {
  $dshCmd = Get-Command dsh -ErrorAction SilentlyContinue
  if (-not $dshCmd) {
    throw "dsh not found on PATH - the bundle is installed through 'dsh plugin --profile <p> add <dir>'"
  }

  # The global tool mount needs a compiled-schema check FIRST: a flat
  # per-property spec reaches the LLM without a top-level type and breaks EVERY
  # session ("Invalid schema for function ... got 'type: null'"). 2026-08-13 guard.
  node (Join-Path $bundleDir 'tests\check_plugin_schema.mjs') 2>&1
  if ($LASTEXITCODE -ne 0) { throw "plugin tool-schema check failed - refusing to mount global tools" }

  foreach ($profileName in $mountProfiles) {
    Write-Host ""
    Write-Host "  -- profile: $profileName"

    # 3a. Bundle → profile (pnpm dependency + dsh.profile.bundles entry)
    dsh plugin --profile $profileName add $bundleDir
    if ($LASTEXITCODE -ne 0) { throw "failed to install the bundle into profile '$profileName'" }
    Write-Host "     OK bundle installed + selected in dsh.profile.bundles"

    # 3b. Global tool mount — the plugin file travels with the profile (resolved
    #     relative to baseUrl = profile dir). A sibling package.json is REQUIRED:
    #     DSH's plugin-package inventory runs nearestManifest on loose modules,
    #     and without it the walk hits the profile's own manifest (name, no
    #     version) and identityFromManifest throws. Generated here, never hand-
    #     maintained — the version tracks the PROTOCOL version (latest spec file).
    $profileDir = Join-Path $profilesDir $profileName
    $profilePluginDir = Join-Path $profileDir 'plugins\anchorlaw'
    New-Item -ItemType Directory -Path $profilePluginDir -Force | Out-Null
    Copy-Item -Path (Join-Path $bundleDir 'plugins\anchorlaw-tools.js') -Destination $profilePluginDir -Force

    $specDir = Join-Path (Split-Path $bundleDir -Parent) 'spec'
    $protoVersion = (Get-ChildItem $specDir -Filter 'protocol-v*.md' -ErrorAction SilentlyContinue | ForEach-Object {
      if ($_.Name -match '^protocol-v(\d+)\.(\d+)\.md$') { [pscustomobject]@{ Maj = [int]$Matches[1]; Min = [int]$Matches[2] } }
    } | Sort-Object Maj, Min -Descending | Select-Object -First 1 | ForEach-Object { "$($_.Maj).$($_.Min)" })
    if (-not $protoVersion) { $protoVersion = '0.0' }
    [ordered]@{
      name        = 'anchorlaw-tools'
      version     = $protoVersion
      private     = $true
      type        = 'module'   # without it Node warns MODULE_TYPELESS_PACKAGE_JSON on every boot
      description = 'Anchorlaw protocol model tools for DSH (scan/report/ai_context/status). Generated by dsh/scripts/install.ps1 to give the loose plugin module under <profile>/plugins/anchorlaw/ a complete package identity.'
    } | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $profilePluginDir 'package.json') -Encoding UTF8

    # 3c. Idempotent YAML merge: drop any prior anchorlaw-tools-global insert row,
    #     then append ours.
    #
    #     NOTE (2026-09-18 correction, carried from PR #2): DSH reads TWO user
    #     patch layers, not one. The per-profile file
    #     (<dshHome>/profiles/<profile>/cordis.patch.yml; baseUrl = profile dir)
    #     is applied first; the home-level <dshHome>/cordis.patch.yml is applied
    #     AFTER it and therefore OUTRANKS it (@deepseek-ai/dsh-app-boot README:
    #     "applied after every bundle layer (per-profile first, then the
    #     home-level file, which therefore outranks it)"; homePatchPath() in
    #     lib/profile-boot-*.js). This installer deliberately writes only the
    #     per-profile layer: the home-level file is shared with other frameworks
    #     and with machine-local settings, so it is not this script's to rewrite.
    #
    #     Caveat (pre-existing, not changed here): the merge below round-trips the
    #     file through yaml.safe_dump, so comments inside the patch file are not
    #     preserved.
    $profilePatchPath = Join-Path $profileDir 'cordis.patch.yml'
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
    $env:ANCHORLAW_PATCH_PATH = $profilePatchPath
    python $tmpPy
    $mergeCode = $LASTEXITCODE
    Remove-Item $tmpPy -Force -ErrorAction SilentlyContinue
    Remove-Item Env:ANCHORLAW_PATCH_PATH -ErrorAction SilentlyContinue
    if ($mergeCode -ne 0) { throw "failed to merge profile patch $profilePatchPath" }
    Write-Host "     OK global tools: $profilePatchPath (anchorlaw-tools-global)"
  }
}

Write-Host ""
Write-Host "Next: run scripts/selfcheck.ps1 to verify; open a NEW session (or wait for"
Write-Host "      profile hot-reload) and pick the 'Anchorlaw' agent preset."