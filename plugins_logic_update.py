# plugins_logic_update.py
from tkinter import ttk


def update_dynamic_tabs(self):
    for widget in self.tab_plugins.winfo_children():
        widget.pack_forget()

    server_type = self.server_type.get().lower()
    if server_type in ["paper", "spigot"]:
        ttk.Label(
            self.tab_plugins,
            text="Empfohlene Plugin-Seiten für diesen Servertyp:"
        ).pack(pady=(20, 10))
        self.link1.pack()
        self.link2.pack(pady=(5, 20))
    elif server_type in ["forge", "fabric"]:
        ttk.Label(
            self.tab_plugins,
            text=(
                "Forge & Fabric verwenden Mods. "
                "Diese findest du im Tab 'Mods'."
            ),
        ).pack(pady=20)
    else:
        ttk.Label(
            self.tab_plugins,
            text="Vanilla unterstützt keine Plugins oder Mods."
        ).pack(pady=20)
