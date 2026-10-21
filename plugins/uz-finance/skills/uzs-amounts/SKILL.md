---
name: uzs-amounts
description: Format Uzbek soʻm (UZS) amounts and write them out in words in Russian or Uzbek, with tiyin. Use for invoices, contracts, payment orders, receipts or any text that needs "1 234 567,89 сум", "сумма прописью" or "soʻm soʻz bilan" for UZS.
license: MIT
metadata:
  description-ru: "Суммы в сумах (UZS): формат «1 234 567,89 сум» и сумма прописью на русском и узбекском, с тийинами."
  description-uz-Latn: "Soʻmdagi (UZS) summalar: «1 234 567,89 soʻm» formati va summani rus hamda oʻzbek tillarida soʻz bilan yozish."
  description-uz-Cyrl: "Сўмдаги (UZS) суммалар: «1 234 567,89 сўм» формати ва суммани рус ҳамда ўзбек тилларида сўз билан ёзиш."
---

# UZS amounts

1 soʻm = 100 tiyin; ISO 4217 code `UZS`. Run the bundled script for the digits and the words — it handles grouping, rounding and Russian plural forms, which are easy to get wrong by hand.

```bash
python3 scripts/amounts.py format 1234567.89                 # 1 234 567,89 сум
python3 scripts/amounts.py format 1234567.89 --lang uz       # 1 234 567,89 soʻm
python3 scripts/amounts.py format 1234567.89 --code --nbsp   # 1 234 567,89 UZS, non-breaking spaces
python3 scripts/amounts.py words 1234567.89                  # Один миллион двести тридцать четыре тысячи пятьсот шестьдесят семь сумов 89 тийинов
python3 scripts/amounts.py words 1234567.89 --lang uz        # Bir million ikki yuz oʻttiz toʻrt ming besh yuz oltmish yetti soʻm 89 tiyin
```

Stdlib only, Python 3.9+. Amounts up to 999 999 999 999,99.

## Conventions

- **Digits:** groups of three separated by a space, decimal comma: `1 234 567,89`. Use `--nbsp` for documents and HTML, so the amount does not break across lines.
- **Tiyin:** two digits after the comma, rounded half up (`0,005` → `0,01`). Whole amounts are written without `,00` in digits. In words, tiyin are always written as two digits: `… сумов 00 тийинов`, as in payment documents.
- **Currency name:** `сум` in Russian text, `soʻm` in Uzbek Latin. Use `UZS` (`--code`) in tables, bank details and anywhere other currencies appear next to it.
- **Words:** Russian uses the plural forms сум / сума / сумов and тийин / тийина / тийинов, and feminine «одна/две тысячи». The words start with a capital letter. Uzbek nouns do not take a plural after numbers: `besh ming soʻm`.
- **Uzbek Cyrillic:** produce the Latin words, then convert them with the `uz-translit` skill (`uz-lang` pack), if it is installed.

## Input

The script accepts `1234567.89`, `1 234 567,89`, `1,234,567.89`, `1.234.567` and negative amounts. A single `,` or `.` is read as the decimal separator; repeated ones as thousands separators. If an amount in the user's text could be read both ways (for example `1,234`), ask before converting.

## Do not

- Do not convert between currencies or quote exchange rates from memory. Ask for the rate and its date, or use a source the user names.
- Do not change the amount the user gave; when rounding to tiyin changes it, say so.

The cases are in `tests/cases.json` (input → expected output); the repository CI runs them. The Uzbek number words are awaiting review by a native speaker (`VERIFY.md` in the repository root).
