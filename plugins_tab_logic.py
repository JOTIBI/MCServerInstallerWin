# plugins_tab_logic.py
import tkinter as tk
from tkinter import ttk
import webbrowser

class PluginsTab(ttk.Frame):
    def __init__(self, parent, server_type_getter):
        super().__init__(parent)
        self.server_type_getter = server_type_getter
        self.pack(fill="both", expand=True)
        self.notice_label = ttk.Label(self, text="Wähle einen Servertyp aus und öffne dann diesen Tab.")
        self.notice_label.pack(pady=20)
        self.link1 = ttk.Label(self, text="Bukkit.org Plugins", foreground="blue", cursor="hand2")
        self.link2 = ttk.Label(self, text="SpigotMC Plugins", foreground="blue", cursor="hand2")
        self.link1.bind("<Button-1>", lambda e: webbrowser.open("https://dev.bukkit.org/bukkit-plugins"))
        self.link2.bind("<Button-1>", lambda e: webbrowser.open("https://www.spigotmc.org/resources/"))

    def update_content(self):
        for widget in self.winfo_children():
            widget.pack_forget()

        server_type = self.server_type_getter().lower()
        if server_type == "paper" or server_type == "spigot":
            ttk.Label(self, text="Empfohlene Plugin-Seiten für diesen Servertyp:").pack(pady=(20, 10))
            self.link1.pack()
            self.link2.pack(pady=(5, 20))
        elif server_type == "forge" or server_type == "fabric":
            ttk.Label(self, text="Mods verwalten im Reiter 'Mods'.").pack(pady=20)
        else:
            ttk.Label(self, text="Vanilla unterstützt keine Plugins oder Mods.").pack(pady=20)
