# uz-docs

Checks the format of Uzbek identifiers — PINFL / JShShIR, STIR / INN, passport and ID card numbers — normalizes and masks them. It treats them as personal data: masked output, no logging, synthetic test values. Check-digit algorithms are not included until confirmed by an official source.

## Install

```
/plugin marketplace add CDDR-7/ai-hub-uz-skills
/plugin install uz-docs@ai-point-uz
```

Manual install: copy `skills/uz-ids` into `~/.claude/skills/` (personal) or `.claude/skills/` (project).

## Use

Ask Claude to validate or clean up a column of identifiers, write a form validator, or generate synthetic test data. The skill runs a Python 3 script (stdlib only), so the agent needs a shell.

Skill: [`skills/uz-ids/SKILL.md`](skills/uz-ids/SKILL.md). Tests: `skills/uz-ids/tests/cases.json`. License: MIT.
