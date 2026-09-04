"""
⚠️  Run ONLY on Day 6. Do NOT touch test.csv before then.

Usage (tfidf):
  python training/evaluate.py --model models/tfidf_v1.joblib --test data/test.csv --type tfidf

Usage (transformer):
  python training/evaluate.py --model models/bert_v1/ --test data/test.csv --type transformer
"""
import argparse
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, f1_score, confusion_matrix
from preprocessing.normalizer import normalize


def evaluate_tfidf(model_path, test_df):
    pipeline = joblib.load(model_path)
    preds    = pipeline.predict(test_df["clean"])
    return preds


def evaluate_transformer(model_path, test_df):
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    LABELS = ["negative", "neutral", "positive"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tok    = AutoTokenizer.from_pretrained(model_path)
    model  = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    model.eval()

    preds = []
    for text in test_df["clean"].tolist():
        enc = tok(text, return_tensors="pt", truncation=True, max_length=128, padding="max_length").to(device)
        with torch.no_grad():
            logits = model(**enc).logits
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        preds.append(LABELS[int(np.argmax(probs))])
    return preds


def run(model_path, test_path, model_type):
    test_df = pd.read_csv(test_path)
    test_df["clean"] = test_df["text"].apply(normalize)

    if model_type == "tfidf":
        preds = evaluate_tfidf(model_path, test_df)
    else:
        preds = evaluate_transformer(model_path, test_df)

    labels   = test_df["label"].tolist()
    macro_f1 = f1_score(labels, preds, average="macro")

    print("=" * 50)
    print("FINAL TEST RESULTS")
    print("=" * 50)
    print(classification_report(labels, preds, target_names=["negative", "neutral", "positive"]))
    print(f"Macro-F1: {macro_f1:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(labels, preds))

    print("\n--- 3 Interesting Misclassifications ---")
    errors = [(i, test_df["text"].iloc[i], labels[i], preds[i])
              for i in range(len(preds)) if preds[i] != labels[i]]
    for k, (_, text, true, pred) in enumerate(errors[:3]):
        print(f"\n[{k+1}] Text:      {text}")
        print(f"      True:      {true}")
        print(f"      Predicted: {pred}")

    with open("evaluation_result.json", "w") as f:
        json.dump({"macro_f1": round(macro_f1, 4), "model_type": model_type}, f, indent=2)
    print("\nSaved: evaluation_result.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--test",  required=True)
    parser.add_argument("--type",  required=True, choices=["tfidf", "transformer"])
    args = parser.parse_args()
    run(args.model, args.test, args.type)