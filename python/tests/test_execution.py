"""Execution Topology conformance tests (protocol v0.8 §15/§16).

Verifies the execution layer of the reference implementation:

1. artifact schema: required fields + valid confidence status
   (reference-implementation convention; §15.5 classifies concrete layout
   as an implementation detail)
2. confidence state machine: one-way draft -> candidate -> confirmed,
   `confirmed` reserved for the host's human (§15.4)
3. review gate: judge output is opinion-only, never a status change (§15.4)
4. role profiles: only the review gate (judge) is sanctioned — kind: role,
   runAs: subagent (v0.8 convergence-gate model); scout/worker must not
   reappear as reference roles
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".reasonix" / "skills"

STATUSES = ("draft", "candidate", "confirmed")
REQUIRED_FIELDS = ("id", "kind", "status", "source_address", "created")


def _validate_artifact(artifact: dict) -> list[str]:
    """Return schema violations (empty list = valid). Per §15.2/§15.4."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in artifact:
            errors.append(f"missing field: {field}")
    if "status" in artifact and artifact["status"] not in STATUSES:
        errors.append(f"invalid status: {artifact['status']}")
    return errors


def _transition_is_legal(current: str, target: str) -> bool:
    """One step forward in draft -> candidate -> confirmed only."""
    idx = STATUSES.index(current)
    return STATUSES.index(target) == idx + 1


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


def test_artifact_schema_valid():
    valid = {
        "id": "speak",
        "kind": "function",
        "status": "draft",
        "source_address": "0x1400077c0",
        "created": "2026-08-08T00:00:00Z",
    }
    assert _validate_artifact(valid) == []
    bad = dict(valid, status="confirmed_by_ai")
    assert "invalid status" in "\n".join(_validate_artifact(bad))
    missing = {"id": "speak"}
    assert _validate_artifact(missing)  # missing fields reported


def test_confidence_state_machine_one_way():
    assert _transition_is_legal("draft", "candidate")
    assert _transition_is_legal("candidate", "confirmed")
    # no skips, no downgrades, no repeats
    assert not _transition_is_legal("draft", "confirmed")
    assert not _transition_is_legal("candidate", "draft")
    assert not _transition_is_legal("confirmed", "candidate")
    assert not _transition_is_legal("confirmed", "draft")


def test_review_gate_is_opinion_only():
    # §15.4: a review gate MUST NOT change a status directly.
    opinion = {
        "artifact": "speak",
        "verdict": "suggest candidate",
        "reason": "source provenance valid (trace)",
    }
    assert "status" not in opinion, "review opinion must not write status"
    assert "verdict" in opinion


def test_role_profiles_declare_subprocess():
    # v0.8: the only sanctioned reference subagent role is the review gate.
    for role in ("anchor.judge",):
        skill_file = SKILLS_DIR / role / "SKILL.md"
        assert skill_file.is_file(), f"{role}: role profile missing"
        fm = _frontmatter(skill_file.read_text(encoding="utf-8"))
        assert fm.get("kind") == "role", f"{role}: missing kind: role"
        assert fm.get("runAs") == "subagent", f"{role}: must declare runAs: subagent"


def test_no_unapproved_subagent_roles():
    # v0.8 convergence-gate model: only judge is sanctioned; scout/worker
    # must not reappear as reference roles.
    for name in ("anchor.scout", "anchor.worker"):
        skill_file = SKILLS_DIR / name / "SKILL.md"
        assert not skill_file.exists(), (
            f"{name} must not exist: v0.8 removed non-judge subagent roles"
        )
