import numpy as np
from preprocessing.normalizer import normalize

from app.model_loader import get_model, get_tokenizer, get_type

LABELS = ["negative", "neutral", "positive"]


def predict(reviews: list[str]) -> list[dict]:
    clean_texts = [normalize(t) for t in reviews]
    model_type = get_type()

    if model_type == "tfidf":
        return _predict_tfidf(clean_texts)
    elif model_type == "transformer":
        return _predict_transformer(clean_texts)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def _predict_tfidf(texts: list[str]) -> list[dict]:
    pipeline = get_model()
    proba = pipeline.predict_proba(texts)
    results = []
    for row in proba:
        idx = int(np.argmax(row))
        results.append(
            {
                "label": LABELS[idx],
                "confidence": round(float(row[idx]), 4),
            }
        )
    return results


def _predict_transformer(texts: list[str]) -> list[dict]:
    import torch

    model = get_model()
    tokenizer = get_tokenizer()
    device = next(model.parameters()).device
    results = []
    for text in texts:
        enc = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding="max_length",
        ).to(device)
        with torch.no_grad():
            logits = model(**enc).logits
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        idx = int(np.argmax(probs))
        results.append(
            {
                "label": LABELS[idx],
                "confidence": round(float(probs[idx]), 4),
            }
        )
    return results
