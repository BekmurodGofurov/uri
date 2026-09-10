from models.model_loader import (
    _resolve_backbone_source,
    get_aspects,
    get_polarities,
)


def test_resolve_backbone_source_prefers_hf_repo_id():
    info = {"backbone_source": "some-org/some-model", "base_model": "base/model"}
    assert _resolve_backbone_source(info) == "some-org/some-model"


def test_resolve_backbone_source_falls_back_for_local_only_name():
    # "pretrained_backbone" has no "/" and doesn't exist on disk in CI,
    # so it isn't a valid HF repo id or local path -> fall back to base_model.
    info = {"backbone_source": "pretrained_backbone", "base_model": "org/base-model"}
    assert _resolve_backbone_source(info) == "org/base-model"


def test_resolve_backbone_source_defaults_to_base_model_when_missing():
    info = {"base_model": "org/base-model"}
    assert _resolve_backbone_source(info) == "org/base-model"


def test_get_aspects_matches_contract():
    aspects = get_aspects()
    assert set(aspects) == {"delivery", "quality", "price", "seller", "packaging", "other"}


def test_get_polarities_matches_contract():
    assert set(get_polarities()) == {"negative", "neutral", "positive"}
