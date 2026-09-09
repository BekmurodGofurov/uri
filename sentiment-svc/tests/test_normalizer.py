# ruff: noqa: RUF001, RUF003
import os
import sys

_sentiment_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _sentiment_dir not in sys.path:
    sys.path.insert(0, _sentiment_dir)

import pytest  # noqa: E402
from preprocessing.normalizer import normalize, normalize_batch  # noqa: E402


def test_basic_latin():
    assert normalize("yaxshi mahsulot") == "yaxshi mahsulot"


def test_lowercase():
    assert normalize("YAXSHI") == "yaxshi"


def test_url_removed():
    assert "https" not in normalize("Ko'ring: https://uzum.uz/123")


def test_phone_removed():
    assert "998" not in normalize("Aloqa: +998 90 123-45-67")


def test_emoji_stripped():
    assert "😊" not in normalize("Yaxshi 😊")


def test_whitespace_collapsed():
    assert normalize("a   b") == "a b"


def test_empty_string():
    assert normalize("") == ""


def test_non_string_raises():
    with pytest.raises(TypeError):
        normalize(123)  # type: ignore


def test_only_special_chars():
    assert normalize("!!! @@@") == ""


# === SPEC REQUIREMENT: Test all 4 apostrophe encodings ===
def test_apostrophe_variants():
    # 1. ASCII standard apostrophe (') - 0x27
    assert normalize("o'zbek") == "o'zbek"

    # 2. Modifier letter turned comma (ʻ) - \u02bb (official Uzbek Latin)
    assert normalize("oʻzbek") == "o'zbek"

    # 3. Right single quotation mark (’) - \u2019 (common from mobile keyboards)
    assert normalize("o’zbek") == "o'zbek"

    # 4. Grave accent / backtick (`) - 0x60
    assert normalize("o`zbek") == "o'zbek"

    # Bonus: Modifier letter apostrophe (ʼ) - \u02bc
    assert normalize("oʼzbek") == "o'zbek"

    # Combined check for g'
    assert normalize("gʻoya") == "g'oya"
    assert normalize("g`oya") == "g'oya"
    assert normalize("g’oya") == "g'oya"


# === SPEC REQUIREMENT: Cyrillic to Latin transliteration ===
def test_cyrillic_transliteration():
    assert normalize("яхши") == "yaxshi"
    assert normalize("ўзбек") == "o'zbek"
    assert normalize("ғоя") == "g'oya"
    assert normalize("қўлланма") == "qo'llanma"


def test_normalize_batch():
    inputs = ["Yaxshi mahsulot!", "TAVSIYA QILAMAN"]
    expected = ["yaxshi mahsulot", "tavsiya qilaman"]
    assert normalize_batch(inputs) == expected
