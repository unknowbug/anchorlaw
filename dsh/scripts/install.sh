#!/usr/bin/env bash
# install.sh — Install/sync the Anchorlaw DSH project into the DSH runtime
# (Linux / macOS; bash twin of install.ps1 for hosts without PowerShell, e.g.
# a Kylin office desktop).
#
# Source of truth: <repo>/dsh
#   preset/agent.cordis.yml + preset/preset.yml  → $DSH_HOME/.agent-presets/anchorlaw/
#   plugins/anchorlaw-tools.js                   → $DSH_HOME/.agent-presets/anchorlaw/plugins/
#   skills/*                                     → $DSH_HOME/.agent-presets/anchorlaw/skills/
#                                                → $DSH_HOME/skills/          (user-global)
#
# Host-level install additionally mounts the 4 anchorlaw_* tools globally: it
# appends an `insert` row to <dshHome>/profiles/<profile>/cordis.patch.yml (the
# ONLY user patch layer DSH reads) and copies the plugin + its package.json to
# <profile>/plugins/anchorlaw/.
#
# GATE: never mount a plugin whose tool schemas are not compiled JSON Schema
# (a flat spec reaches the LLM without a top-level type and breaks EVERY
# session). The gate runs before any patch is written.
#
# Requires: node (schema gate), python3 + PyYAML (profile patch merge).
# Idempotent: safe to re-run after editing any source file.

set -euo pipefail

src_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$src_root/.." && pwd)"
dsh_home="${DSH_HOME:-$HOME/.dsh}"
preset_dir="$dsh_home/.agent-presets/anchorlaw"
user_skills="$dsh_home/skills"

echo "== Anchorlaw DSH install =="
echo "source : $src_root"
echo "preset : $preset_dir"
echo "skills : $user_skills"

# 0. Schema gate (see tests/check_plugin_schema.mjs for why this is mandatory).
if command -v node >/dev/null 2>&1; then
  if ! node "$src_root/tests/check_plugin_schema.mjs"; then
    echo "plugin tool-schema check failed - refusing to mount global tools" >&2
    exit 1
  fi
else
  echo "node not found: the plugin tool-schema gate cannot run." >&2
  echo "Install Node.js, then re-run." >&2
  exit 1
fi

# 1. Preset composition + metadata
mkdir -p "$preset_dir"
cp -f "$src_root/preset/agent.cordis.yml" "$preset_dir/"
cp -f "$src_root/preset/preset.yml"       "$preset_dir/"

# 2. Local plugin file (travels with the preset)
mkdir -p "$preset_dir/plugins"
cp -f "$src_root/plugins/anchorlaw-tools.js" "$preset_dir/plugins/"

# 3. Skills: preset-embedded + user-global refresh.
#    `cp -R src/. dst/` copies the CONTENTS (a bare `cp -R src dst` would nest
#    a second skills/ level when dst already exists).
if [ -d "$src_root/skills" ]; then
  rm -rf "$preset_dir/skills"
  cp -R "$src_root/skills" "$preset_dir/skills"
  mkdir -p "$user_skills"
  cp -R "$src_root/skills/." "$user_skills/"
fi

# 4. Global tool mount — DSH reads ONLY a profile's own patch layer
#    (<dshHome>/profiles/<profile>/cordis.patch.yml; baseUrl = profile dir).
#    Every profile holding a package.json is mounted, so whichever profile the
#    host runs, the tools are there. No hard-coded default profile name.
mount_profiles=()
if [ -d "$dsh_home/profiles" ]; then
  for p in "$dsh_home"/profiles/*/; do
    [ -f "${p}package.json" ] || continue
    mount_profiles+=("$(basename "$p")")
  done
fi

if [ ${#mount_profiles[@]} -eq 0 ]; then
  echo "  skip global tools: no DSH profile found under $dsh_home/profiles"
  echo "        (create one, then re-run install.sh)"
else
  python3 -c "import yaml" 2>/dev/null || {
    echo "PyYAML is required to merge the profile patch - run: pip3 install pyyaml" >&2
    exit 1
  }
  # The plugin package version tracks the PROTOCOL version (latest spec file) —
  # never a hand-picked number; bumps automatically with every protocol release.
  proto_version="$(ls "$repo_root"/spec/protocol-v*.md 2>/dev/null \
    | sed -n 's/.*protocol-v\([0-9][0-9]*\)\.\([0-9][0-9]*\)\.md$/\1 \2/p' \
    | sort -k1,1n -k2,2n | tail -1 | awk '{print $1"."$2}')"
  [ -n "$proto_version" ] || proto_version="0.0"

  for profile_name in "${mount_profiles[@]}"; do
    profile_dir="$dsh_home/profiles/$profile_name"
    patch_path="$profile_dir/cordis.patch.yml"
    plugin_dir="$profile_dir/plugins/anchorlaw"

    mkdir -p "$plugin_dir"
    cp -f "$src_root/plugins/anchorlaw-tools.js" "$plugin_dir/anchorlaw-tools.js"
    cp -f "$src_root/plugins/package.json"       "$plugin_dir/package.json"
    # A sibling package.json is REQUIRED: DSH's plugin-package inventory runs
    # nearestManifest on loose modules — without it the walk hits the profile's
    # own manifest (name but no version) and identityFromManifest throws.
    python3 - "$plugin_dir/package.json" "$proto_version" <<'PY'
import json, sys
path, version = sys.argv[1], sys.argv[2]
with open(path, encoding='utf-8') as f:
    data = json.load(f)
data['version'] = version
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
PY

    # Idempotent YAML merge: drop any prior anchorlaw-tools-global insert row,
    # then append ours.
    ANCHORLAW_PATCH_PATH="$patch_path" python3 - <<'PY'
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
out = ('# Managed by install.ps1 / install.sh - global anchorlaw tools for this '
       'profile (anchorlaw-tools-global). Re-run the installer to refresh; do '
       'not hand-edit.\n' + yaml.safe_dump(rows, allow_unicode=True, sort_keys=False))
with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
PY
    echo "  OK global tools: $patch_path (anchorlaw-tools-global)"
  done
fi

echo ""
echo "Installed:"
# cd + relative find: never interpolate the destination path into sed (a path
# containing backslashes would be parsed as back-references).
(cd "$preset_dir" && find . -type f | sed 's|^\./|  preset/|')
for profile_name in "${mount_profiles[@]:-}"; do
  [ -n "$profile_name" ] || continue
  echo "  global: $dsh_home/profiles/$profile_name/cordis.patch.yml (anchorlaw-tools-global)"
done
echo ""
echo "Next: run scripts/selfcheck.ps1 (PowerShell) or verify manually; open a NEW"
echo "      session and the 4 anchorlaw_* tools are available in every session."
