# modrinth_mod_manager.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import urllib.request
import threading
import json

class ModrinthModManager(ttk.Frame):
    def __init__(self, parent, install_path_var):
        super().__init__(parent)
        self.install_path_var = install_path_var
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Installierte Mods:").pack(pady=(10, 0))
        self.installed_list = tk.Listbox(self, height=10)
        self.installed_list.pack(fill="both", expand=True, padx=10)
        ttk.Button(self, text="Mods-Ordner öffnen", command=self.open_mod_folder).pack(pady=5)

        ttk.Separator(self).pack(fill="x", pady=5)
        ttk.Label(self, text="Modrinth Mod-Suche & Installation:").pack(pady=(10, 5))
        self.search_entry = ttk.Entry(self)
        self.search_entry.pack(fill="x", padx=10)
        ttk.Button(self, text="Mod suchen & installieren", command=self.search_and_install_modrinth).pack(pady=5)

        ttk.Separator(self).pack(fill="x", pady=5)
        ttk.Label(self, text="Manuell Mods einfügen (.jar Dateien)").pack(pady=(10, 0))
        ttk.Button(self, text="Dateien auswählen und kopieren", command=self.manual_add_mods).pack(pady=5)

    def open_mod_folder(self):
        mods_path = os.path.join(self.install_path_var.get(), "mods")
        if os.path.exists(mods_path):
            os.startfile(mods_path)
        else:
            messagebox.showerror("Fehler", "Mods-Ordner nicht gefunden")

    def manual_add_mods(self):
        files = filedialog.askopenfilenames(filetypes=[("Java Archive", "*.jar")])
        mods_dir = os.path.join(self.install_path_var.get(), "mods")
        os.makedirs(mods_dir, exist_ok=True)
        for f in files:
            shutil.copy(f, mods_dir)
        self.update_installed_list()

    def search_and_install_modrinth(self):
        def run():
            query = self.search_entry.get()
            if not query:
                return
            try:
                url = f"https://api.modrinth.com/v2/search?query={query}"
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                if not data["hits"]:
                    messagebox.showinfo("Keine Ergebnisse", "Keine Mods gefunden.")
                    return
                mod = data["hits"][0]
                project_id = mod["project_id"]
                project_url = f"https://api.modrinth.com/v2/project/{project_id}/version"
                with urllib.request.urlopen(project_url) as response:
                    versions = json.loads(response.read().decode())
                file_url = versions[0]["files"][0]["url"]
                mods_dir = os.path.join(self.install_path_var.get(), "mods")
                os.makedirs(mods_dir, exist_ok=True)
                filename = os.path.basename(file_url)
                dest_path = os.path.join(mods_dir, filename)
                urllib.request.urlretrieve(file_url, dest_path)
                messagebox.showinfo("Mod installiert", f"{filename} installiert.")
                self.update_installed_list()
            except Exception as e:
                messagebox.showerror("Fehler", str(e))
        threading.Thread(target=run).start()

    def update_installed_list(self):
        mods_dir = os.path.join(self.install_path_var.get(), "mods")
        self.installed_list.delete(0, tk.END)
        if os.path.exists(mods_dir):
            for file in os.listdir(mods_dir):
                if file.endswith(".jar"):
                    self.installed_list.insert(tk.END, file)
