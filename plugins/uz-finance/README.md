# uz-finance

Formats Uzbek soʻm (UZS) amounts the way local documents write them (1 234 567,89 сум) and writes amounts out in words in Russian and Uzbek, with tiyin and correct Russian plural forms. Useful for invoices, contracts and payment orders.

## Install

```
/plugin marketplace add CDDR-7/ai-hub-uz-skills
/plugin install uz-finance@ai-point-uz
```

Manual install: copy `skills/uzs-amounts` into `~/.claude/skills/` (personal) or `.claude/skills/` (project).

## Use

Ask Claude for "сумма прописью", "soʻm soʻz bilan" or to format UZS amounts in a document or table. The skill runs a Python 3 script (stdlib only), so the agent needs a shell.

Skill: [`skills/uzs-amounts/SKILL.md`](skills/uzs-amounts/SKILL.md). Tests: `skills/uzs-amounts/tests/cases.json`. License: MIT.
