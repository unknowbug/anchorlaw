# selfcheck.ps1 — Maintenance self-check for the Anchorlaw DSH project.
#
# Mirrors the Anchorlaw self-reference iron rule: the project must be able to
# verify itself. Checks:
#   1. python + anchorlaw-scanner + anchorlaw availability
#   2. skill manifest validity (DSH naming/frontmatter) via tests/test_manifest.py
#   3. scanner self-scan of the project's own python sources (ERR must be 0)
#   4. installed preset + skills presence under ~/.dsh
#   5. plugin tool-schema shape (compiled JSON-Schema parameters) via
#      tests/check_plugin_schema.mjs — a flat spec would reach the LLM without
#      a top-level type and break every session ("Invalid schema ... type: null").
#   6. preset row resolvability via tests/audit_preset_rows.mjs — every `name:` in
#      the composition must resolve against the harness package set; an upstream
#      rename/removal otherwise surfaces only when a session resume fails to mount
#      (2026-09-09 drift: dsh-workflow-worker-thread → dsh-workflow-ptc).
#   7. prompt variable resolvability via tests/audit_prompt_variables.mjs — every
#      `{{var}}` in the preset's persona template must be a variable the harness
#      still registers; persona templates interpolate STRICTLY at assembly, so an
#      upstream variable removal surfaces only when a session starts
#      (2026-10-10: DSH 0.2.x dropped `cwd` → `unknown prompt variable "{{cwd}}"`
#      in section "deployment:persona-prefix").

$ErrorActionPreference = 'Continue'

$srcRoot = Split-Path -Parent $PSScriptRoot
$fail = 0

# ── harness 运行时选择 ──────────────────────────────────────────────────────
# 第 6/7 项要读 harness 的包与源码。源码 checkout 用 node 即可；Desktop 把运行时
# 打进 resources\app.asar，**普通 Node 的 fs 读不到 asar**，必须用
# ELECTRON_RUN_AS_NODE=1 让 Electron 的可执行文件当 Node 跑同一个脚本。
$checkout = if ($env:DSH_CHECKOUT) { $env:DSH_CHECKOUT } else { 'D:\git\deepseek-harness' }
$installDir = $env:DSH_INSTALL_DIR
if (-not $installDir) {
  foreach ($candidate in @(
      (Join-Path $env:ProgramFiles 'DeepSeek Harness\resources'),
      (Join-Path $env:LOCALAPPDATA 'Programs\DeepSeek Harness\resources'))) {
    if ($candidate -and (Test-Path (Join-Path $candidate 'app.asar'))) { $installDir = $candidate; break }
  }
}
$harnessLayout = 'unknown'
$harnessExe = $null
if (Test-Path (Join-Path $checkout 'packages')) {
  $harnessLayout = 'checkout'
} elseif ($installDir) {
  $candidateExe = Join-Path (Split-Path $installDir -Parent) 'DeepSeek Harness.exe'
  if (Test-Path $candidateExe) { $harnessLayout = 'asar'; $harnessExe = $candidateExe }
}
Write-Host "harness layout: $harnessLayout$(if ($harnessExe) { " ($harnessExe)" })"

# 用当前布局跑一个 harness 门禁脚本（返回退出码）
function Invoke-HarnessGate([string]$scriptPath) {
  if ($harnessLayout -eq 'asar') {
    $previous = $env:ELECTRON_RUN_AS_NODE
    $env:ELECTRON_RUN_AS_NODE = '1'
    try { & $harnessExe $scriptPath 2>&1 | Out-Host; return $LASTEXITCODE }
    finally {
      if ($null -eq $previous) { Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue }
      else { $env:ELECTRON_RUN_AS_NODE = $previous }
    }
  }
  & node $scriptPath 2>&1 | Out-Host
  return $LASTEXITCODE
}

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
# DSH >= 0.1.7: the preset lives in a bundle selected by the profile's ordered
# `dsh.profile.bundles`. The legacy ~/.dsh/.agent-presets/<id>/ directory is read
# by NOTHING — 2026-09-23 incident: it was still populated and this check still
# passed while the preset was already unreachable.
$bundleName = (Get-Content (Join-Path $srcRoot 'package.json') -Raw | ConvertFrom-Json).name
$profilesDir = Join-Path $dshHome 'profiles'
$selected = @()
foreach ($pf in (Get-ChildItem -Path $profilesDir -Directory -ErrorAction SilentlyContinue |
                 Where-Object { $_.Name -ne 'node_modules' -and (Test-Path (Join-Path $_.FullName 'package.json')) })) {
  $m = Get-Content (Join-Path $pf.FullName 'package.json') -Raw | ConvertFrom-Json
  if ($m.dsh.profile.bundles -contains $bundleName) { $selected += $pf.Name }
}
if ($selected.Count -gt 0) {
  Write-Host "  OK bundle '$bundleName' selected in profile(s): $($selected -join ', ')"
} else {
  Write-Host "  FAIL: bundle '$bundleName' not selected in any profile — run scripts/install.ps1"; $fail = 1
}
$legacyDir = Join-Path $dshHome '.agent-presets\anchorlaw'
if (Test-Path $legacyDir) {
  Write-Host "  WARN: legacy preset dir still present (read by nothing, safe to delete): $legacyDir"
}
$userSkills = Join-Path $dshHome 'skills'
$count = @(Get-ChildItem -Path $userSkills -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'anchor-*' }).Count
Write-Host "  OK user skills: $count anchor-* directories"
if ($count -lt 11) { Write-Host "  FAIL: expected 11 anchor skills"; $fail = 1 }

# 5. plugin tool-schema shape (compiled JSON-Schema parameters; see check_plugin_schema.mjs)
Write-Host ""
Write-Host "[5] plugin tool schemas"
node (Join-Path $srcRoot 'tests\check_plugin_schema.mjs') 2>&1
if ($LASTEXITCODE -ne 0) { Write-Host "  FAIL: plugin tool schemas not compiled JSON Schema"; $fail = 1 }

# 6. preset row resolvability (fail-closed; see audit_preset_rows.mjs)
Write-Host ""
Write-Host "[6] preset row resolvability"
$presetAudit = Invoke-HarnessGate (Join-Path $srcRoot 'tests\audit_preset_rows.mjs')
if ($presetAudit -eq 2) {
  Write-Host "  WARN: preset audit skipped (harness unreadable — set DSH_CHECKOUT, or run under Electron for an asar install)"
} elseif ($presetAudit -ne 0) {
  Write-Host "  FAIL: unresolvable preset row(s) — upstream renamed/removed a plugin"; $fail = 1
}

# 7. prompt variable resolvability (fail-closed; see audit_prompt_variables.mjs)
Write-Host ""
Write-Host "[7] prompt variable resolvability"
$promptVarAudit = Invoke-HarnessGate (Join-Path $srcRoot 'tests\audit_prompt_variables.mjs')
if ($promptVarAudit -eq 2) {
  if ($env:DSH_SKIP_PROMPT_VAR_AUDIT -eq '1') {
    Write-Host "  WARN: prompt-variable audit skipped (DSH_SKIP_PROMPT_VAR_AUDIT=1 — gap explicitly accepted)"
  } else {
    Write-Host "  FAIL: prompt-variable audit could not run (set DSH_CHECKOUT, or run under Electron for an asar install, or DSH_SKIP_PROMPT_VAR_AUDIT=1 to accept the gap)"; $fail = 1
  }
} elseif ($promptVarAudit -ne 0) {
  Write-Host "  FAIL: unregistered prompt variable in the preset template — a session would fail to assemble"; $fail = 1
}

Write-Host ""
if ($fail -eq 0) { Write-Host "== ALL CHECKS PASSED ==" } else { Write-Host "== CHECKS FAILED ==" }
exit $fail
