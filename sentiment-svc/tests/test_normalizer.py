import pytest
from preprocessing.normalizer import normalize


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


def test_apostrophe_kept():
    assert "o'" in normalize("o'zbek")
