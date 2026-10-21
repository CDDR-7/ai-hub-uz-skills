---
name: uz-translit
description: Transliterate Uzbek text between Latin (oʻzbek lotin alifbosi, 1995 rules) and Cyrillic script. Use when the user asks to convert Uzbek text to Latin or Cyrillic, to "lotinga oʻgir" / "kirillga oʻgir", to fix oʻ/gʻ apostrophes, or to prepare the same text in both Uzbek scripts.
---

# Uzbek Latin ↔ Cyrillic

Run the bundled script first; it applies the letter rules deterministically. Then review its output for the cases listed under "Check by hand".

```bash
python3 scripts/translit.py --to latn "Ўзбекистон Республикаси"   # -> Oʻzbekiston Respublikasi
python3 scripts/translit.py --to cyrl "Toshkent shahri"           # -> Тошкент шаҳри
python3 scripts/translit.py --to latn --ascii < text.txt          # ' instead of ʻ and ʼ
```

The script reads stdin when no text is given. It keeps URLs and e-mail addresses as is, along with digits, punctuation and Latin words that have no Uzbek letters to change. Stdlib only, Python 3.9+.

## Rules the script applies

| Cyrillic | Latin | Notes |
|---|---|---|
| ў, ғ | oʻ, gʻ | `ʻ` is U+02BB. In Latin→Cyrillic any apostrophe after o/g is accepted: ʻ ʼ ' ‘ ’ or a backtick |
| ш, ч | sh, ch | Case follows the word: Шаҳар → Shahar, ШАҲАР → SHAHAR |
| қ, ҳ, х | q, h, x | |
| ж, й | j, y | |
| ё, ю, я | yo, yu, ya | yoʻl is y + oʻ (йўл), not ё |
| е | ye / e | ye at the start of a word, after a vowel, ъ or ь (ер → yer, поезд → poyezd); e otherwise |
| э | e | Latin→Cyrillic: e → э at the start of a word or after a vowel (eshik → эшик, poet → поэт), е otherwise |
| ъ | ʼ | `ʼ` is U+02BC (tutuq belgisi): маъно → maʼno. Before е/ё it is dropped: объект → obyekt |
| ь | — | dropped: пальто → palto |
| ц | s / ts | ts after a vowel (милиция → militsiya), s otherwise (цирк → sirk, концерт → konsert) |
| сҳ | sʼh | the apostrophe keeps s and h apart: Исҳоқ ↔ Isʼhoq |

## Check by hand

Latin → Cyrillic loses information the script cannot recover. Fix these after the run:

- **ц in loanwords.** Latin writes it as s or ts, so the script writes с / тс: sirk → сирк, but the word is цирк; militsiya → милитсия, but the word is милиция. Restore ц in Russian and international loanwords (цирк, концерт, милиция, лицей, акция, станция).
- **ь and ъ in loanwords.** palto → палто, but the word is пальто; obyekt → обект, but the word is объект.
- **e after a vowel** in Uzbek (not loan) words: the script writes э. Check that the word is spelled that way.
- **Proper names, brands, code, quotes in another language** — do not transliterate them unless the user asks.

Cyrillic → Latin is exact for native words; the only judgment calls are loanwords with ц (the vowel rule is the common spelling) and names that have an established Latin form.

## Output

- Use the real `ʻ` (U+02BB) and `ʼ` (U+02BC) unless the user or the target system needs ASCII; then pass `--ascii` and tell the user that both became `'`.
- Keep the layout of the input: line breaks, lists, Markdown, numbers.
- When both scripts are requested, give the Latin text first, then the Cyrillic one.

The rule cases are in `tests/cases.json` (input → expected output); the repository CI runs them.
