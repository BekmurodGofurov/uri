import json
import logging
import os

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_version = None
_type = None
_macro_f1 = None
_device = None

_ASPECTS = ["delivery", "quality", "price", "seller", "packaging", "other"]
_POLARITIES = ["negative", "neutral", "positive"]


class AspectMultiTaskModel:  # pragma: no cover -- needs torch/transformers
    """4-kun notebook'idagi arxitekturaning aynan nusxasi (import qilinadi)."""

    def __new__(cls, *args, **kwargs):
        import torch.nn as nn
        from transformers import AutoModel

        class _Impl(nn.Module):
            def __init__(self, model_name, n_aspects, n_polarity):
                super().__init__()
                self.backbone = AutoModel.from_pretrained(model_name)
                hidden = self.backbone.config.hidden_size
                self.dropout = nn.Dropout(0.1)
                self.presence_head = nn.Linear(hidden, n_aspects)
                self.polarity_head = nn.Linear(hidden, n_aspects * n_polarity)
                self.n_aspects = n_aspects
                self.n_polarity = n_polarity

            def forward(self, input_ids, attention_mask):
                out = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
                pooled = out.last_hidden_state[:, 0]
                pooled = self.dropout(pooled)
                presence_logits = self.presence_head(pooled)
                polarity_logits = self.polarity_head(pooled).view(
                    -1, self.n_aspects, self.n_polarity
                )
                return presence_logits, polarity_logits

        return _Impl(*args, **kwargs)


def _resolve_backbone_source(info: dict) -> str:
    """model_info.json'dagi backbone_source ba'zan faqat lokal papka nomi
    (masalan "pretrained_backbone") bo'lishi mumkin — bu HF Hub'da mavjud
    emas. Bunday holatda asl base_model'ga (haqiqiy HF repo id) qaytamiz."""
    backbone_source = info.get("backbone_source", info["base_model"])
    looks_like_hf_repo_or_path = "/" in backbone_source or os.path.exists(backbone_source)
    if not looks_like_hf_repo_or_path:
        return info["base_model"]
    return backbone_source


def load_model():
    global _model, _tokenizer, _version, _type, _macro_f1, _device

    _type = os.getenv("MODEL_TYPE", "keyword_stub")

    if _type == "keyword_stub":
        logger.info("Loading keyword-rule stub aspect model (no artifact needed).")
        _version = os.getenv("MODEL_VERSION", "aspect-stub-v0.1")
        _macro_f1 = float(os.getenv("MODEL_MACRO_F1", "0.0"))
        _model = "keyword_stub"
        logger.info("Stub aspect model ready.")

    elif _type == "multilabel":  # pragma: no cover -- needs torch + real model artifact
        import torch
        from transformers import AutoTokenizer

        model_dir = os.getenv("MODEL_PATH", "models/aspect_model_v1")
        info_path = os.path.join(model_dir, "model_info.json")
        hf_repo_id = os.getenv("HF_MODEL_REPO")  # masalan: "Jony-0009/isomiddinovs-model"

        # Model lokal diskda topilmasa (masalan yengil Docker image'da),
        # uni Hugging Face Hub'dan avtomatik tortib olamiz.
        if hf_repo_id and not os.path.exists(info_path):
            from huggingface_hub import snapshot_download

            logger.info(f"Model lokal topilmadi, Hugging Face'dan yuklanmoqda: {hf_repo_id}")
            snapshot_download(
                repo_id=hf_repo_id,
                local_dir=model_dir,
                token=os.getenv("HF_TOKEN"),  # faqat private repo bo'lsa kerak
            )

        with open(info_path, encoding="utf-8") as f:
            info = json.load(f)

        _version = info["model_version"]
        _macro_f1 = float(info["macro_f1"])
        backbone_source = _resolve_backbone_source(info)

        _device = "cuda" if torch.cuda.is_available() else "cpu"
        _tokenizer = AutoTokenizer.from_pretrained(model_dir)

        _model = AspectMultiTaskModel(backbone_source, len(_ASPECTS), len(_POLARITIES))
        state_dict = torch.load(os.path.join(model_dir, "pytorch_model.bin"), map_location=_device)
        _model.load_state_dict(state_dict)
        _model.to(_device)
        _model.eval()

        logger.info(f"Multilabel aspect model yuklandi: {_version} ({_device})")

    else:
        raise ValueError(f"Unsupported MODEL_TYPE: {_type}")


def get_model():
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return _model


def get_tokenizer():
    return _tokenizer


def get_device():
    return _device


def get_version() -> str:
    return _version or os.getenv("MODEL_VERSION", "aspect-stub-v0.1")


def get_type() -> str:
    return _type or os.getenv("MODEL_TYPE", "keyword_stub")


def get_macro_f1() -> float:
    return _macro_f1 if _macro_f1 is not None else 0.0


def get_aspects() -> list[str]:
    return _ASPECTS


def get_polarities() -> list[str]:
    return _POLARITIES
