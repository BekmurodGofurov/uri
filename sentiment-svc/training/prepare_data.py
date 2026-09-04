"""
Downloads the HuggingFace dataset and converts ratings to sentiment labels.

Usage:
  pip install datasets
  python training/prepare_data.py
"""
import os
from datasets import load_dataset


def rating_to_label(rating) -> str:
    if isinstance(rating, str):
        textual_labels = {
            "excellent": "positive",
            "good": "positive",
            "fair": "neutral",
            "poor": "negative",
            "very poor": "negative",
        }
        normalized_rating = rating.strip().lower()
        if normalized_rating in textual_labels:
            return textual_labels[normalized_rating]

    r = int(rating)
    if r <= 2:
        return "negative"
    elif r == 3:
        return "neutral"
    else:
        return "positive"


def main():
    os.makedirs("data", exist_ok=True)

    print("Downloading dataset from HuggingFace...")
    ds = load_dataset("risqaliyevds/uzbek-sentiment-analysis")
    df = ds["train"].to_pandas()

    print(f"Columns: {df.columns.tolist()}")
    print(f"Rows: {len(df)}")
    print(f"Rating value counts:\n{df['rating'].value_counts().sort_index()}")

    df["label"] = df["rating"].apply(rating_to_label)
    df = df.rename(columns={"normalized_review_text": "text"})
    df = df[["text", "label"]]

    df.to_csv("data/labelled.csv", index=False)
    print(f"\nLabel distribution:\n{df['label'].value_counts()}")
    print("\nSaved: data/labelled.csv")


if __name__ == "__main__":
    main()