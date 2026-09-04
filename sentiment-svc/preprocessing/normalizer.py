import re
import unicodedata

_CYR_TO_LAT: dict[str, str] = {
    "а": "a",  "б": "b",  "в": "v",  "г": "g",  "д": "d",
    "е": "ye", "ё": "yo", "ж": "j",  "з": "z",  "и": "i",
    "й": "y",  "к": "k",  "л": "l",  "м": "m",  "н": "n",
    "о": "o",  "п": "p",  "р": "r",  "с": "s",  "т": "t",
    "у": "u",  "ф": "f",  "х": "x",  "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "sh", "ъ": "'",  "ы": "i",  "ь": "",
    "э": "e",  "ю": "yu", "я": "ya",
    "ў": "o'", "қ": "q",  "ғ": "g'", "ҳ": "h",  "нг": "ng",
}

def _cyr_to_lat(text: str) -> str:
    result = []
    i = 0
    while i < len(text):
        two = text[i : i + 2].lower()
        if two in _CYR_TO_LAT:
            result.append(_CYR_TO_LAT[two])
            i += 2
        else:
            ch = text[i].lower()
            result.append(_CYR_TO_LAT.get(ch, text[i]))
            i += 1
    return "".join(result)


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = _cyr_to_lat(text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\+?998[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", " ", text)
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_batch(texts: list[str]) -> list[str]:
    return [normalize(t) for t in texts]