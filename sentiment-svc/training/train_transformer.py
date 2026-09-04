"""
Usage:
  python training/train_transformer.py --train data/train.csv --val data/val.csv --out models/bert_v1/
"""
import argparse
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from sklearn.metrics import f1_score
from preprocessing.normalizer import normalize

LABELS   = ["negative", "neutral", "positive"]
LABEL2ID = {lbl: i for i, lbl in enumerate(LABELS)}
ID2LABEL = {i: lbl for i, lbl in enumerate(LABELS)}
MODEL_NAME = "tahrirchi/tahrirchi-bert-small"


class ReviewDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer, max_len: int = 128):
        self.texts  = df["clean"].tolist()
        self.labels = [LABEL2ID[lbl] for lbl in df["label"].tolist()]
        self.tok    = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tok(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "label":          torch.tensor(self.labels[idx], dtype=torch.long),
        }


def train(train_path, val_path, out_path, epochs=3, batch_size=16, lr=2e-5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    train_df = pd.read_csv(train_path)
    val_df   = pd.read_csv(val_path)
    train_df["clean"] = train_df["text"].apply(normalize)
    val_df["clean"]   = val_df["text"].apply(normalize)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=3, id2label=ID2LABEL, label2id=LABEL2ID
    ).to(device)

    train_loader = DataLoader(ReviewDataset(train_df, tokenizer), batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(ReviewDataset(val_df,   tokenizer), batch_size=batch_size)

    optimizer   = torch.optim.AdamW(model.parameters(), lr=lr)
    total_steps = len(train_loader) * epochs
    scheduler   = get_linear_schedule_with_warmup(optimizer, total_steps // 10, total_steps)

    best_f1 = 0.0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            out  = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                labels=batch["label"].to(device),
            )
            optimizer.zero_grad()
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_loss += out.loss.item()

        model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in val_loader:
                logits = model(
                    input_ids=batch["input_ids"].to(device),
                    attention_mask=batch["attention_mask"].to(device),
                ).logits
                all_preds.extend(torch.argmax(logits, dim=1).cpu().numpy())
                all_labels.extend(batch["label"].numpy())

        macro_f1 = f1_score(all_labels, all_preds, average="macro")
        print(f"Epoch {epoch}/{epochs} | loss={total_loss/len(train_loader):.4f} | val macro-F1={macro_f1:.4f}")

        if macro_f1 > best_f1:
            best_f1 = macro_f1
            model.save_pretrained(out_path)
            tokenizer.save_pretrained(out_path)
            print(f"  ✅ Best model saved → {out_path}")

    print(f"\nBest val macro-F1: {best_f1:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train",  required=True)
    parser.add_argument("--val",    required=True)
    parser.add_argument("--out",    required=True)
    parser.add_argument("--epochs", type=int,   default=3)
    parser.add_argument("--batch",  type=int,   default=16)
    parser.add_argument("--lr",     type=float, default=2e-5)
    args = parser.parse_args()
    train(args.train, args.val, args.out, args.epochs, args.batch, args.lr)