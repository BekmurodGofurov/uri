import os
import sys

sentiment_dir = os.path.abspath(os.path.dirname(__file__))
if sentiment_dir not in sys.path:
    sys.path.insert(0, sentiment_dir)

# Agar boshqa servis 'app' nomli modulni yuklab qo'ygan bo'lsa,
# sentiment-svc/app to'g'ri import bo'lishi uchun keshni tozalaymiz
app_mod = sys.modules.get("app")
if app_mod is not None:


    mod_path = getattr(app_mod, "__file__", "") or (
        getattr(app_mod, "__path__", [""])[0] if hasattr(app_mod, "__path__") else ""
    )


    if not mod_path.startswith(sentiment_dir):
        for mod_name in list(sys.modules.keys()):
            if mod_name == "app" or mod_name.startswith("app."):
                del sys.modules[mod_name]
