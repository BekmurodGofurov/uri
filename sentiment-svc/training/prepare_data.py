"""Data preparation: download dataset and map 1-5 ratings to 3 sentiment classes."""

import os

import pandas as pd
from datasets import load_dataset


def rating_to_label(rating) -> str:
    """Map 1-5 ratings or textual labels to 3 sentiment classes."""
    if isinstance(rating, str):
        cleaned = rating.strip().lower()
        textual = {
            "excellent": "positive",
            "good": "positive",
            "fair": "neutral",
            "poor": "negative",
            "very poor": "negative",
        }
        if cleaned in textual:
            return textual[cleaned]
        # If it's a numeric string like "1", "2", "3", etc.
        try:
            rating = int(cleaned)
        except ValueError as err:
            raise ValueError(f"Unknown rating value: {rating}") from err

    r = int(rating)
    if r <= 2:
        return "negative"
    elif r == 3:
        return "neutral"
    else:
        return "positive"


def main():
    os.makedirs("data", exist_ok=True)
    print("Downloading risqaliyevds/uzbek-sentiment-analysis from Hugging Face...")
    ds = load_dataset("risqaliyevds/uzbek-sentiment-analysis")
    df = pd.DataFrame(ds["train"])

    print(f"Total downloaded rows: {len(df)}")
    print("Raw rating distribution:")
    print(df["rating"].value_counts())

    df["label"] = df["rating"].apply(rating_to_label)
    df = df.rename(columns={"normalized_review_text": "text"})
    df = df[["text", "label"]].dropna()

    out_path = "data/labelled.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved labelled data to {out_path} ({len(df)} rows)")
    print("Mapped label distribution:")
    print(df["label"].value_counts(normalize=True))


if __name__ == "__main__":
    main()
