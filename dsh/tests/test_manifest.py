"""test_manifest.py — validate the 11 anchor-* skill manifests for DSH.

DSH requirements (dsh-skill-filesystem):
  - name must match /^[a-z0-9]+(?:-[a-z0-9]+)*$/ (kebab-case)
  - description is required
Optional: whenToUse (string). Unknown fields are ignored by DSH.

Single-source-of-truth guard against the protocol's canonical Reasonix skills
in ../.reasonix/skills (same repository):
  - every anchor-* here has an anchor.* counterpart
  - the BODY (everything after the closing frontmatter delimiter) must match
    the upstream body byte-for-byte after line-ending normalization (CRLF -> LF)
    and surrounding-whitespace trimming. Only frontmatter adaptation is allowed.
  - description is preserved verbatim (protocol manifest consistency, §14)

Exit code 0 = pass; 1 = any check failed.
"""

import re
import sys
from pathlib import Path

from anchorlaw import i_dont_know as idk

SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# This file lives at <repo>/dsh/tests/test_manifest.py
ROOT = Path(__file__).resolve().parent.parent          # <repo>/dsh
SKILLS_DIR = ROOT / "skills"                            # DSH-format skills
UPSTREAM_DIR = ROOT.parent / ".reasonix" / "skills"     # canonical bodies

EXPECTED = {
    "anchor-challenge", "anchor-concepts", "anchor-degrade", "anchor-judge",
    "anchor-maintain", "anchor-noise", "anchor-scan", "anchor-scout",
    "anchor-test", "anchor-worker", "anchor-write",
}


@idk("frontmatter 解析只覆盖本仓库 SKILL.md 使用的 YAML 子集，未覆盖完整 YAML 规范",
     source="static: 仅按本仓库 manifest 形态验证")
def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip("'\"")
    return fm


@idk("正文提取只覆盖本仓库 SKILL.md 的 frontmatter 闭合形态（\\n--- 分隔）",
     source="static: 仅按本仓库 manifest 形态验证")
def body_of(text: str) -> str:
    """Everything after the closing frontmatter delimiter, normalized (CRLF->LF)."""
    end = text.find("\n---", 3)
    body = text[end + 4:] if end >= 0 else text
    return body.replace("\r\n", "\n").strip()


@idk("main() 的退出码契约仅在 CLI 直跑路径验证，未覆盖被 import 复用的场景",
     source="static: 设计为脚本入口，未测试 import 复用")
def main() -> int:
    failures = []

    if not SKILLS_DIR.is_dir():
        failures.append(f"skills dir missing: {SKILLS_DIR}")
        print("\n".join(failures))
        return 1

    found = set()
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        md = skill_dir / "SKILL.md"
        name = skill_dir.name
        if not md.is_file():
            failures.append(f"{name}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        body = body_of(text)
        found.add(name)

        # name
        if fm.get("name") != name:
            failures.append(f"{name}: frontmatter name '{fm.get('name')}' != dir name '{name}'")
        if not SKILL_NAME.match(name):
            failures.append(f"{name}: not kebab-case (DSH rejects it)")

        # description
        desc = fm.get("description")
        if not desc:
            failures.append(f"{name}: missing required description")

        # whenToUse optional: must be a string when present
        wtu = fm.get("whenToUse")
        if wtu is not None and not isinstance(wtu, str):
            failures.append(f"{name}: whenToUse must be a string")

        # upstream cross-check: canonical body in ../.reasonix/skills/anchor.<name-without-dash>
        upstream = UPSTREAM_DIR / name.replace("-", ".")
        if upstream.is_dir():
            up_md = upstream / "SKILL.md"
            if up_md.is_file():
                up_text = up_md.read_text(encoding="utf-8")
                up_fm = parse_frontmatter(up_text)
                if up_fm.get("description") != desc:
                    failures.append(f"{name}: description drifted from upstream")
                if body_of(up_text) != body:
                    failures.append(f"{name}: BODY drifted from upstream "
                                   f"(canonical edits go to .reasonix/skills/{upstream.name})")
            else:
                failures.append(f"{name}: upstream dir missing SKILL.md")
        else:
            failures.append(f"{name}: no upstream counterpart {name.replace('-', '.')}")

    missing = EXPECTED - found
    if missing:
        failures.append(f"missing skills: {sorted(missing)}")
    extra = found - EXPECTED
    if extra:
        failures.append(f"unexpected skills: {sorted(extra)}")

    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"OK: {len(found)} anchor skills valid; bodies consistent with ../.reasonix/skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
