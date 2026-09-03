import os
import sys

# Pytest imports standard library `platform` early during startup.
# To allow importing submodules from the `platform/` directory (such as platform.database),
# we add the platform folder to sys.modules['platform'].__path__.
platform_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "platform"))
if "platform" in sys.modules:
    mod = sys.modules["platform"]
    if not hasattr(mod, "__path__") or platform_dir not in getattr(mod, "__path__", []):
        mod.__path__ = [platform_dir]
