"""
platform/registry/manager.py
─────────────────────────────
Versioned model registry using a directory tree + pointer file.

Layout on disk
──────────────
<root>/
  current          ← plain text: the active version name, e.g. "sentiment-v2"
  sentiment-v1/
    meta.json      ← {"version", "service", "model_type", "registered_at",
                       "headline_metric", "artifact_path", "notes"}
    model.joblib   ← (or any artifact the caller passes in)
  sentiment-v2/
    meta.json
    model.joblib

Why this instead of MLflow
──────────────────────────
MLflow requires a running tracking server (or SQLite + local artifact store).
This implementation is zero-dependency beyond the stdlib and is fully
testable in-process. A versioned directory + pointer file is explicitly
listed as an acceptable approach in the project requirements.

Rollback is one command:
    python -m platform.registry rollback <version>

The one-command constraint is satisfied by the CLI in platform/registry/cli.py.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_REGISTRY_ROOT = Path(__file__).parent.parent.parent / "model_registry"
CURRENT_POINTER = "current"
META_FILE = "meta.json"


class RegistryError(Exception):
    """Raised for any registry operation failure."""


class ModelRegistry:
    """
    File-system backed model registry.

    Parameters
    ----------
    root:
        Path to the registry root directory.  Created automatically.
    """

    def __init__(self, root: Path | str = DEFAULT_REGISTRY_ROOT) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # ── internal helpers ──────────────────────────────────────────────────────

    @property
    def _pointer_path(self) -> Path:
        return self.root / CURRENT_POINTER

    def _version_dir(self, version: str) -> Path:
        return self.root / version

    def _meta_path(self, version: str) -> Path:
        return self._version_dir(version) / META_FILE

    # ── public API ────────────────────────────────────────────────────────────

    def register(
        self,
        version: str,
        service: str,
        model_type: str,
        artifact_src: Path | str,
        headline_metric: str = "",
        notes: str = "",
        set_current: bool = True,
    ) -> Path:
        """
        Register a new model version.

        Copies *artifact_src* (a file or directory) into the registry and
        writes a ``meta.json`` alongside it.  Optionally makes this version
        the *current* active version.

        Parameters
        ----------
        version:
            Unique version string, e.g. ``"sentiment-v2"``.
        service:
            Which service owns this model, e.g. ``"sentiment-svc"``.
        model_type:
            ``"tfidf"`` | ``"transformer"`` | any string.
        artifact_src:
            Path to the model file or directory to register.
        headline_metric:
            Human-readable metric string, e.g. ``"macro-f1: 0.63"``.
        notes:
            Free-form notes (why this version was trained, etc.).
        set_current:
            If *True* (default), atomically update the ``current`` pointer.

        Returns
        -------
        Path
            The directory where the artifact was stored.

        Raises
        ------
        RegistryError
            If the version already exists.
        """
        src = Path(artifact_src)
        if not src.exists():
            raise RegistryError(f"Artifact not found: {src}")

        version_dir = self._version_dir(version)
        if version_dir.exists():
            raise RegistryError(
                f"Version '{version}' already exists at {version_dir}. "
                "Bump the version string to register a new artifact."
            )

        version_dir.mkdir(parents=True)

        # Copy artifact (file or directory tree)
        dest = version_dir / src.name
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)

        # Write metadata
        meta = {
            "version": version,
            "service": service,
            "model_type": model_type,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "headline_metric": headline_metric,
            "artifact_path": str(dest),
            "notes": notes,
        }
        self._meta_path(version).write_text(json.dumps(meta, indent=2))

        if set_current:
            self._set_current(version)

        return version_dir

    def rollback(self, version: str) -> None:
        """
        Roll back to *version* by updating the ``current`` pointer.

        Does **not** delete any files — only changes which version is active.
        The caller is responsible for reloading the service (e.g. restart the
        container, or PATCH the running service's /reload endpoint).

        Parameters
        ----------
        version:
            The version to activate, e.g. ``"sentiment-v1"``.

        Raises
        ------
        RegistryError
            If *version* is not registered.
        """
        if not self._version_dir(version).exists():
            available = self.list_versions()
            raise RegistryError(
                f"Version '{version}' is not registered. "
                f"Available versions: {available}"
            )
        self._set_current(version)

    def current(self) -> str | None:
        """
        Return the active version name, or *None* if no version is set yet.
        """
        if not self._pointer_path.exists():
            return None
        return self._pointer_path.read_text().strip() or None

    def current_meta(self) -> dict | None:
        """Return the metadata dict for the current version, or *None*."""
        ver = self.current()
        if ver is None:
            return None
        return self.get_meta(ver)

    def get_meta(self, version: str) -> dict:
        """
        Return the metadata dict for *version*.

        Raises
        ------
        RegistryError
            If *version* is not registered or meta.json is missing/corrupt.
        """
        meta_path = self._meta_path(version)
        if not meta_path.exists():
            raise RegistryError(f"No metadata found for version '{version}'.")
        try:
            return json.loads(meta_path.read_text())
        except json.JSONDecodeError as exc:
            raise RegistryError(
                f"Corrupt meta.json for version '{version}': {exc}"
            ) from exc

    def list_versions(self) -> list[str]:
        """
        Return all registered version names sorted by registration time.
        Versions without a valid ``meta.json`` are skipped.
        """
        versions: list[tuple[str, str]] = []
        for child in self.root.iterdir():
            if child.is_dir() and (child / META_FILE).exists():
                try:
                    meta = json.loads((child / META_FILE).read_text())
                    versions.append((meta.get("registered_at", ""), child.name))
                except (json.JSONDecodeError, KeyError):
                    pass
        return [name for _, name in sorted(versions)]

    def artifact_path(self, version: str) -> Path:
        """
        Return the path to the stored artifact for *version*.

        Raises
        ------
        RegistryError
            If the artifact is missing from disk.
        """
        meta = self.get_meta(version)
        path = Path(meta["artifact_path"])
        if not path.exists():
            raise RegistryError(
                f"Artifact for '{version}' not found at {path}."
            )
        return path

    # ── internal ──────────────────────────────────────────────────────────────

    def _set_current(self, version: str) -> None:
        """Atomically write the current pointer (write-then-rename)."""
        tmp = self._pointer_path.with_suffix(".tmp")
        tmp.write_text(version)
        tmp.replace(self._pointer_path)  # atomic on POSIX
