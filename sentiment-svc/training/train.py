"""
Master training entry point.
Runs data preparation, hash split, TF-IDF training, evaluation, and learning curve in one command.

Usage:
  python training/train.py
"""

import os
import subprocess
import sys

_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["PYTHONPATH"] = _dir


def run_cmd(cmd: list[str]) -> None:
    print(f"\n>>> Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=_dir)  # noqa: S603


def main():
    print("=== Uzum Sentiment Service — End-to-End Pipeline ===")

    # 1. Prepare data
    run_cmd([sys.executable, "training/prepare_data.py"])

    # 2. Hash-based data split
    run_cmd(
        [
            sys.executable,
            "training/split_data.py",
            "--input",
            "data/labelled.csv",
            "--output",
            "data/",
        ]
    )

    # 3. Train TF-IDF baseline
    run_cmd(
        [
            sys.executable,
            "training/train_tfidf.py",
            "--train",
            "data/train.csv",
            "--val",
            "data/val.csv",
            "--out",
            "models/tfidf_v1.joblib",
        ]
    )

    # 4. Evaluate on test set
    run_cmd(
        [
            sys.executable,
            "training/evaluate.py",
            "--model",
            "models/tfidf_v1.joblib",
            "--type",
            "tfidf",
            "--test",
            "data/test.csv",
        ]
    )

    # 5. Generate learning curve
    run_cmd(
        [
            sys.executable,
            "training/learning_curve.py",
            "--train",
            "data/train.csv",
            "--val",
            "data/val.csv",
        ]
    )

    print("\n✅ Entire ML Pipeline successfully completed with fixed seed!")


if __name__ == "__main__":
    main()
