import ctypes

from gui_design_upgrade import apply_theme


def setup_app(app):
    apply_theme(app)
    try:
        import sys
        import os
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        icon_path = os.path.join(base_path, "icon.ico")
        app.iconbitmap(default=icon_path)
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
