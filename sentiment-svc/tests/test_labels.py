"""
Label mapping and split integrity tests.

These tests are split into two groups:
  - Pure unit tests (no file I/O) — always run in CI.
  - Data-file tests — skipped in CI when CSVs are absent (local/training only).
"""

import os
import sys

import pytest

# Ensure sentiment-svc root is in sys.path before importing from training
_sentiment_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _sentiment_dir not in sys.path:
    sys.path.insert(0, _sentiment_dir)

from training.prepare_data import rating_to_label  # noqa: E402

# ---------------------------------------------------------------------------
# Pure unit tests — no file I/O, always run in CI
# ---------------------------------------------------------------------------
VALID_LABELS = {"positive", "neutral", "negative"}


def test_rating_1_is_negative():
    assert rating_to_label(1) == "negative"


def test_rating_2_is_negative():
    assert rating_to_label(2) == "negative"


def test_rating_3_is_neutral():
    assert rating_to_label(3) == "neutral"


def test_rating_4_is_positive():
    assert rating_to_label(4) == "positive"


def test_rating_5_is_positive():
    assert rating_to_label(5) == "positive"


def test_textual_excellent_is_positive():
    assert rating_to_label("excellent") == "positive"


def test_textual_good_is_positive():
    assert rating_to_label("good") == "positive"


def test_textual_fair_is_neutral():
    assert rating_to_label("fair") == "neutral"


def test_textual_poor_is_negative():
    assert rating_to_label("poor") == "negative"


def test_textual_very_poor_is_negative():
    assert rating_to_label("very poor") == "negative"


def test_textual_case_and_whitespace_handling():
    assert rating_to_label("  EXCELLENT  ") == "positive"
    assert rating_to_label("Fair") == "neutral"
    assert rating_to_label(" POOR ") == "negative"


def test_string_numeric_ratings():
    assert rating_to_label("1") == "negative"
    assert rating_to_label("3") == "neutral"
    assert rating_to_label("5") == "positive"


def test_all_outputs_are_valid_labels():
    for r in [1, 2, 3, 4, 5]:
        assert rating_to_label(r) in VALID_LABELS


# ---------------------------------------------------------------------------
# Data-file tests — skipped in CI (local/training env only)
# ---------------------------------------------------------------------------
_DATA_DIR = os.path.join(_sentiment_dir, "data")


def _load(filename):
    import pandas as pd

    path = os.path.join(_DATA_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(
            f"{filename} not found — local-only test, not counted toward CI coverage. "
            "Run `make train` to generate data splits."
        )
    return pd.read_csv(path)


def test_train_labels_valid():
    df = _load("train.csv")
    bad = set(df["label"].unique()) - VALID_LABELS
    assert bad == set(), f"Invalid labels in train.csv: {bad}"


def test_val_labels_valid():
    df = _load("val.csv")
    bad = set(df["label"].unique()) - VALID_LABELS
    assert bad == set(), f"Invalid labels in val.csv: {bad}"


def test_no_missing_text():
    df = _load("train.csv")
    assert df["text"].isna().sum() == 0


def test_no_missing_labels():
    df = _load("train.csv")
    assert df["label"].isna().sum() == 0


def test_no_data_leakage():
    """Verify split independence: train and test are disjoint on unique texts."""
    import pandas as pd

    train = _load("train.csv")
    test = _load("test.csv")
    _load("val.csv")  # ensure val split also exists

    assert len(train) > 0 and len(test) > 0

    combined = pd.concat([train, test])
    counts = combined["text"].value_counts()
    single_occurrence = set(counts[counts == 1].index)

    train_singles = set(train["text"]) & single_occurrence
    test_singles = set(test["text"]) & single_occurrence
    overlap = train_singles & test_singles
    assert len(overlap) == 0, f"Unique reviews leaked across splits: {len(overlap)} rows"
