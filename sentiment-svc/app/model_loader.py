import os
import joblib
import logging

logger = logging.getLogger(__name__)

_model     = None
_tokenizer = None
_version   = None
_type      = None

def load_model():
    global _model, _tokenizer, _version, _type
    model_path = os.getenv("MODEL_PATH",    "models/tfidf_v1.joblib")
    _version   = os.getenv("MODEL_VERSION", "sentiment-v1")
    _type      = os.getenv("MODEL_TYPE",    "tfidf")
    if _type == "tfidf":
        logger.info(f"Loading TF-IDF model from {model_path}")
        _model = joblib.load(model_path)
        logger.info("TF-IDF model loaded.")
    elif _type == "transformer":
        from transformers import AutoTokenizer, AutoModelForSequenceClassification  # noqa: PLC0415
        logger.info(f"Loading transformer model from {model_path}")
        _tokenizer = AutoTokenizer.from_pretrained(model_path)
        _model     = AutoModelForSequenceClassification.from_pretrained(model_path)
        _model.eval()
        logger.info("Transformer model loaded.")
    else:
        raise ValueError(f"Unsupported MODEL_TYPE: {_type}")
def get_model():
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    return _model


def get_tokenizer():
    return _tokenizer


def get_version() -> str:
    return _version or os.getenv("MODEL_VERSION", "sentiment-v1")


def get_type() -> str:
    return _type or os.getenv("MODEL_TYPE", "tfidf")