"""
Usage:
  python training/learning_curve.py --train data/train.csv --val data/val.csv
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from preprocessing.normalizer import normalize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline


def plot(train_path, val_path):
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    train_df["clean"] = train_df["text"].apply(normalize)
    val_df["clean"] = val_df["text"].apply(normalize)

    fractions = np.linspace(0.10, 1.0, 10)
    train_f1s, val_f1s = [], []

    for frac in fractions:
        subset = train_df.sample(frac=frac, random_state=42)
        pipe = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(ngram_range=(1, 2), max_features=100_000, sublinear_tf=True),
                ),
                ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", n_jobs=-1)),
            ]
        )
        pipe.fit(subset["clean"], subset["label"])

        train_f1s.append(f1_score(subset["label"], pipe.predict(subset["clean"]), average="macro"))
        val_f1s.append(f1_score(val_df["label"], pipe.predict(val_df["clean"]), average="macro"))
        print(f"  {int(frac * 100):3d}% → train={train_f1s[-1]:.3f}, val={val_f1s[-1]:.3f}")

    sizes = [int(f * len(train_df)) for f in fractions]
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, train_f1s, label="Train macro-F1", marker="o")
    plt.plot(sizes, val_f1s, label="Val macro-F1", marker="s")
    plt.xlabel("Training examples")
    plt.ylabel("Macro-F1")
    plt.title("Learning Curve — Sentiment")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("learning_curve.png", dpi=150)
    print("Saved: learning_curve.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--val", required=True)
    args = parser.parse_args()
    plot(args.train, args.val)
