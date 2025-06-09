from icon_and_darkmode import setup_app
from minecraft_gui_installer import MinecraftServerGUI


if __name__ == "__main__":
    app = MinecraftServerGUI()
    setup_app(app)
    app.mainloop()
