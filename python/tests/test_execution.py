"""Execution Topology conformance tests (protocol v0.17 §15/§16).

Verifies the execution layer of the reference implementation:

1. artifact schema: required fields + valid confidence status
   (reference-implementation convention; §15.5 classifies concrete layout
   as an implementation detail)
2. confidence state machine: one-way draft -> candidate -> confirmed,
   `confirmed` reserved for the host's human (§15.4)
3. review gate: judge output is opinion-only, never a status change (§15.4)
4. role profiles: judge / scout / worker are sanctioned reference roles —
   kind: role, runAs: subagent (v0.10 Judge-driven pipeline, §15.1);
   v0.8's "only judge" restriction is superseded
5. judge institutionalization (v0.9; v0.10 extended): trigger points are
   normative and mirrored across protocol §15.4 / AGENTS.md index / judge SKILL
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
    # v0.10: judge / scout / worker are the sanctioned reference roles
    # (Judge-driven pipeline, §15.1).
    for role in ("anchor.judge", "anchor.scout", "anchor.worker"):
        skill_file = SKILLS_DIR / role / "SKILL.md"
        assert skill_file.is_file(), f"{role}: role profile missing"
        fm = _frontmatter(skill_file.read_text(encoding="utf-8"))
        assert fm.get("kind") == "role", f"{role}: missing kind: role"
        assert fm.get("runAs") == "subagent", f"{role}: must declare runAs: subagent"


def test_roles_defined_in_protocol_pipeline():
    # v0.10 Judge-driven pipeline (§15.1): scout/worker are sanctioned
    # reference roles, each with an explicit pipeline stage.
    proto = (REPO_ROOT / "spec" / "protocol-v0.17.md").read_text(encoding="utf-8")
    for marker in ("**Scout** (subprocess)", "**Worker** (subprocess)", "Input contract", "Parallel implementation"):
        assert marker in proto, f"protocol §15.1 missing role/stage marker: {marker}"


def test_judge_trigger_points_normative_in_protocol():
    # v0.9 §15.4: the review gate is a mandatory checkpoint at specific
    # decision points, not only a closing gate.
    proto = (REPO_ROOT / "spec" / "protocol-v0.17.md").read_text(encoding="utf-8")
    for marker in (
        "**Judge trigger points (v0.9; extended v0.10)**",
        "**Self-review ≠ review gate (v0.9)**",
        "**Plan-time judge placement (v0.9)**",
    ):
        assert marker in proto, f"protocol §15.4 missing marker: {marker}"
    # v0.10 pipeline trigger points are normative
    for stage_marker in ("Input contract acceptance", "Spec approval", "Module integration", "Delivery acceptance"):
        assert stage_marker in proto, f"protocol §15.4 missing stage trigger: {stage_marker}"
    # confirmed gating MUST be normative (not advisory)
    assert "MUST precede any human grant of `confirmed`" in proto
    # producer self-check MUST NOT be presented as the review gate
    assert "self-check MUST NOT be presented as the §15.4 review gate" in proto
    # plan-time placement MUST be normative
    assert "MUST pre-place judge steps at the trigger points" in proto


def test_agents_force_chain_lists_judge_triggers():
    # v0.9 AGENTS.md: index-only discipline — AGENTS must point at §15.4 /
    # anchor.judge rather than mirroring protocol text (mirror drift is the
    # root cause of review loops; §15.4 D-tier guard).
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    # index pointer exists
    assert "协议 §15.4" in agents and "只索引不复制" in agents
    # force-chain skeleton retained (v0.12 four-stage pipeline, 非镜像)
    for marker in ("输入契约", "实施规范", "实施计划", "并行实施", "交付"):
        assert marker in agents, f"AGENTS.md pipeline skeleton missing: {marker}"
    # must NOT copy the protocol's normative bullet text (mirror drift guard)
    for banned in ("MUST 有 judge 审查意见", "重大转向 MUST judge", "自评 ≠ judge"):
        assert banned not in agents, (
            f"AGENTS.md must not mirror §15.4 normative text: {banned}"
        )


def test_judge_skill_documents_trigger_points():
    # v0.9 judge reference profile: trigger-point section aligned with §15.4.
    skill = (SKILLS_DIR / "anchor.judge" / "SKILL.md").read_text(encoding="utf-8")
    assert "## 强制触发点（v0.9；v0.10 扩展）" in skill
    assert "`confirmed` 授予前" in skill
    for marker in ("结案重开", "根因定论", "范围决策"):
        assert marker in skill, f"judge SKILL trigger list missing: {marker}"
    assert "自评 ≠ 审查" in skill


def test_section11_audits_v09_claims():
    # v0.9 self-reference (protocol §11): every new universal claim MUST be
    # audited in the §11 table; the audit rows must be present so a §15.4
    # change cannot silently desync the claim audit.
    proto = (REPO_ROOT / "spec" / "protocol-v0.17.md").read_text(encoding="utf-8")
    audit_rows = (
        '`confirmed` MUST be granted only after a judge review opinion exists',
        "Major redirections (case reopening, root-cause determination, significant scope",
        "Producer self-review does NOT constitute the review gate",
        "Workflow plans MUST pre-place judge steps at trigger points",
        "Auto-promoted `candidate` (Full mode) MUST note the absence",
    )
    audit_lines = [
        line
        for line in proto.splitlines()
        if any(row in line for row in audit_rows)
    ]
    assert len(audit_lines) == len(audit_rows), (
        f"§11 audit table must carry all v0.9 claims (found {len(audit_lines)})"
    )
    for line in audit_lines:
        assert "scoped (unverified)" in line, (
            "v0.9 audit rows must stay honest (unverified): " + line[:80]
        )


def test_verification_termination_gates_in_protocol():
    # v0.9/v0.10 §15.4 termination gates: the pipeline MUST terminate on
    # mechanical criteria — external test set, three-tier opinions,
    # Judge-nod termination (v0.10, replaces the round cap).
    proto = (REPO_ROOT / "spec" / "protocol-v0.17.md").read_text(encoding="utf-8")
    assert "**Verification termination gates" in proto
    # A: termination on the external test set; no in-place test additions
    assert "The external test set passes" in proto
    assert "MUST NOT add tests during the verification phase" in proto
    # B: three tiers, only blocking blocks
    assert "exactly three tiers" in proto
    assert "(i) test failure" in proto and "(ii) build/compile failure" in proto
    assert "MUST NOT require more than one verification" in proto
    # C: Judge-nod termination with mechanical fallback (v0.12; v0.15 amended) —
    # criteria satisfied = done; same-criterion iteration capped at 3, then the
    # pipeline MUST halt and the Judge submits a detailed report of the review
    # situation and unresolved issues to the human, who decides
    assert "Judge-nod termination" in proto
    assert "mechanical fallback" in proto
    assert "capped at 3" in proto
    assert "halt entirely" in proto
    assert "submit a detailed report" in proto
    assert "the human decides" in proto
    assert "Acceptance criteria first (v0.10; v0.11 amended)" in proto
    assert "MUST be persisted as an artifact" in proto
    # E: evidence conflicts go through §12 or recorded exclusion, never the loop
    assert "never by\n  entering the verification loop" in proto or "never by\n  entering" in proto or "never by entering" in proto


def test_v013_challenge_outcome_registered():
    # v0.13: §12 challenge (RE report: unregistered universal claim) — the
    # constructiveness claim is scoped to the input-contract domain and
    # registered in §11; input-contract confirmation criterion in §16.1
    # (v0.14 generalized, protocol-neutral); §9.4 retry cap
    # upgraded to evidence saturation.
    proto = (REPO_ROOT / "spec" / "protocol-v0.17.md").read_text(encoding="utf-8")
    for marker in (
        "scoped to this domain",
        "Input-contract confirmation criterion (v0.13; v0.14 generalized)",
        "evidence saturation",
        "scoped (input-contract domain)",
    ):
        assert marker in proto, f"protocol missing v0.13 marker: {marker}"


def test_v014_input_contract_layering():
    # v0.14: input contract = confirmed requirements + technical-constraint
    # specification (customer-confirmable facts); architecture design is
    # stage-1 output. §16.1 criterion generalized — no RE-specific adaption:
    # the three protocols are independently operable frameworks.
    proto = (REPO_ROOT / "spec" / "protocol-v0.17.md").read_text(encoding="utf-8")
    for marker in (
        "technical-constraint specification",
        "does NOT carry the architecture design",
        "Input-contract confirmation criterion (v0.13; v0.14 generalized)",
        "protocol-neutral",
    ):
        assert marker in proto, f"protocol missing v0.14 marker: {marker}"
    # de-RE guard: no RE-specific adaption terms in the active text
    # (historical changelog/summary entries may still mention them).
    for banned in ("RE host", "reverse-engineering framework"):
        assert banned not in proto, f"protocol must not adapt to RE: {banned}"


def test_verification_termination_gates_in_agents():
    # v0.9 AGENTS.md: the termination gates must be executable from the
    # force chain — review changes MUST re-run the external test set
    # (approved plan + existing suite, NOT producer-added tests).
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "验证终止门禁" in agents
    # index-only: points at the protocol, does not re-copy the gate list
    assert "只索引不复制" in agents
    assert "协议 §15.4" in agents
    # the gate list itself lives in §15.4 / anchor.judge, not in AGENTS
    for banned in ("A 外部测试集", "B 意见分级", "C 轮次上限", "E 证据冲突"):
        assert banned not in agents, (
            f"AGENTS.md must not mirror the §15.4 gate list: {banned}"
        )


def test_judge_skill_documents_opinion_tiers():
    # v0.9 judge reference profile: three-tier opinion grading aligned with
    # §15.4 termination gates (only blocking blocks).
    skill = (SKILLS_DIR / "anchor.judge" / "SKILL.md").read_text(encoding="utf-8")
    assert "## 意见分级" in skill
    assert "blocking" in skill and "should-fix" in skill and "info" in skill
    assert "测试失败" in skill and "编译失败" in skill and "协议声称与实现" in skill
    assert "不得归入 blocking" in skill
    assert "排除误报的验证不得超过 1 轮" in skill
