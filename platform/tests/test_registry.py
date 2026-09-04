"""
platform/tests/test_registry.py
────────────────────────────────
Tests for the model registry (platform/registry/manager.py).

Covers the requirement from §7:
  "a test that the rollback command actually rolls back"

All tests use a temporary directory (pytest's tmp_path) so nothing
is written to the real model_registry/ on disk.
"""

from __future__ import annotations

from pathlib import Path
from platform.registry.manager import ModelRegistry, RegistryError

import pytest

# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def registry(tmp_path: Path) -> ModelRegistry:
    """A fresh registry rooted in a pytest-managed temp directory."""
    return ModelRegistry(root=tmp_path / "registry")


@pytest.fixture
def dummy_artifact(tmp_path: Path) -> Path:
    """A tiny fake model file."""
    f = tmp_path / "model_v1.joblib"
    f.write_bytes(b"fake-model-bytes-v1")
    return f


@pytest.fixture
def dummy_artifact_v2(tmp_path: Path) -> Path:
    """A second fake model file for the v2 version."""
    f = tmp_path / "model_v2.joblib"
    f.write_bytes(b"fake-model-bytes-v2")
    return f


# ── basic registration ─────────────────────────────────────────────────────────


def test_register_creates_version_dir(registry: ModelRegistry, dummy_artifact: Path):
    registry.register(
        version="sentiment-v1",
        service="sentiment-svc",
        model_type="tfidf",
        artifact_src=dummy_artifact,
        headline_metric="macro-f1: 0.63",
    )
    assert (registry.root / "sentiment-v1").is_dir()
    assert (registry.root / "sentiment-v1" / "meta.json").exists()


def test_register_copies_artifact(registry: ModelRegistry, dummy_artifact: Path):
    registry.register("sentiment-v1", "sentiment-svc", "tfidf", dummy_artifact)
    stored = registry.artifact_path("sentiment-v1")
    assert stored.read_bytes() == b"fake-model-bytes-v1"


def test_register_sets_current_by_default(registry: ModelRegistry, dummy_artifact: Path):
    assert registry.current() is None
    registry.register("sentiment-v1", "sentiment-svc", "tfidf", dummy_artifact)
    assert registry.current() == "sentiment-v1"


def test_register_no_current_flag(registry: ModelRegistry, dummy_artifact: Path):
    registry.register(
        "sentiment-v1", "sentiment-svc", "tfidf", dummy_artifact, set_current=False
    )
    assert registry.current() is None


def test_register_duplicate_version_raises(registry: ModelRegistry, dummy_artifact: Path):
    registry.register("sentiment-v1", "sentiment-svc", "tfidf", dummy_artifact)
    with pytest.raises(RegistryError, match="already exists"):
        registry.register("sentiment-v1", "sentiment-svc", "tfidf", dummy_artifact)


def test_register_missing_artifact_raises(registry: ModelRegistry, tmp_path: Path):
    with pytest.raises(RegistryError, match="Artifact not found"):
        registry.register("v1", "svc", "tfidf", tmp_path / "nonexistent.joblib")


# ── metadata ──────────────────────────────────────────────────────────────────


def test_meta_fields(registry: ModelRegistry, dummy_artifact: Path):
    registry.register(
        version="sentiment-v1",
        service="sentiment-svc",
        model_type="tfidf",
        artifact_src=dummy_artifact,
        headline_metric="macro-f1: 0.63",
        notes="baseline TF-IDF",
    )
    meta = registry.get_meta("sentiment-v1")
    assert meta["version"] == "sentiment-v1"
    assert meta["service"] == "sentiment-svc"
    assert meta["model_type"] == "tfidf"
    assert meta["headline_metric"] == "macro-f1: 0.63"
    assert meta["notes"] == "baseline TF-IDF"
    assert "registered_at" in meta
    assert "artifact_path" in meta


def test_get_meta_missing_version_raises(registry: ModelRegistry):
    with pytest.raises(RegistryError):
        registry.get_meta("nonexistent-v99")


# ── list versions ─────────────────────────────────────────────────────────────


def test_list_versions_empty(registry: ModelRegistry):
    assert registry.list_versions() == []


def test_list_versions_sorted_by_registration_time(
    registry: ModelRegistry, dummy_artifact: Path, dummy_artifact_v2: Path
):
    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)
    registry.register("sentiment-v2", "svc", "tfidf", dummy_artifact_v2)
    versions = registry.list_versions()
    assert versions == ["sentiment-v1", "sentiment-v2"]


# ── rollback ──────────────────────────────────────────────────────────────────
# This block satisfies the requirement:
#   "a test that the rollback command actually rolls back"


def test_rollback_changes_current_pointer(
    registry: ModelRegistry, dummy_artifact: Path, dummy_artifact_v2: Path
):
    """
    Core rollback test (§7 acceptance criterion).

    1. Register v1 → current becomes v1
    2. Register v2 → current becomes v2
    3. rollback("sentiment-v1") → current must return to v1
    """
    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)
    assert registry.current() == "sentiment-v1"

    registry.register("sentiment-v2", "svc", "tfidf", dummy_artifact_v2)
    assert registry.current() == "sentiment-v2"

    # ── THE ROLLBACK ──
    registry.rollback("sentiment-v1")

    # After rollback the pointer must point to v1, not v2
    assert registry.current() == "sentiment-v1"


def test_rollback_does_not_delete_newer_version(
    registry: ModelRegistry, dummy_artifact: Path, dummy_artifact_v2: Path
):
    """Rollback only changes the pointer; v2 artifact must still exist."""
    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)
    registry.register("sentiment-v2", "svc", "tfidf", dummy_artifact_v2)

    registry.rollback("sentiment-v1")

    assert (registry.root / "sentiment-v2").is_dir()
    assert registry.artifact_path("sentiment-v2").exists()


def test_rollback_artifact_bytes_intact(
    registry: ModelRegistry, dummy_artifact: Path, dummy_artifact_v2: Path
):
    """After rollback, reading artifact_path(current) gives v1 bytes."""
    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)
    registry.register("sentiment-v2", "svc", "tfidf", dummy_artifact_v2)

    registry.rollback("sentiment-v1")

    current_artifact = registry.artifact_path(registry.current())
    assert current_artifact.read_bytes() == b"fake-model-bytes-v1"


def test_rollback_unknown_version_raises(
    registry: ModelRegistry, dummy_artifact: Path
):
    """Trying to roll back to a non-existent version must raise RegistryError."""
    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)

    with pytest.raises(RegistryError, match="not registered"):
        registry.rollback("sentiment-v999")


def test_rollback_and_forward_again(
    registry: ModelRegistry, dummy_artifact: Path, dummy_artifact_v2: Path
):
    """Roll back to v1, then forward to v2 — pointer must follow both moves."""
    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)
    registry.register("sentiment-v2", "svc", "tfidf", dummy_artifact_v2)

    registry.rollback("sentiment-v1")
    assert registry.current() == "sentiment-v1"

    # "re-promote" v2 via rollback (it's still registered)
    registry.rollback("sentiment-v2")
    assert registry.current() == "sentiment-v2"


# ── CLI smoke tests ────────────────────────────────────────────────────────────


def test_cli_rollback_command(
    registry: ModelRegistry,
    dummy_artifact: Path,
    dummy_artifact_v2: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Runs the CLI rollback subcommand end-to-end and checks that
    the on-disk pointer file is updated.
    """
    import sys
    from io import StringIO
    from platform.registry.cli import build_parser, cmd_rollback

    # Set the registry root to our temp registry via env var
    monkeypatch.setenv("REGISTRY_ROOT", str(registry.root))

    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)
    registry.register("sentiment-v2", "svc", "tfidf", dummy_artifact_v2)
    assert registry.current() == "sentiment-v2"

    # Parse rollback command and execute
    parser = build_parser()
    args = parser.parse_args(["rollback", "sentiment-v1"])

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)
    exit_code = cmd_rollback(args)

    assert exit_code == 0
    # Check that the on-disk pointer was actually written
    pointer_file = registry.root / "current"
    assert pointer_file.read_text().strip() == "sentiment-v1"


def test_cli_rollback_unknown_version_exits_nonzero(
    registry: ModelRegistry,
    dummy_artifact: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    from platform.registry.cli import build_parser, cmd_rollback

    monkeypatch.setenv("REGISTRY_ROOT", str(registry.root))
    registry.register("sentiment-v1", "svc", "tfidf", dummy_artifact)

    parser = build_parser()
    args = parser.parse_args(["rollback", "sentiment-v999"])
    exit_code = cmd_rollback(args)
    assert exit_code != 0


# ── directory-artifact support ────────────────────────────────────────────────


def test_register_directory_artifact(registry: ModelRegistry, tmp_path: Path):
    """Registry must also accept a directory (e.g. a HuggingFace model dir)."""
    model_dir = tmp_path / "transformer_model"
    model_dir.mkdir()
    (model_dir / "config.json").write_text('{"model_type": "bert"}')
    (model_dir / "pytorch_model.bin").write_bytes(b"\x00" * 16)

    registry.register(
        "sentiment-transformer-v1",
        "sentiment-svc",
        "transformer",
        model_dir,
    )

    stored = registry.artifact_path("sentiment-transformer-v1")
    assert stored.is_dir()
    assert (stored / "config.json").exists()
