"""
Hash-based deterministic data split.
Ensures identical splits across platforms and datasets.

Usage:
  python training/split_data.py --input data/labelled.csv --output data/
"""

import argparse
import hashlib
import json
import os

import pandas as pd


def get_hash_bucket(val: str) -> int:
    """Returns an integer bucket 0..99 based on sha256 hash."""
    h = hashlib.sha256(str(val).encode("utf-8")).hexdigest()
    return int(h[:8], 16) % 100


def split(input_path: str, output_dir: str) -> None:
    df = pd.read_csv(input_path)
    required = {"text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    df = df.dropna(subset=["text", "label"])
    df = df[df["text"].str.strip() != ""]
    # Assign hash bucket 0-99 using review text
    df["bucket"] = df["text"].apply(get_hash_bucket)
    # 70% train (0..69), 15% val (70..84), 15% test (85..99)
    train = df[df["bucket"] < 70].drop(columns=["bucket"])
    val = df[(df["bucket"] >= 70) & (df["bucket"] < 85)].drop(columns=["bucket"])
    test = df[df["bucket"] >= 85].drop(columns=["bucket"])
    os.makedirs(output_dir, exist_ok=True)
    train.to_csv(os.path.join(output_dir, "train.csv"), index=False)
    val.to_csv(os.path.join(output_dir, "val.csv"), index=False)
    test.to_csv(os.path.join(output_dir, "test.csv"), index=False)
    manifest = {
        "hash_algorithm": "sha256",
        "split_ratios": "70/15/15",
        "total_rows": len(df),
        "train_rows": len(train),
        "val_rows": len(val),
        "test_rows": len(test),
        "train_label_distribution": train["label"].value_counts().to_dict(),
        "val_label_distribution": val["label"].value_counts().to_dict(),
        "test_label_distribution": test["label"].value_counts().to_dict(),
    }
    manifest_path = os.path.join(output_dir, "split_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Data split successfully: train={len(train)}, val={len(val)}, test={len(test)}")
    print(f"Manifest saved to: {manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    split(args.input, args.output)
