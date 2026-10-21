#!/usr/bin/env python3
"""Uzbek soʻm (UZS) amounts: digits and words, Russian and Uzbek (Latin).

    amounts.py format AMOUNT [--lang ru|uz] [--nbsp] [--code]   # 1 234 567,89 сум
    amounts.py words  AMOUNT [--lang ru|uz]                     # Один миллион ... сумов 89 тийинов

AMOUNT accepts "1234567.89", "1 234 567,89", "1,234,567.89" and "-500". Tiyin are
rounded half up to 2 digits (1 soʻm = 100 tiyin). Stdlib only; see ../SKILL.md.
"""

import argparse
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CURRENCY = {"ru": "сум", "uz": "soʻm"}

RU_ONES_M = ["", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
RU_ONES_F = ["", "одна", "две"] + RU_ONES_M[3:]
RU_TEENS = ["десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать",
            "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"]
RU_TENS = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят",
           "восемьдесят", "девяносто"]
RU_HUNDREDS = ["", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот",
               "восемьсот", "девятьсот"]
# (one, few, many) and the gender of the numeral before it.
RU_SCALES = [(("", "", ""), "m"), (("тысяча", "тысячи", "тысяч"), "f"),
             (("миллион", "миллиона", "миллионов"), "m"), (("миллиард", "миллиарда", "миллиардов"), "m")]
RU_SOM = ("сум", "сума", "сумов")
RU_TIYIN = ("тийин", "тийина", "тийинов")

UZ_ONES = ["", "bir", "ikki", "uch", "toʻrt", "besh", "olti", "yetti", "sakkiz", "toʻqqiz"]
UZ_TENS = ["", "oʻn", "yigirma", "oʻttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "toʻqson"]
UZ_SCALES = ["", "ming", "million", "milliard"]

MAX = 10**12  # up to 999 999 999 999,99


def parse(raw: str) -> Decimal:
    s = re.sub(r"[\s  ']", "", raw)
    if "," in s and "." in s:  # both: the last one is the decimal separator
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    else:  # one kind: repeated means thousands (1.234.567), single means decimal (12,5)
        for sep in ",.":
            if s.count(sep) > 1:
                s = s.replace(sep, "")
        s = s.replace(",", ".")
    try:
        value = Decimal(s)
    except InvalidOperation:
        raise SystemExit(f"not an amount: {raw!r}")
    value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if abs(value) >= MAX:
        raise SystemExit(f"amount out of range (< {MAX:,}): {raw!r}".replace(",", " "))
    return value


def split(value: Decimal) -> tuple[bool, int, int]:
    cents = int(abs(value) * 100)
    return value < 0, cents // 100, cents % 100


def fmt(value: Decimal, lang: str, nbsp: bool = False, code: bool = False) -> str:
    neg, som, tiyin = split(value)
    sep = " " if nbsp else " "
    digits = f"{som:,}".replace(",", sep)
    if tiyin:
        digits += f",{tiyin:02d}"
    unit = "UZS" if code else CURRENCY[lang]
    return f"{'-' if neg else ''}{digits}{sep}{unit}"


def ru_plural(n: int, forms: tuple[str, str, str]) -> str:
    if 11 <= n % 100 <= 14:
        return forms[2]
    return forms[0] if n % 10 == 1 else forms[1] if 2 <= n % 10 <= 4 else forms[2]


def ru_triple(n: int, gender: str) -> list[str]:
    ones = RU_ONES_F if gender == "f" else RU_ONES_M
    words = [RU_HUNDREDS[n // 100]]
    rest = n % 100
    if 10 <= rest <= 19:
        words.append(RU_TEENS[rest - 10])
    else:
        words += [RU_TENS[rest // 10], ones[rest % 10]]
    return [w for w in words if w]


def ru_words(n: int) -> str:
    if n == 0:
        return "ноль"
    words = []
    for scale in range(len(RU_SCALES) - 1, -1, -1):
        group = n // 1000**scale % 1000
        if group:
            forms, gender = RU_SCALES[scale]
            words += ru_triple(group, gender)
            if scale:
                words.append(ru_plural(group, forms))
    return " ".join(words)


def uz_triple(n: int) -> list[str]:
    words = []
    if n // 100:
        words += [UZ_ONES[n // 100], "yuz"]
    words += [UZ_TENS[n % 100 // 10], UZ_ONES[n % 10]]
    return [w for w in words if w]


def uz_words(n: int) -> str:
    if n == 0:
        return "nol"
    words = []
    for scale in range(len(UZ_SCALES) - 1, -1, -1):
        group = n // 1000**scale % 1000
        if group:
            words += uz_triple(group)
            if scale:
                words.append(UZ_SCALES[scale])
    return " ".join(words)


def words(value: Decimal, lang: str) -> str:
    neg, som, tiyin = split(value)
    if lang == "ru":
        text = f"{ru_words(som)} {ru_plural(som, RU_SOM)} {tiyin:02d} {ru_plural(tiyin, RU_TIYIN)}"
        text = ("минус " if neg else "") + text
    else:
        text = ("minus " if neg else "") + f"{uz_words(som)} soʻm {tiyin:02d} tiyin"
    return text[0].upper() + text[1:]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("mode", choices=("format", "words"))
    p.add_argument("amount")
    p.add_argument("--lang", choices=("ru", "uz"), default="ru")
    p.add_argument("--nbsp", action="store_true", help="non-breaking spaces (format)")
    p.add_argument("--code", action="store_true", help="UZS instead of сум / soʻm (format)")
    a = p.parse_args()
    value = parse(a.amount)
    print(fmt(value, a.lang, a.nbsp, a.code) if a.mode == "format" else words(value, a.lang))
    return 0


if __name__ == "__main__":
    sys.exit(main())
