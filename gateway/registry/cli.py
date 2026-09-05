"""
gateway/registry/cli.py
───────────────────────
One-command CLI for the model registry.

Usage
─────
    # Show current active version
    python -m gateway.registry current

    # List all registered versions
    python -m gateway.registry list

    # Register a new model artifact
    python -m gateway.registry register \
        --version  sentiment-v2 \
        --service  sentiment-svc \
        --type     tfidf \
        --artifact sentiment-svc/models/tfidf_v2.joblib \
        --metric   "macro-f1: 0.65" \
        --notes    "Trained with balanced class weights"

    # Roll back to a previous version  ← the one-command rollback
    python -m gateway.registry rollback sentiment-v1

    # Show metadata for a specific version
    python -m gateway.registry info sentiment-v1
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Allow running as `python -m gateway.registry` from the repo root.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.registry.manager import DEFAULT_REGISTRY_ROOT, ModelRegistry, RegistryError


def _get_registry() -> ModelRegistry:
    root = os.getenv("REGISTRY_ROOT", str(DEFAULT_REGISTRY_ROOT))
    return ModelRegistry(root=root)


def cmd_current(_args: argparse.Namespace) -> int:
    reg = _get_registry()
    ver = reg.current()
    if ver is None:
        print("No active version set.")
        return 1
    meta = reg.get_meta(ver)
    print(f"Current version : {ver}")
    print(f"Service         : {meta.get('service', '-')}")
    print(f"Model type      : {meta.get('model_type', '-')}")
    print(f"Registered at   : {meta.get('registered_at', '-')}")
    print(f"Headline metric : {meta.get('headline_metric', '-')}")
    print(f"Artifact        : {meta.get('artifact_path', '-')}")
    if meta.get("notes"):
        print(f"Notes           : {meta['notes']}")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    reg = _get_registry()
    versions = reg.list_versions()
    current = reg.current()
    if not versions:
        print("No versions registered yet.")
        return 0
    for v in versions:
        marker = " ← current" if v == current else ""
        meta = reg.get_meta(v)
        metric = meta.get("headline_metric", "")
        print(f"  {v}{marker}  [{metric}]")
    return 0


def cmd_register(args: argparse.Namespace) -> int:
    reg = _get_registry()
    try:
        version_dir = reg.register(
            version=args.version,
            service=args.service,
            model_type=args.type,
            artifact_src=args.artifact,
            headline_metric=args.metric,
            notes=args.notes,
            set_current=not args.no_current,
        )
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Registered '{args.version}' → {version_dir}")
    if not args.no_current:
        print(f"Current pointer updated to '{args.version}'.")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    reg = _get_registry()
    previous = reg.current()
    try:
        reg.rollback(args.version)
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Rolled back: {previous!r} → '{args.version}'")
    print(f"Active version is now: {reg.current()}")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    reg = _get_registry()
    try:
        meta = reg.get_meta(args.version)
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(meta, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m gateway.registry",
        description="Uzum Review Intelligence — model registry CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # current
    sub.add_parser("current", help="Show the active model version")

    # list
    sub.add_parser("list", help="List all registered versions")

    # register
    reg_p = sub.add_parser("register", help="Register a new model artifact")
    reg_p.add_argument("--version", required=True, help="Version string, e.g. sentiment-v2")
    reg_p.add_argument("--service", required=True, help="Service name, e.g. sentiment-svc")
    reg_p.add_argument("--type", required=True, dest="type", help="tfidf | transformer")
    reg_p.add_argument("--artifact", required=True, help="Path to model file or directory")
    reg_p.add_argument("--metric", default="", help='Headline metric, e.g. "macro-f1: 0.63"')
    reg_p.add_argument("--notes", default="", help="Free-form notes")
    reg_p.add_argument(
        "--no-current",
        action="store_true",
        help="Do not update the current pointer after registering",
    )

    # rollback  ← the one command
    rb_p = sub.add_parser("rollback", help="Roll back to a previously registered version")
    rb_p.add_argument("version", help="Version to activate, e.g. sentiment-v1")

    # info
    info_p = sub.add_parser("info", help="Show metadata for a specific version")
    info_p.add_argument("version", help="Version name")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "current": cmd_current,
        "list": cmd_list,
        "register": cmd_register,
        "rollback": cmd_rollback,
        "info": cmd_info,
    }
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
