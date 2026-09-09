"""
aspect-svc — YAKUNIY, XOLIS baholash: 60 ta test_locked to'plamda.

MUHIM QOIDA (R5): bu skript FAQAT BIR MARTA ishga tushiriladi. Natija qanday
chiqishidan qat'i nazar (yaxshi yoki yomon), qaytib modelni yoki threshold'larni
"test'ga moslab" o'zgartirish TAQIQLANADI — bu test-set leakage bo'ladi va
butun baholashni haqiqiy bo'lmagan holga keltiradi.

Threshold'lar bu yerda QATTIQ YOZILGAN (dev to'plamda tuned qilingan qiymatlar),
bu skript ularni HECH QACHON qayta sozlamaydi.

Ishga tushirish (aspect-svc/ papkasidan):
    python training/evaluate_locked_test.py
"""

import json
import os
import sys

import torch
from sklearn.metrics import precision_recall_fscore_support

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.model_loader import AspectMultiTaskModel

ASPECTS = ["delivery", "quality", "price", "seller", "packaging", "other"]
POLARITIES = ["negative", "neutral", "positive"]

# Dev to'plamda tanlangan, QOTIRILGAN threshold'lar (train.py / notebook natijasidan).
# Bu yerda o'zgartirmang — o'zgartirish test-ga moslashtirish bo'ladi.
TUNED_THRESHOLDS = {
    "delivery": 0.20,
    "quality": 0.20,
    "price": 0.55,
    "seller": 0.30,
    "packaging": 0.55,
    "other": 0.60,
}

MODEL_DIR = "models/aspect_model_v1"
TEST_PATH = "splits/gold_test_LOCKED.jsonl"
TRAIN_PATH = "splits/gold_train.jsonl"
MAX_LEN = 128


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def presence_row(record, aspects):
    present = {a["aspect"] for a in record["aspects"]}
    return [1 if a in present else 0 for a in aspects]


def keyword_predict(text, aspects):
    keywords = {
        "delivery": ["yetkazib", "kuryer", "yetkazish", "kechik"],
        "quality": ["sifat", "ishlamay", "buzil", "mustahkam"],
        "price": ["narx", "qimmat", "arzon", "chegirma"],
        "seller": ["sotuvchi", "javob ber", "kafolat"],
        "packaging": ["qadoq", "quti", "yoril", "ezil"],
    }
    lowered = text.lower()
    pred, any_hit = [], False
    for a in aspects:
        if a == "other":
            continue
        hit = any(kw in lowered for kw in keywords.get(a, []))
        pred.append(1 if hit else 0)
        any_hit = any_hit or hit
    pred.append(0 if any_hit else 1)
    return pred


def main():
    if not os.path.exists(TEST_PATH):
        raise FileNotFoundError(
            f"{TEST_PATH} topilmadi. Avval `python training/train.py` ni ishga tushiring — "
            "u splits/gold_test_LOCKED.jsonl ni yaratadi."
        )

    print("=" * 70)
    print("DIQQAT: bu — yakuniy, bir martalik test baholash. Natija qanday")
    print("chiqishidan qat'i nazar, threshold yoki modelni qayta sozlamang.")
    print("=" * 70)

    test = load_jsonl(TEST_PATH)
    train = load_jsonl(TRAIN_PATH)
    print(f"\nTest (LOCKED): {len(test)} ta | Train (majority uchun): {len(train)} ta")

    # Majority baseline — faqat train statistikasidan (test'ga qaralmagan holda)
    y_train = [presence_row(r, ASPECTS) for r in train]
    majority = [1 if sum(col) > len(col) / 2 else 0 for col in zip(*y_train, strict=True)]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    with open(os.path.join(MODEL_DIR, "model_info.json"), encoding="utf-8") as f:
        info = json.load(f)
    backbone_source = info.get("backbone_source", info["base_model"])

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AspectMultiTaskModel(backbone_source, len(ASPECTS), len(POLARITIES))
    state_dict = torch.load(os.path.join(MODEL_DIR, "pytorch_model.bin"), map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    print(f"Model yuklandi: {info['model_version']} ({device})\n")

    y_true = [presence_row(r, ASPECTS) for r in test]
    y_pred_majority = [majority for _ in test]
    y_pred_keyword = [keyword_predict(r["text"], ASPECTS) for r in test]

    y_pred_model = []
    with torch.no_grad():
        for r in test:
            enc = tokenizer(
                r["text"],
                truncation=True,
                max_length=MAX_LEN,
                padding="max_length",
                return_tensors="pt",
            )
            input_ids = enc["input_ids"].to(device)
            attention_mask = enc["attention_mask"].to(device)
            presence_logits, _ = model(input_ids, attention_mask)
            probs = torch.sigmoid(presence_logits)[0].cpu().tolist()
            pred = [1 if probs[j] > TUNED_THRESHOLDS[a] else 0 for j, a in enumerate(ASPECTS)]
            y_pred_model.append(pred)

    def per_aspect_prf(y_true_mat, y_pred_mat):
        result = {}
        for j, aspect in enumerate(ASPECTS):
            yt = [row[j] for row in y_true_mat]
            yp = [row[j] for row in y_pred_mat]
            p, r, f1, _ = precision_recall_fscore_support(yt, yp, average="binary", zero_division=0)
            result[aspect] = {"precision": p, "recall": r, "f1": f1}
        return result

    results = {
        "majority": per_aspect_prf(y_true, y_pred_majority),
        "keyword": per_aspect_prf(y_true, y_pred_keyword),
        "model": per_aspect_prf(y_true, y_pred_model),
    }

    header = (
        f"{'Aspekt':12s} | {'Majority':>8s} | {'Keyword':>8s} | "
        f"{'Model P':>8s} | {'Model R':>8s} | {'Model F1':>9s}"
    )
    print(header)
    print("-" * 75)
    for aspect in ASPECTS:
        m = results["majority"][aspect]["f1"]
        k = results["keyword"][aspect]["f1"]
        mp = results["model"][aspect]["precision"]
        mr = results["model"][aspect]["recall"]
        mf = results["model"][aspect]["f1"]
        print(f"{aspect:12s} | {m:11.3f} | {k:10.3f} | {mp:8.3f} | {mr:8.3f} | {mf:9.3f}")

    macro_f1_model = sum(results["model"][a]["f1"] for a in ASPECTS) / len(ASPECTS)
    macro_f1_majority = sum(results["majority"][a]["f1"] for a in ASPECTS) / len(ASPECTS)
    macro_f1_keyword = sum(results["keyword"][a]["f1"] for a in ASPECTS) / len(ASPECTS)

    summary = (
        f"\nMacro-F1 — Majority: {macro_f1_majority:.3f} | "
        f"Keyword: {macro_f1_keyword:.3f} | Model: {macro_f1_model:.3f}"
    )
    print(summary)

    out = {
        "n_test": len(test),
        "thresholds_used": TUNED_THRESHOLDS,
        "per_aspect": results,
        "macro_f1": {
            "majority": macro_f1_majority,
            "keyword": macro_f1_keyword,
            "model": macro_f1_model,
        },
    }
    with open("locked_test_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n✅ Natija saqlandi: locked_test_results.json")
    print("Bu faylni EVALUATION.md'ga 'Yakuniy test natijasi' bo'limi sifatida qo'shing.")


if __name__ == "__main__":
    main()
