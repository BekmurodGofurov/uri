import importlib.util
import os

# Transparently forward standard library `platform` functions and attributes
# so that third-party packages (SQLAlchemy, pytest, urllib3, etc.) that do
# `import platform; platform.python_implementation()` continue to work seamlessly.
_stdlib_platform_path = os.path.join(os.path.dirname(os.__file__), "platform.py")
if os.path.exists(_stdlib_platform_path):
    _spec = importlib.util.spec_from_file_location("_stdlib_platform", _stdlib_platform_path)
    if _spec and _spec.loader:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        for _attr_name in dir(_mod):
            if not _attr_name.startswith("__"):
                globals()[_attr_name] = getattr(_mod, _attr_name)
