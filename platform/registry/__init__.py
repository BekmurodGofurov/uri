"""
platform/registry/__init__.py

Public surface for the model registry.
"""

from platform.registry.manager import ModelRegistry, RegistryError

__all__ = ["ModelRegistry", "RegistryError"]
