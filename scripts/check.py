#!/usr/bin/env python3
"""Repository gate: marketplace structure, skill frontmatter, licenses and skill tests.

    python3 scripts/check.py           # everything
    python3 scripts/check.py --no-tests

The SKILL.md rules mirror `uz-gate validate` of the hub (CDDR-7/ai-hub-uz), so a skill
that passes here is imported by the hub as is. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

errors: list[str] = []


def fail(path: Path | str, msg: str) -> None:
    rel = path.relative_to(ROOT) if isinstance(path, Path) else path
    errors.append(f"{rel}: {msg}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fail(path, f"cannot read JSON: {e}")
        return None


def frontmatter(text: str) -> dict | None:
    """Top-level `key: value` pairs of the YAML frontmatter (enough for name and description)."""
    text = text.removeprefix("﻿")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    meta = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            v = m.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            meta[m.group(1)] = v
    return meta


def check_skill(skill_md: Path) -> None:
    meta = frontmatter(skill_md.read_text(encoding="utf-8"))
    if meta is None:
        return fail(skill_md, "no YAML frontmatter between --- lines")
    name, desc = meta.get("name", ""), meta.get("description", "")
    if not NAME.match(name):
        fail(skill_md, f"name {name!r}: lowercase Latin letters, digits and hyphens only")
    elif name != skill_md.parent.name:
        fail(skill_md, f"name {name!r} must match the folder {skill_md.parent.name!r}")
    if not desc:
        fail(skill_md, "description is required: the agent decides from it when to use the skill")
    elif len(desc) > 1024:
        fail(skill_md, "description is longer than 1024 characters")


def run_tests(skill: Path) -> int:
    cases_file = skill / "tests" / "cases.json"
    if not cases_file.exists():
        fail(skill, "tests/cases.json is missing: every skill ships input -> output examples")
        return 0
    cases = load_json(cases_file) or []
    scripts = sorted((skill / "scripts").glob("*.py"))
    for i, case in enumerate(cases):
        script = skill / "scripts" / case["script"] if "script" in case else (scripts[0] if len(scripts) == 1 else None)
        if script is None:
            fail(cases_file, f"case {i}: set \"script\" (the skill has {len(scripts)} scripts)")
            continue
        r = subprocess.run([sys.executable, "-I", str(script), *case["args"]], input=case.get("stdin"),
                           capture_output=True, text=True, timeout=30)
        want_code = case.get("code", 0)
        if r.stdout.strip() != case["out"] or r.returncode != want_code:
            fail(cases_file, f"case {i} {case['args']}: got {r.stdout.strip()!r} (exit {r.returncode}), "
                             f"want {case['out']!r} (exit {want_code})")
    return len(cases)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--no-tests", action="store_true")
    a = p.parse_args()

    mp_path = ROOT / ".claude-plugin" / "marketplace.json"
    mp = load_json(mp_path) or {}
    if not NAME.match(mp.get("name", "")):
        fail(mp_path, "name: kebab-case marketplace name is required")
    listed = {}
    for entry in mp.get("plugins", []):
        name = entry.get("name", "")
        if name in listed:
            fail(mp_path, f"plugin {name!r} is listed twice")
        listed[name] = entry
        if entry.get("source") != f"./plugins/{name}":
            fail(mp_path, f"{name}: source must be ./plugins/{name}")
        if not entry.get("description"):
            fail(mp_path, f"{name}: description is required")

    total = 0
    packs = sorted(d for d in (ROOT / "plugins").iterdir() if d.is_dir())
    for pack in packs:
        if pack.name not in listed:
            fail(pack, "not listed in .claude-plugin/marketplace.json")
        for required in ("LICENSE", "README.md"):
            if not (pack / required).is_file():
                fail(pack, f"{required} is required in every pack")
        pj_path = pack / ".claude-plugin" / "plugin.json"
        pj = load_json(pj_path) or {}
        if pj.get("name") != pack.name:
            fail(pj_path, f"name must be {pack.name!r}")
        if not SEMVER.match(pj.get("version", "")):
            fail(pj_path, "version: MAJOR.MINOR.PATCH is required")
        elif pack.name in listed and listed[pack.name].get("version") != pj["version"]:
            fail(mp_path, f"{pack.name}: version differs from plugin.json ({pj['version']})")
        if not pj.get("license"):
            fail(pj_path, "license is required")
        skills = sorted(d for d in (pack / "skills").iterdir() if d.is_dir()) if (pack / "skills").is_dir() else []
        if not skills:
            fail(pack, "no skills/<skill>/SKILL.md")
        for skill in skills:
            if not (skill / "SKILL.md").is_file():
                fail(skill, "SKILL.md is missing")
                continue
            check_skill(skill / "SKILL.md")
            if not a.no_tests:
                total += run_tests(skill)
    for name in listed:
        if not (ROOT / "plugins" / name).is_dir():
            fail(mp_path, f"{name}: ./plugins/{name} does not exist")

    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(packs)} packs, {total} test cases, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
