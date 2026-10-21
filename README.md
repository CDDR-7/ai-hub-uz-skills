# ai-hub-uz-skills

Skills for AI agents in Uzbekistan — the skills marketplace of [ai-point.uz](https://ai-point.uz). The repository is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces): every pack is a plugin with one or more skills (`SKILL.md`), and the hub catalog imports them from here.

| Pack | Skill | What it does |
|---|---|---|
| [`uz-lang`](plugins/uz-lang) | `uz-translit` | Uzbek Latin ↔ Cyrillic transliteration (1995 rules) |
| [`uz-finance`](plugins/uz-finance) | `uzs-amounts` | UZS amounts: formatting, amounts in words (ru, uz) |
| [`uz-docs`](plugins/uz-docs) | `uz-ids` | PINFL, STIR, passport: format checks and masking |

## Install

In Claude Code:

```
/plugin marketplace add CDDR-7/ai-hub-uz-skills
/plugin install uz-lang@ai-point-uz
```

Manual install: copy a skill folder (for example `plugins/uz-lang/skills/uz-translit`) into `~/.claude/skills/` or the project's `.claude/skills/`. Each skill is a `SKILL.md` and a Python 3 script (stdlib only).

## Layout

```
.claude-plugin/marketplace.json      # marketplace "ai-point-uz": the list of packs
plugins/<pack>/
  .claude-plugin/plugin.json         # name, version, license
  LICENSE, README.md                 # required in every pack
  skills/<skill>/
    SKILL.md                         # frontmatter: name (= folder), description
    scripts/                         # deterministic helpers the skill runs
    tests/cases.json                 # input -> expected output, run by CI
scripts/check.py                     # the repository gate
VERIFY.md                            # what waits for an official source or a native speaker
```

## Adding a skill

1. Pick a pack (or add one: folder, `plugin.json`, `LICENSE`, `README.md`, entry in `marketplace.json`).
2. Add `skills/<name>/SKILL.md`: `name` in kebab-case equal to the folder, `description` up to 1024 characters saying what the skill does and when to use it.
3. Put input → output examples in `tests/cases.json` and run `python3 scripts/check.py`.
4. Bump `version` in `plugin.json` and in `marketplace.json`.

Rules: no secrets, no personal data in examples (synthetic values only), no names of real companies or government bodies, no facts the skill cannot source — put them in `VERIFY.md` instead.

CI (`.github/workflows/ci.yml`): `scripts/check.py` on Python 3.9 and 3.13, `claude plugin validate --strict`, Gitleaks.

License: MIT.
