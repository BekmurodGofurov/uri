"""
Usage:
  python training/split_data.py --input data/labelled.csv --output data/
"""

import argparse

import pandas as pd
from sklearn.model_selection import train_test_split


def split(input_path: str, output_dir: str, seed: int = 42) -> None:
    df = pd.read_csv(input_path)

    required = {"text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")

    valid_labels = {"positive", "neutral", "negative"}
    bad = set(df["label"].unique()) - valid_labels
    if bad:
        raise ValueError(f"Unknown labels: {bad}")

    df = df.dropna(subset=["text", "label"])
    df = df[df["text"].str.strip() != ""]

    print(f"Total rows: {len(df)}")
    print(df["label"].value_counts())

    train, temp = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=seed)
    val, test = train_test_split(temp, test_size=0.50, stratify=temp["label"], random_state=seed)

    train.to_csv(f"{output_dir}/train.csv", index=False)
    val.to_csv(f"{output_dir}/val.csv", index=False)
    test.to_csv(f"{output_dir}/test.csv", index=False)

    print(f"\ntrain={len(train)}, val={len(val)}, test={len(test)}")
    print("⚠️  Lock test.csv — do NOT use it until Day 6!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    split(args.input, args.output, args.seed)
