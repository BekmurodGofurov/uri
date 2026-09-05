import logging
import os

logger = logging.getLogger(__name__)

_model = None
_version = None
_type = None
_macro_f1 = None

_ASPECTS = ["delivery", "quality", "price", "seller", "packaging", "other"]


def load_model():
    global _model, _version, _type, _macro_f1

    _version = os.getenv("MODEL_VERSION", "aspect-stub-v0.1")
    _type = os.getenv("MODEL_TYPE", "keyword_stub")
    _macro_f1 = float(os.getenv("MODEL_MACRO_F1", "0.0"))

    if _type == "keyword_stub":
        logger.info("Loading keyword-rule stub aspect model (no artifact needed).")
        _model = "keyword_stub"  # placeholder — haqiqiy modelga o'tganda joblib/torch obyekti bo'ladi
        logger.info("Stub aspect model ready.")
    elif _type == "multilabel":
        # TODO (4-kun): haqiqiy multi-label klassifikatorni shu yerda yuklang.
        # Masalan:
        #   import joblib
        #   _model = joblib.load(os.getenv("MODEL_PATH", "models/aspect_v1.joblib"))
        raise NotImplementedError("multilabel model loader hali yozilmagan (4-kun ishi)")
    else:
        raise ValueError(f"Unsupported MODEL_TYPE: {_type}")


def get_model():
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return _model


def get_version() -> str:
    return _version or os.getenv("MODEL_VERSION", "aspect-stub-v0.1")


def get_type() -> str:
    return _type or os.getenv("MODEL_TYPE", "keyword_stub")


def get_macro_f1() -> float:
    return _macro_f1 if _macro_f1 is not None else 0.0


def get_aspects() -> list[str]:
    return _ASPECTS