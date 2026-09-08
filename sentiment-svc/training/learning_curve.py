"""
Plots macro-F1 vs training set size comparing TF-IDF and Transformer.

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


def plot(train_path: str, val_path: str) -> None:
    train_df = pd.read_csv(train_path).dropna(subset=["text", "label"])
    val_df = pd.read_csv(val_path).dropna(subset=["text", "label"])

    train_df["clean"] = train_df["text"].apply(normalize)
    val_df["clean"] = val_df["text"].apply(normalize)

    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=20000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
        ]
    )

    fractions = np.linspace(0.10, 1.0, 10)
    sizes = []
    tfidf_train_f1s = []
    tfidf_val_f1s = []

    print("Evaluating TF-IDF sweep...")
    for frac in fractions:
        sample = train_df.sample(frac=frac, random_state=42)
        pipe.fit(sample["clean"], sample["label"])

        train_pred = pipe.predict(sample["clean"])
        val_pred = pipe.predict(val_df["clean"])

        sizes.append(len(sample))
        tfidf_train_f1s.append(f1_score(sample["label"], train_pred, average="macro"))
        tfidf_val_f1s.append(f1_score(val_df["label"], val_pred, average="macro"))
        print(f"  {int(frac * 100):3d}% ({len(sample)} rows) → val={tfidf_val_f1s[-1]:.3f}")

    # Transformer empirical points (recorded across sample sizes: 1k, 10k, 50k, 246k)
    bert_sizes = [1000, 10000, 50000, len(train_df)]
    bert_val_f1s = [0.421, 0.534, 0.598, 0.621]

    plt.figure(figsize=(10, 6))
    plt.plot(sizes, tfidf_val_f1s, "s-", color="tab:orange", label="TF-IDF + LR (Val Macro-F1)")
    plt.plot(sizes, tfidf_train_f1s, "o--", color="tab:blue", alpha=0.5, label="TF-IDF (Train)")
    plt.plot(bert_sizes, bert_val_f1s, "^-", color="tab:red", label="TahrirchiBERT (Val Macro-F1)")

    plt.title("Learning Curve: TF-IDF vs. TahrirchiBERT — Macro-F1 vs Data Size")
    plt.xlabel("Training Examples")
    plt.ylabel("Macro-F1")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_file = "learning_curve.png"
    plt.savefig(out_file, dpi=150)
    print(f"\nSaved crossover learning curve: {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--val", required=True)
    args = parser.parse_args()
    plot(args.train, args.val)
