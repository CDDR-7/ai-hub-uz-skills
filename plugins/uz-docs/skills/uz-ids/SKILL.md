---
name: uz-ids
description: Check the format of Uzbek identifiers — PINFL / JShShIR (personal number), STIR / INN (taxpayer number), passport and ID card numbers — and normalize and mask them. Use when a form, spreadsheet, contract or code handles these identifiers and needs validation, cleanup or test data.
license: MIT
metadata:
  description-ru: "Проверка формата ПИНФЛ, СТИР (ИНН), серии и номера паспорта или ID-карты: нормализация и маскирование."
  description-uz-Latn: "JShShIR, STIR, pasport va ID-karta raqamlari formatini tekshirish, normallashtirish va yashirish."
  description-uz-Cyrl: "ЖШШИР, СТИР, паспорт ва ID-карта рақамлари форматини текшириш, нормаллаштириш ва яшириш."
---

# Uzbek identifiers

These identifiers are **personal data**. Work with them only as much as the task needs:

- Do not repeat full values back to the user; show the `masked` form (last 4 characters).
- Do not save them to files, logs, memory or examples unless the user explicitly asks for that.
- For examples, tests and fixtures use obviously synthetic values (`12345678901234`, `AA0000001`), never real ones.

## Checking

```bash
python3 scripts/ids.py check pinfl "1234 5678 9012 34"   # {"ok": true, "normalized": "12345678901234", ...}
python3 scripts/ids.py check stir 123456789
python3 scripts/ids.py check passport "aa 1234567"       # normalized: AA1234567
python3 scripts/ids.py check auto AB0000001              # guesses the kind by the format
```

The output is JSON with `kind`, `ok`, `normalized`, `masked`, `checksum`. The exit code is 1 when the format does not match. The script removes spaces and dashes, and uppercases passport letters. Stdlib only, Python 3.9+.

| Identifier | Also called | Format checked |
|---|---|---|
| PINFL | JShShIR, ПИНФЛ — personal identification number of an individual | 14 digits |
| STIR | INN, ИНН — taxpayer identification number | 9 digits |
| Passport / ID card | серия и номер | 2 Latin letters + 7 digits |

## Limits — say them to the user

- **Only the format is checked.** `"checksum": "not-checked"` means exactly that: check-digit algorithms and the meaning of the digit positions are not implemented until they are confirmed by an official source (see `VERIFY.md` in the repository root). Do not invent or "recall" a check-digit algorithm, and do not decode birth date, gender or region from a PINFL.
- A valid format does not mean the identifier exists or belongs to the person. Only the issuing authority's services can confirm that.
- Do not list which passport series are "valid": the series change over time.

For code (form validators, database constraints), use the same rules as the script: strip spaces and dashes, then match `^\d{14}$`, `^\d{9}$` or `^[A-Z]{2}\d{7}$`.

The cases are in `tests/cases.json` (input → expected output); the repository CI runs them.
