import os
import sys

aspect_dir = os.path.abspath(os.path.dirname(__file__))
if aspect_dir not in sys.path:
    sys.path.insert(0, aspect_dir)

# sentiment-svc ham "app" nomli paket ishlatadi — bitta pytest process ichida
# ikkalasi ham import qilinsa, eskisi keshda qolib ketmasligi uchun tozalaymiz.
app_mod = sys.modules.get("app")
if app_mod is not None:
    mod_path = getattr(app_mod, "__file__", "") or (
        getattr(app_mod, "__path__", [""])[0] if hasattr(app_mod, "__path__") else ""
    )
    if not mod_path.startswith(aspect_dir):
        for mod_name in list(sys.modules.keys()):
            if mod_name == "app" or mod_name.startswith("app."):
                del sys.modules[mod_name]
