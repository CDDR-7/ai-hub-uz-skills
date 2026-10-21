# uz-lang

Transliterates Uzbek text between the Latin alphabet (1995 rules: oʻ, gʻ, sh, ch, the ʼ tutuq belgisi) and Cyrillic, in both directions. The bundled script applies the letter rules deterministically; the skill tells the agent which loanword cases to fix by hand.

## Install

```
/plugin marketplace add CDDR-7/ai-hub-uz-skills
/plugin install uz-lang@ai-point-uz
```

Manual install: copy `skills/uz-translit` into `~/.claude/skills/` (personal) or `.claude/skills/` (project).

## Use

Ask Claude to convert Uzbek text: "lotinga oʻgir", "переведи на кириллицу", "give me this in both Uzbek scripts". The skill runs a Python 3 script (stdlib only), so the agent needs a shell.

Skill: [`skills/uz-translit/SKILL.md`](skills/uz-translit/SKILL.md). Tests: `skills/uz-translit/tests/cases.json`. License: MIT.
