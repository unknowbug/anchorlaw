"""Anchor Skill Manifest conformance tests (protocol v0.6 §14/§15).

Verifies the Reasonix reference implementation (`.reasonix/skills/`) against
the protocol's Skill Manifest (§14.6), applying the First Law reflexively:

1. manifest skill set == implementation file set (action skills only;
   execution roles are §15 reference, not manifest entries; v0.8: only
   the review gate judge is sanctioned)
2. frontmatter valid (name present, matches directory name, description present)
3. index description line within 120-char budget
4. Protocol reference line present (single source of truth, §14.1)
5. CLI binding contract (§14.4): no `import anchorlaw` guidance except the
   sole sanctioned in-code hook (create_noise_card in anchor.noise)
6. layer dependency direction (§14.2): no upward references, except L0
   `anchor.concepts` (semantic index MAY point onward to any layer)
7. execution mode (§14.1 v0.6): body `> Execution:` matches manifest column
8. execution roles: judge / scout / worker are sanctioned (v0.10)
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = REPO_ROOT / "spec" / "protocol-v0.13.md"
SKILLS_DIR = REPO_ROOT / ".reasonix" / "skills"

# §14.6 catalog rows: | `anchor.concepts` | L0 | inline | ...
_MANIFEST_RE = re.compile(r"^\| `(anchor\.[a-z]+)` \| (L\d) \| (inline|subprocess) \|", re.MULTILINE)
_NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)
_DESC_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)
_PROTOCOL_REF_RE = re.compile(r"^\s*>\s*Protocol:", re.MULTILINE)
_ANCHOR_REF_RE = re.compile(r"`(anchor\.[a-z]+)`")
_EXEC_RE = re.compile(r"^\s*>\s*Execution:\s*(inline|subprocess)\b", re.MULTILINE)

LAYER_RANK = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}


def _manifest() -> dict[str, str]:
    """Parse §14.6 skill catalog from the protocol into {name: layer}."""
    text = PROTOCOL.read_text(encoding="utf-8")
    section = text[text.index("### 14.6"):]
    manifest = {}
    for name, layer, _exec in _MANIFEST_RE.findall(section):
        assert name not in manifest, f"duplicate skill in manifest: {name}"
        manifest[name] = layer
    return manifest


def _manifest_execution() -> dict[str, str]:
    """Parse §14.6 execution-mode column into {name: inline|subprocess}."""
    text = PROTOCOL.read_text(encoding="utf-8")
    section = text[text.index("### 14.6"):]
    return {name: exec_mode for name, _layer, exec_mode in _MANIFEST_RE.findall(section)}


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "missing frontmatter opener"
    fm: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    raise AssertionError("frontmatter never closed")


def _implementations() -> dict[str, Path]:
    """Scan action skills (non-role) -> {name: path}."""
    if not SKILLS_DIR.is_dir():
        return {}
    impl = {}
    for d in sorted(SKILLS_DIR.iterdir()):
        f = d / "SKILL.md"
        if not (d.is_dir() and f.is_file()):
            continue
        fm = _frontmatter(f.read_text(encoding="utf-8"))
        if fm.get("kind") != "role":
            impl[d.name] = f
    return impl


def _roles() -> dict[str, Path]:
    """Scan execution-role profiles (kind: role) -> {name: path}."""
    if not SKILLS_DIR.is_dir():
        return {}
    roles = {}
    for d in sorted(SKILLS_DIR.iterdir()):
        f = d / "SKILL.md"
        if not (d.is_dir() and f.is_file()):
            continue
        fm = _frontmatter(f.read_text(encoding="utf-8"))
        if fm.get("kind") == "role":
            roles[d.name] = f
    return roles


def test_manifest_matches_implementations():
    manifest = _manifest()
    impl = _implementations()
    assert manifest, "protocol §14.6 manifest is empty — parse failed?"
    assert set(manifest) == set(impl), (
        "manifest/implementation mismatch\n"
        f"  manifest-only: {sorted(set(manifest) - set(impl))}\n"
        f"  impl-only:     {sorted(set(impl) - set(manifest))}"
    )


def test_frontmatter_valid():
    for name, path in _implementations().items():
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        assert fm.get("name") == name, f"{name}: frontmatter name != dir name"
        assert fm.get("description"), f"{name}: missing description"


def test_description_within_index_budget():
    for name, path in _implementations().items():
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        desc = fm["description"]
        assert len(desc) <= 120, (
            f"{name}: index description {len(desc)} chars > 120 budget"
        )


def test_protocol_reference_present():
    for name, path in _implementations().items():
        text = path.read_text(encoding="utf-8")
        assert _PROTOCOL_REF_RE.search(text), (
            f"{name}: missing '> Protocol:' single-source-of-truth reference"
        )


def test_cli_binding_contract():
    # §14.4: no library-import guidance (any import form), except the sole
    # sanctioned in-code hook: create_noise_card inside anchor.noise.
    import_re = re.compile(r"^\s*(?:import\s+anchorlaw\b|from\s+anchorlaw\b)", re.MULTILINE)
    for name, path in _implementations().items():
        text = path.read_text(encoding="utf-8")
        for m in import_re.finditer(text):
            assert name == "anchor.noise", (
                f"{name}: §14.4 violated — library import guidance "
                f"({m.group(0)!r}) only sanctioned for the create_noise_card "
                "hook in anchor.noise"
            )


def test_layer_matches_manifest():
    # SKILL.md body declares `> Layer: Lx`; guard against drift between the
    # protocol manifest and the reference implementation (both directions).
    layer_re = re.compile(r"^\s*>\s*Layer:\s*(L\d)\b", re.MULTILINE)
    manifest = _manifest()
    for name, path in _implementations().items():
        text = path.read_text(encoding="utf-8")
        m = layer_re.search(text)
        assert m, f"{name}: missing '> Layer:' declaration"
        assert m.group(1) == manifest[name], (
            f"{name}: body Layer {m.group(1)} != manifest Layer {manifest[name]}"
        )


def test_layer_dependency_direction():
    manifest = _manifest()
    for name, path in _implementations().items():
        if name == "anchor.concepts":
            continue  # L0 semantic index MAY point onward (§14.2 exception)
        text = path.read_text(encoding="utf-8")
        own_rank = LAYER_RANK[manifest[name]]
        for ref in _ANCHOR_REF_RE.findall(text):
            if ref == name or ref not in manifest:
                continue  # self-reference or forward-compatible name
            ref_rank = LAYER_RANK[manifest[ref]]
            assert ref_rank <= own_rank, (
                f"{name}: upward reference to {ref} "
                f"({manifest[name]} -> {manifest[ref]})"
            )


def test_execution_mode_matches_manifest():
    # §14.1 v0.6: body `> Execution:` line must match the manifest column.
    exec_modes = _manifest_execution()
    for name, path in _implementations().items():
        text = path.read_text(encoding="utf-8")
        m = _EXEC_RE.search(text)
        assert m, f"{name}: missing '> Execution:' declaration"
        assert m.group(1) == exec_modes[name], (
            f"{name}: body Execution {m.group(1)} != manifest {exec_modes[name]}"
        )


def test_roles_present_and_outside_manifest():
    # §15 execution roles are reference-implementation profiles, NOT §14.6
    # manifest action skills. v0.10: judge / scout / worker are sanctioned
    # (Judge-driven pipeline); v0.8's "only judge" is superseded.
    manifest = _manifest()
    roles = _roles()
    assert set(roles) == {"anchor.judge", "anchor.scout", "anchor.worker"}, (
        f"execution role profiles: {sorted(roles)} (v0.10 sanctions the three)"
    )
    for name, path in roles.items():
        assert name not in manifest, (
            f"{name}: execution role must not be a §14.6 manifest skill"
        )
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        assert fm.get("runAs") == "subagent", f"{name}: role must declare runAs: subagent"
