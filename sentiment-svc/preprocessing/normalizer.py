# ruff: noqa: RUF001
import re
import unicodedata

_VOWELS = set("аеёиоуэюяўaouie")

_CYR_TO_LAT: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "ё": "yo",
    "ж": "j",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "x",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sh",
    "ъ": "'",
    "ы": "i",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    "ў": "o'",
    "қ": "q",
    "ғ": "g'",
    "ҳ": "h",
    "нг": "ng",
}


def _cyr_to_lat(text: str) -> str:
    result = []
    i = 0
    while i < len(text):
        ch = text[i].lower()
        if ch == "е":
            # Word-initial or after vowel/space -> 'ye', after consonant -> 'e'
            if i == 0 or text[i - 1].isspace() or text[i - 1].lower() in _VOWELS:
                result.append("ye")
            else:
                result.append("e")
            i += 1
        elif text[i : i + 2].lower() in _CYR_TO_LAT:
            result.append(_CYR_TO_LAT[text[i : i + 2].lower()])
            i += 2
        else:
            result.append(_CYR_TO_LAT.get(ch, text[i]))
            i += 1
    return "".join(result)


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    # Unify all apostrophe variants into standard ASCII apostrophe (')
    text = re.sub(r"[`ʻʼ'ʽ’]", "'", text)
    text = _cyr_to_lat(text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\+?998[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", " ", text)
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_batch(texts: list[str]) -> list[str]:
    return [normalize(t) for t in texts]


def test_normalize_batch():
    inputs = ["Yaxshi mahsulot!", "TAVSIYA QILAMAN"]
    expected = ["yaxshi mahsulot", "tavsiya qilaman"]
    assert normalize_batch(inputs) == expected
