import argparse
import json
import os
import random
import sys
from collections import Counter
from datetime import date

import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.model_loader import AspectMultiTaskModel

ASPECTS = ["delivery", "quality", "price", "seller", "packaging", "other"]
POLARITIES = ["negative", "neutral", "positive"]
KEYWORDS = {
    "delivery": ["yetkazib", "kuryer", "yetkazish", "kechik"],
    "quality": ["sifat", "ishlamay", "buzil", "mustahkam"],
    "price": ["narx", "qimmat", "arzon", "chegirma"],
    "seller": ["sotuvchi", "javob ber", "kafolat"],
    "packaging": ["qadoq", "quti", "yoril", "ezil"],
}


def load_jsonl(path):
    recs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def presence_matrix(records, aspects):
    mat = []
    for r in records:
        present = {a["aspect"] for a in r["aspects"]}
        mat.append([1 if a in present else 0 for a in aspects])
    return mat


def keyword_predict_presence(text, aspects):
    lowered = text.lower()
    pred, any_hit = [], False
    for a in aspects:
        if a == "other":
            continue
        hit = any(kw in lowered for kw in KEYWORDS.get(a, []))
        pred.append(1 if hit else 0)
        any_hit = any_hit or hit
    pred.append(0 if any_hit else 1)
    return pred


def build_targets(aspects_list, n_aspects, n_polarity):
    presence = torch.zeros(n_aspects)
    polarity = torch.full((n_aspects,), -100, dtype=torch.long)
    aspect_to_idx = {a: i for i, a in enumerate(ASPECTS)}
    pol_to_idx = {p: i for i, p in enumerate(POLARITIES)}
    for item in aspects_list:
        idx = aspect_to_idx[item["aspect"]]
        presence[idx] = 1.0
        polarity[idx] = pol_to_idx[item["polarity"]]
    return presence, polarity


class AspectDataset(Dataset):
    def __init__(self, records, tokenizer, max_len):
        self.records = records
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.records)

    def __getitem__(self, i):
        r = self.records[i]
        enc = self.tokenizer(
            r["text"],
            truncation=True,
            max_length=self.max_len,
            padding="max_length",
            return_tensors="pt",
        )
        presence, polarity = build_targets(r["aspects"], len(ASPECTS), len(POLARITIES))
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "presence": presence,
            "polarity": polarity,
            "weight": torch.tensor(r.get("weight", 1.0), dtype=torch.float),
        }


class SentimentDataset(Dataset):
    def __init__(self, df, tokenizer, max_len, label_to_idx):
        self.texts = df["text"].tolist()
        self.labels = df["label_str"].map(label_to_idx).tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, i):
        enc = self.tokenizer(
            self.texts[i],
            truncation=True,
            max_length=self.max_len,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label": torch.tensor(self.labels[i], dtype=torch.long),
        }


class SentimentClassifier(nn.Module):
    def __init__(self, model_name, n_labels):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)
        hidden = self.backbone.config.hidden_size
        self.dropout = nn.Dropout(0.1)
        self.head = nn.Linear(hidden, n_labels)

    def forward(self, input_ids, attention_mask):
        out = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        pooled = out.last_hidden_state[:, 0]
        return self.head(self.dropout(pooled))


def pretrain_backbone(sentiment_csv, model_name, max_len, device, epochs=2, seed=42):
    print(f"\n=== Oraliq isitish: {sentiment_csv} ===")
    sent_df = pd.read_csv(sentiment_csv)
    sentiment_map = {0: "neutral", 1: "positive", 2: "negative"}
    sent_df = sent_df.dropna(subset=["text", "sentiment"]).reset_index(drop=True)
    sent_df["text"] = sent_df["text"].astype(str)
    sent_df["label_str"] = sent_df["sentiment"].map(sentiment_map)
    assert sent_df["label_str"].isna().sum() == 0, "SENTIMENT_MAP to'liq emas"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    label_to_idx = {label: i for i, label in enumerate(["negative", "neutral", "positive"])}

    dataset = SentimentDataset(sent_df, tokenizer, max_len, label_to_idx)
    loader = DataLoader(
        dataset, batch_size=32, shuffle=True, generator=torch.Generator().manual_seed(seed)
    )

    model = SentimentClassifier(model_name, 3).to(device)
    optimizer = AdamW(model.parameters(), lr=2e-5)
    loss_fn = nn.CrossEntropyLoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            logits = model(input_ids, attention_mask)
            loss = loss_fn(logits, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"  isitish epoch {epoch + 1}/{epochs} - loss: {total_loss / len(loader):.4f}")

    backbone_dir = "pretrained_backbone"
    os.makedirs(backbone_dir, exist_ok=True)
    model.backbone.save_pretrained(backbone_dir)
    tokenizer.save_pretrained(backbone_dir)
    print(f"Isitilgan backbone saqlandi: {backbone_dir}/")
    return backbone_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold-path", default="gold_set.jsonl")
    parser.add_argument("--sentiment-csv", default=None, help="Ixtiyoriy: oraliq isitish uchun CSV")
    parser.add_argument("--model-name", default="tahrirchi/tahrirchi-bert-small")
    parser.add_argument("--output-dir", default="models/aspect_model_v1")
    parser.add_argument("--max-len", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--pretrain-epochs", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Qurilma: {device}")

    gold = load_jsonl(args.gold_path)
    assert len(gold) == 300, f"Kutilgan 300 ta emas, {len(gold)} ta topildi"
    random.Random(args.seed).shuffle(gold)

    test_locked = gold[:60]
    train_dev = gold[60:]
    train = train_dev[:200]
    dev = train_dev[200:]
    print(
        f"train: {len(train)} | dev: {len(dev)} | test (LOCKED, ishlatilmaydi): {len(test_locked)}"
    )

    os.makedirs("splits", exist_ok=True)
    for name, records in [
        ("gold_train", train),
        ("gold_dev", dev),
        ("gold_test_LOCKED", test_locked),
    ]:
        with open(f"splits/{name}.jsonl", "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    y_dev = presence_matrix(dev, ASPECTS)
    y_train = presence_matrix(train, ASPECTS)

    majority = [1 if sum(col) > len(col) / 2 else 0 for col in zip(*y_train, strict=True)]
    baseline_majority_f1, baseline_keyword_f1 = {}, {}
    for j, aspect in enumerate(ASPECTS):
        y_true = [row[j] for row in y_dev]
        baseline_majority_f1[aspect] = f1_score(
            y_true, [majority[j]] * len(y_true), zero_division=0
        )
        y_pred_kw = [keyword_predict_presence(r["text"], ASPECTS)[j] for r in dev]
        baseline_keyword_f1[aspect] = f1_score(y_true, y_pred_kw, zero_division=0)

    print("\n=== Baseline F1 (dev) ===")
    for aspect in ASPECTS:
        maj = baseline_majority_f1[aspect]
        kw = baseline_keyword_f1[aspect]
        print(f"  {aspect:12s}: majority={maj:.3f}  keyword={kw:.3f}")

    backbone_source = args.model_name
    if args.sentiment_csv:
        backbone_source = pretrain_backbone(
            args.sentiment_csv,
            args.model_name,
            args.max_len,
            device,
            epochs=args.pretrain_epochs,
            seed=args.seed,
        )
    else:
        print("\n(Oraliq isitish o'tkazib yuborildi - --sentiment-csv berilmadi)")

    tokenizer = AutoTokenizer.from_pretrained(backbone_source)
    combined_train = [{"text": r["text"], "aspects": r["aspects"], "weight": 1.0} for r in train]
    random.Random(args.seed).shuffle(combined_train)

    train_dataset = AspectDataset(combined_train, tokenizer, args.max_len)
    dev_dataset = AspectDataset(
        [{"text": r["text"], "aspects": r["aspects"], "weight": 1.0} for r in dev],
        tokenizer,
        args.max_len,
    )

    model = AspectMultiTaskModel(backbone_source, len(ASPECTS), len(POLARITIES)).to(device)

    aspect_counts = Counter()
    for r in combined_train:
        for a in {item["aspect"] for item in r["aspects"]}:
            aspect_counts[a] += 1
    n_total = len(combined_train)
    pos_weights = [
        min((n_total - max(aspect_counts[a], 1)) / max(aspect_counts[a], 1), 10.0) for a in ASPECTS
    ]
    pos_weight_tensor = torch.tensor(pos_weights, dtype=torch.float, device=device)
    print("\n=== pos_weight (class imbalance) ===")
    for a, w in zip(ASPECTS, pos_weights, strict=True):
        print(f"  {a:12s}: musbat={aspect_counts[a]}  vazn={w:.2f}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(args.seed),
    )
    optimizer = AdamW(model.parameters(), lr=args.lr)
    bce_loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor, reduction="none")
    ce_loss_fn = nn.CrossEntropyLoss(ignore_index=-100, reduction="none")

    model.train()
    for epoch in range(args.epochs):
        total_loss = 0.0
        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            presence_target = batch["presence"].to(device)
            polarity_target = batch["polarity"].to(device)
            weight = batch["weight"].to(device)

            presence_logits, polarity_logits = model(input_ids, attention_mask)
            presence_loss = bce_loss_fn(presence_logits, presence_target)
            presence_loss = (presence_loss.mean(dim=1) * weight).mean()

            polarity_loss = ce_loss_fn(
                polarity_logits.view(-1, len(POLARITIES)), polarity_target.view(-1)
            )
            valid_mask = (polarity_target.view(-1) != -100).float()
            polarity_loss = (
                (polarity_loss * valid_mask).sum() / valid_mask.sum()
                if valid_mask.sum() > 0
                else torch.tensor(0.0, device=device)
            )

            loss = presence_loss + polarity_loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(
            f"Epoch {epoch + 1}/{args.epochs} - o'rtacha loss: {total_loss / len(train_loader):.4f}"
        )

    dev_loader = DataLoader(dev_dataset, batch_size=args.batch_size, shuffle=False)
    model.eval()
    all_presence_prob, all_presence_true = [], []
    with torch.no_grad():
        for batch in dev_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            presence_logits, _ = model(input_ids, attention_mask)
            probs = torch.sigmoid(presence_logits).cpu().numpy()
            all_presence_prob.extend(probs.tolist())
            all_presence_true.extend(batch["presence"].int().numpy().tolist())

    print("\n=== Har bir aspekt uchun eng yaxshi threshold (dev) ===")
    model_f1 = {}
    for j, aspect in enumerate(ASPECTS):
        y_true = [row[j] for row in all_presence_true]
        y_prob = [row[j] for row in all_presence_prob]
        best_f1, best_t = 0.0, 0.5
        for t in [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]:
            y_pred = [1 if p > t else 0 for p in y_prob]
            f1 = f1_score(y_true, y_pred, zero_division=0)
            if f1 > best_f1:
                best_f1, best_t = f1, t
        model_f1[aspect] = best_f1
        print(f"  {aspect:12s}: best_threshold={best_t:.2f}  F1={best_f1:.3f}")

    macro_f1 = sum(model_f1.values()) / len(model_f1)
    print(f"\nMacro-F1 (dev, tuned thresholds): {macro_f1:.3f}")

    print("\n=== Yakuniy solishtiruv ===")
    comparison = pd.DataFrame(
        {
            "Aspekt": ASPECTS,
            "Majority": [round(baseline_majority_f1[a], 3) for a in ASPECTS],
            "Keyword": [round(baseline_keyword_f1[a], 3) for a in ASPECTS],
            "Model": [round(model_f1[a], 3) for a in ASPECTS],
        }
    )
    print(comparison.to_string(index=False))

    os.makedirs(args.output_dir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(args.output_dir, "pytorch_model.bin"))
    tokenizer.save_pretrained(args.output_dir)

    model_info = {
        "model_version": "aspect-multilabel-v1",
        "model_type": "multilabel",
        "trained_on": str(date.today()),
        "macro_f1": round(macro_f1, 4),
        "aspects": ASPECTS,
        "base_model": args.model_name,
        "backbone_source": backbone_source,
        "train_size": len(combined_train),
        "seed": args.seed,
    }
    with open(os.path.join(args.output_dir, "model_info.json"), "w", encoding="utf-8") as f:
        json.dump(model_info, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Model saqlandi: {args.output_dir}/")
    print(json.dumps(model_info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
