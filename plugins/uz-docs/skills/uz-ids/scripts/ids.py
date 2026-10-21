#!/usr/bin/env python3
"""Format checks for Uzbek identifiers: PINFL (JShShIR), STIR (INN), passport / ID card number.

    ids.py check pinfl|stir|passport VALUE   # one kind
    ids.py check auto VALUE                  # guess the kind from the format

Prints JSON: kind, ok, normalized, masked, checksum. Only the format is checked:
check-digit algorithms are not implemented until confirmed by an official source
(VERIFY.md in the repository root). Stdlib only; see ../SKILL.md.
"""

import argparse
import json
import re
import sys

FORMATS = {
    "pinfl": (re.compile(r"^\d{14}$"), "14 digits"),
    "stir": (re.compile(r"^\d{9}$"), "9 digits"),
    "passport": (re.compile(r"^[A-Z]{2}\d{7}$"), "2 Latin letters + 7 digits"),
}


def normalize(kind: str, value: str) -> str:
    s = re.sub(r"[\s\- ]", "", value)
    return s.upper() if kind in ("passport", "auto") else s


def mask(value: str) -> str:
    """Keeps the last 4 characters: identifiers are personal data, do not echo them in full."""
    return "*" * max(len(value) - 4, 0) + value[-4:]


def check(kind: str, value: str) -> dict:
    s = normalize(kind, value)
    if kind == "auto":
        kind = next((k for k, (rx, _) in FORMATS.items() if rx.match(s)), "unknown")
        if kind == "unknown":
            return {"kind": "unknown", "ok": False, "masked": mask(s),
                    "error": "matches none of: " + ", ".join(f"{k} ({d})" for k, (_, d) in FORMATS.items())}
    rx, desc = FORMATS[kind]
    out = {"kind": kind, "ok": bool(rx.match(s)), "normalized": s, "masked": mask(s), "checksum": "not-checked"}
    if not out["ok"]:
        del out["normalized"]
        out["error"] = f"expected {desc}"
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("mode", choices=("check",))
    p.add_argument("kind", choices=(*FORMATS, "auto"))
    p.add_argument("value")
    a = p.parse_args()
    res = check(a.kind, a.value)
    print(json.dumps(res, ensure_ascii=False, sort_keys=True))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
