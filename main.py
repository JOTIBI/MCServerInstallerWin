from icon_and_darkmode import *
from minecraft_gui_installer import MinecraftServerGUI

import sys
import os

if __name__ == "__main__":
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    icon_path = os.path.join(base_path, "icon.ico")

    app = MinecraftServerGUI()
    apply_theme(app)
    app.iconbitmap(default=icon_path)
    app.mainloop()
