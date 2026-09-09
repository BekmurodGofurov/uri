from models.model_loader import (
    get_aspects,
    get_device,
    get_model,
    get_polarities,
    get_tokenizer,
    get_type,
)

from shared.contracts import AspectHit

_KEYWORDS = {
    "delivery": ["yetkazib", "kuryer", "yetkazish", "kechik"],
    "quality": ["sifat", "ishlamay", "buzil", "mustahkam"],
    "price": ["narx", "qimmat", "arzon", "chegirma"],
    "seller": ["sotuvchi", "javob ber", "kafolat"],
    "packaging": ["qadoq", "quti", "yoril", "ezil"],
}

_NEGATIVE_MARKERS = [
    "yomon",
    "buzil",
    "kechik",
    "qimmat",
    "ishlamay",
    "yoril",
    "ezil",
    "javob ber",
]
_POSITIVE_MARKERS = ["zo'r", "yaxshi", "tez", "arzon", "mustahkam", "tavsiya", "yoqdi"]


def _guess_polarity(text: str) -> str:
    lowered = text.lower()
    neg = any(m in lowered for m in _NEGATIVE_MARKERS)
    pos = any(m in lowered for m in _POSITIVE_MARKERS)
    if neg and not pos:
        return "negative"
    if pos and not neg:
        return "positive"
    return "neutral"


def _predict_keyword_stub(texts: list[str]) -> list[list[AspectHit]]:
    all_hits: list[list[AspectHit]] = []
    for text in texts:
        lowered = text.lower()
        hits: list[AspectHit] = []
        for aspect, keywords in _KEYWORDS.items():
            if any(kw in lowered for kw in keywords):
                hits.append(
                    AspectHit(
                        aspect=aspect,  # type: ignore[arg-type]
                        polarity=_guess_polarity(text),  # type: ignore[arg-type]
                        confidence=0.55,
                    )
                )
        if not hits:
            hits.append(
                AspectHit(aspect="other", polarity=_guess_polarity(text), confidence=0.3)  # type: ignore[arg-type]
            )
        all_hits.append(hits)
    return all_hits


def _predict_multilabel(texts: list[str]) -> list[list[AspectHit]]:
    import torch

    model = get_model()
    tokenizer = get_tokenizer()
    device = get_device()
    aspects = get_aspects()
    polarities = get_polarities()

    all_hits: list[list[AspectHit]] = []
    with torch.no_grad():
        for text in texts:
            enc = tokenizer(
                text, truncation=True, max_length=128, padding="max_length",
                return_tensors="pt",
            )
            input_ids = enc["input_ids"].to(device)
            attention_mask = enc["attention_mask"].to(device)

            presence_logits, polarity_logits = model(input_ids, attention_mask)
            presence_probs = torch.sigmoid(presence_logits)[0]
            polarity_pred = torch.argmax(polarity_logits[0], dim=-1)

            hits: list[AspectHit] = []
            for j, aspect in enumerate(aspects):
                if presence_probs[j] > 0.5:
                    hits.append(
                        AspectHit(
                            aspect=aspect,  # type: ignore[arg-type]
                            polarity=polarities[polarity_pred[j].item()],  # type: ignore[arg-type]
                            confidence=round(presence_probs[j].item(), 3),
                        )
                    )
            if not hits:
                hits.append(
                    AspectHit(aspect="other", polarity="neutral", confidence=0.3)  # type: ignore[arg-type]
                )
            all_hits.append(hits)
    return all_hits


def predict(texts: list[str]) -> list[list[AspectHit]]:
    model_type = get_type()
    if model_type == "keyword_stub":
        return _predict_keyword_stub(texts)
    if model_type == "multilabel":
        return _predict_multilabel(texts)
    raise ValueError(f"Unknown model type: {model_type}")