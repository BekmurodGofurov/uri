"""
Usage:
  python training/train_tfidf.py --train data/train.csv \
    --val data/val.csv --out models/tfidf_v1.joblib
"""

import argparse

import joblib
import pandas as pd
from preprocessing.normalizer import normalize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.pipeline import Pipeline


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["clean"] = df["text"].apply(normalize)
    return df


def train(train_path: str, val_path: str, out_path: str) -> float:
    train_df = load(train_path)
    val_df = load(val_path)

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=100_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    C=1.0,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    print("Training...")
    pipeline.fit(train_df["clean"], train_df["label"])

    preds = pipeline.predict(val_df["clean"])
    macro_f1 = f1_score(val_df["label"], preds, average="macro")

    print(classification_report(val_df["label"], preds))
    print(f"Val Macro-F1: {macro_f1:.4f}")

    joblib.dump(pipeline, out_path)
    print(f"Saved: {out_path}")
    return macro_f1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--val", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    train(args.train, args.val, args.out)
