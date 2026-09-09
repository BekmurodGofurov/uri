import os
import sys

# Ensure sentiment-svc root is prepended to sys.path
sentiment_dir = os.path.abspath(os.path.dirname(__file__))
if sentiment_dir not in sys.path:
    sys.path.insert(0, sentiment_dir)

# If 'app' was already imported by another service or root namespace,
# purge it to ensure sentiment-svc/app is loaded cleanly during test runs.
app_mod = sys.modules.get("app")
if app_mod is not None:
    mod_path = getattr(app_mod, "__file__", "") or (
        getattr(app_mod, "__path__", [""])[0] if hasattr(app_mod, "__path__") else ""
    )
    if not mod_path.startswith(sentiment_dir):
        for mod_name in list(sys.modules.keys()):
            if mod_name == "app" or mod_name.startswith("app."):
                del sys.modules[mod_name]
