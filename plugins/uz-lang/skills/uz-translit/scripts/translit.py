#!/usr/bin/env python3
"""Uzbek Latin <-> Cyrillic transliteration (1995 Latin alphabet rules).

    translit.py --to latn [--ascii] [TEXT...]   # Cyrillic -> Latin
    translit.py --to cyrl [TEXT...]             # Latin -> Cyrillic

Reads stdin when no TEXT is given. URLs and e-mail addresses are left as is.
Stdlib only; see ../SKILL.md for the rules and the cases the script cannot decide.
"""

import argparse
import re
import sys

OKINA = "ʻ"  # ʻ in oʻ, gʻ
TUTUQ = "ʼ"  # ʼ, the tutuq belgisi (Cyrillic ъ)
APOSTROPHES = set("ʻʼ'‘’`")  # a set: "" in a str is True

VOWELS_CYR = set("аеёиоуэюяўы")
VOWELS_LAT = set("aeiou")

CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ё": "yo", "ж": "j",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
    "х": "x", "ч": "ch", "ш": "sh", "щ": "sh", "ы": "i", "ь": "", "э": "e",
    "ю": "yu", "я": "ya", "ў": "o" + OKINA, "қ": "q", "ғ": "g" + OKINA, "ҳ": "h",
}

LAT_TO_CYR = {
    "a": "а", "b": "б", "c": "ц", "d": "д", "f": "ф", "g": "г", "h": "ҳ",
    "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о",
    "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у", "v": "в",
    "x": "х", "y": "й", "z": "з",
}
LAT_DIGRAPHS = {"sh": "ш", "ch": "ч", "yo": "ё", "yu": "ю", "ya": "я", "ye": "е"}

SKIP = re.compile(r"\S+://\S+|\S+@\S+\.\S+")


def _case(src: str, out: str, upper_word: bool) -> str:
    """Applies the case of the source letter to its (possibly multi-letter) result."""
    if not src.isupper() or not out:
        return out
    return out.upper() if upper_word else out[0].upper() + out[1:]


def _upper_word(text: str, i: int, width: int) -> bool:
    """True when the letter at i sits in an all-caps word (ШАҲАР -> SHAHAR, not ShAHAR)."""
    def is_upper(j: int) -> bool:
        return 0 <= j < len(text) and text[j].isalpha() and text[j].isupper()
    return is_upper(i - 1) or is_upper(i + width)


def to_latin(text: str, ascii_apostrophe: bool = False) -> str:
    out = []
    n = len(text)
    for i, ch in enumerate(text):
        low = ch.lower()
        prev = text[i - 1].lower() if i > 0 else ""
        nxt = text[i + 1].lower() if i + 1 < n else ""
        word_start = not prev.isalpha() and prev not in APOSTROPHES
        if low == "е":
            res = "ye" if word_start or prev in VOWELS_CYR or prev in {"ъ", "ь"} else "e"
        elif low == "ц":
            res = "ts" if prev in VOWELS_CYR else "s"
        elif low == "ъ":
            res = "" if nxt in {"е", "ё"} else TUTUQ  # объект -> obyekt, маъно -> maʼno
        elif low in CYR_TO_LAT:
            res = CYR_TO_LAT[low]
            if low == "ҳ" and prev in ("с", "ш", "ч"):
                res = TUTUQ + res  # Исҳоқ -> Isʼhoq: keeps s+h apart from sh
        else:
            out.append(ch)
            continue
        out.append(_case(ch, res, _upper_word(text, i, 1)))
    result = "".join(out)
    if ascii_apostrophe:
        result = result.replace(OKINA, "'").replace(TUTUQ, "'")
    return result


def to_cyrillic(text: str) -> str:
    out = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        low = ch.lower()
        nxt = text[i + 1] if i + 1 < n else ""
        prev = text[i - 1].lower() if i > 0 else ""
        word_start = not prev.isalpha() and prev not in APOSTROPHES
        if low in {"o", "g"} and nxt in APOSTROPHES:  # oʻ, gʻ in any apostrophe flavour
            out.append(_case(ch, "ў" if low == "o" else "ғ", _upper_word(text, i, 2)))
            i += 2
            continue
        if ch in APOSTROPHES:
            # sʼh separates s and h: Isʼhoq -> Исҳоқ, no ъ.
            if prev in {"s", "c"} and nxt.lower() == "h":
                i += 1
                continue
            out.append("ъ" if prev.isalpha() else ch)
            i += 1
            continue
        pair = (low + nxt.lower()) if nxt else ""
        after = text[i + 2] if i + 2 < n else ""
        if pair in LAT_DIGRAPHS and not (pair == "yo" and after in APOSTROPHES):  # yoʻl = y + oʻ
            res = LAT_DIGRAPHS[pair]
            out.append(_case(ch, res, _upper_word(text, i, 2) or nxt.isupper()))
            i += 2
            continue
        if low == "e":
            res = "э" if word_start or prev in VOWELS_LAT else "е"
        elif low in LAT_TO_CYR:
            res = LAT_TO_CYR[low]
        else:
            out.append(ch)
            i += 1
            continue
        out.append(_case(ch, res, _upper_word(text, i, 1)))
        i += 1
    return "".join(out)


def convert(text: str, to: str, ascii_apostrophe: bool = False) -> str:
    """Transliterates text, leaving URLs and e-mail addresses untouched."""
    fn = (lambda s: to_latin(s, ascii_apostrophe)) if to == "latn" else to_cyrillic
    parts, last = [], 0
    for m in SKIP.finditer(text):
        parts.append(fn(text[last:m.start()]))
        parts.append(m.group(0))
        last = m.end()
    parts.append(fn(text[last:]))
    return "".join(parts)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--to", choices=("latn", "cyrl"), required=True)
    p.add_argument("--ascii", action="store_true", help="write ' instead of ʻ and ʼ (Latin only)")
    p.add_argument("text", nargs="*")
    a = p.parse_args()
    text = " ".join(a.text) if a.text else sys.stdin.read()
    sys.stdout.write(convert(text, a.to, a.ascii))
    if a.text:
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
