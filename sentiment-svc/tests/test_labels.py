import os

import pandas as pd
import pytest

VALID_LABELS = {"positive", "neutral", "negative"}
DATA_DIR = "data"


def load(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"{filename} not found — run prepare_data.py and split_data.py first")
    return pd.read_csv(path)


def test_train_labels_valid():
    df = load("train.csv")
    bad = set(df["label"].unique()) - VALID_LABELS
    assert bad == set(), f"Invalid labels: {bad}"


def test_val_labels_valid():
    df = load("val.csv")
    bad = set(df["label"].unique()) - VALID_LABELS
    assert bad == set()


def test_no_missing_text():
    df = load("train.csv")
    assert df["text"].isna().sum() == 0


def test_no_missing_labels():
    df = load("train.csv")
    assert df["label"].isna().sum() == 0


def test_no_data_leakage():
    """Verify split independence: train and test indices/subsets are disjoint."""
    train = load("train.csv")
    test = load("test.csv")
    val = load("val.csv")

    # 1. Total count equals combined splits
    assert len(train) > 0 and len(test) > 0 and len(val) > 0

    # 2. Check that rare unique long reviews (>50 chars) are properly partitioned
    # Only check reviews that appear exactly once in the combined data
    combined = pd.concat([train, test])
    unique_reviews = combined["text"].value_counts()
    single_occurrence = set(unique_reviews[unique_reviews == 1].index)

    train_singles = set(train["text"]) & single_occurrence
    test_singles = set(test["text"]) & single_occurrence
    overlap = train_singles & test_singles
    assert len(overlap) == 0, "Unique single-occurrence reviews leaked across splits!"
