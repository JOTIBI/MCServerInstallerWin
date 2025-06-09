import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import urllib.request
import os
import json
import subprocess
import threading
import shutil
import sys
import ctypes
import requests
from xml.etree import ElementTree

class MinecraftServerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Server Installer - by JOTIBI")
        self.geometry("750x800")
        self.resizable(False, False)
        self.install_path = tk.StringVar(value=os.getcwd())
        self.create_tabs()
        self.java_installed = False
        self.all_minecraft_versions = []

        self.load_minecraft_versions()

    def create_tabs(self):
        tab_control = ttk.Notebook(self)

        self.tab_main = ttk.Frame(tab_control)
        self.tab_java = ttk.Frame(tab_control)
        self.tab_plugins = ttk.Frame(tab_control)
        self.tab_mods = ttk.Frame(tab_control)

        tab_control.add(self.tab_main, text='Server')
        tab_control.add(self.tab_java, text='Java')
        tab_control.add(self.tab_plugins, text='Addons')
        tab_control.add(self.tab_mods, text='Mods')

        tab_control.pack(expand=1, fill='both')

        self.create_main_tab()
        self.create_java_tab()
        self.create_plugins_tab()
        self.create_mods_tab()

        tab_control.bind("<<NotebookTabChanged>>", lambda e: self.update_dynamic_tabs())

    def create_main_tab(self):
        self.entries = {}

        def label_entry(parent, text, default=""):
            ttk.Label(parent, text=text).pack(pady=(10, 0))
            entry = ttk.Entry(parent)
            entry.insert(0, default)
            entry.pack()
            return entry

        self.entries['name'] = label_entry(self.tab_main, "Server Name:", "minecraft-server")

        ttk.Label(self.tab_main, text="Minecraft Version:").pack(pady=(10, 0))
        self.mc_version_cb = ttk.Combobox(self.tab_main, values=[], state="readonly")
        self.mc_version_cb.pack()
        self.mc_version_cb.bind("<<ComboboxSelected>>", self.on_minecraft_version_change)

        ttk.Label(self.tab_main, text="Max RAM (e.g. 4G):").pack(pady=(10, 0))
        self.entries['ram'] = ttk.Entry(self.tab_main)
        self.entries['ram'].insert(0, "4G")
        self.entries['ram'].pack()

        ttk.Label(self.tab_main, text="Port:").pack(pady=(10, 0))
        self.entries['port'] = ttk.Entry(self.tab_main)
        self.entries['port'].insert(0, "25565")
        self.entries['port'].pack()

        ttk.Label(self.tab_main, text="Server Type:").pack(pady=(10, 0))
        self.server_type = ttk.Combobox(self.tab_main, values=["Vanilla", "Paper", "Forge", "Fabric"], state="readonly")
        self.server_type.current(0)
        self.server_type.pack()
        self.server_type.bind("<<ComboboxSelected>>", self.on_server_type_change)

        self.mod_loader_version = ttk.Combobox(self.tab_main, state="readonly")
        self.mod_loader_version.pack(pady=(10, 0))
        self.mod_loader_version.pack_forget()

        ttk.Label(self.tab_main, text="Installation Directory:").pack(pady=(10, 0))
        path_entry = ttk.Entry(self.tab_main, textvariable=self.install_path)
        path_entry.pack()
        ttk.Button(self.tab_main, text="Choose Folder", command=self.select_folder).pack(pady=5)

        ttk.Button(self.tab_main, text="Install Server", command=self.install_server_click).pack(pady=20)

        self.status_label = ttk.Label(self.tab_main, text="")
        self.status_label.pack()

    def load_minecraft_versions(self):
        def run():
            try:
                url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                versions = [v['id'] for v in data['versions']]
                self.all_minecraft_versions = versions
                self.filter_versions_by_server_type(self.server_type.get().lower())
            except Exception as e:
                print(f"Fehler beim Laden der Minecraft-Versionen: {e}")
        threading.Thread(target=run).start()

    def filter_versions_by_server_type(self, server_type):
        if server_type == "vanilla":
            filtered_versions = self.all_minecraft_versions  # alle inkl. snapshots/previews
        else:
            filtered_versions = [v for v in self.all_minecraft_versions if "snapshot" not in v and "preview" not in v]

        filtered_versions.sort()

        current_selection = self.mc_version_cb.get()
        self.mc_version_cb['values'] = filtered_versions
        if current_selection in filtered_versions:
            self.mc_version_cb.set(current_selection)
        elif filtered_versions:
            self.mc_version_cb.current(len(filtered_versions) - 1)

    def fetch_forge_versions(self, mc_version):
        def run():
            try:
                url = "https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                tree = ElementTree.fromstring(resp.content)
                versions = [v.text for v in tree.findall(".//versioning/versions/version")]
                filtered = [v for v in versions if v.startswith(mc_version) and not any(x in v for x in ["-rc", "-beta", "-alpha"])]
                filtered.sort()
                if filtered:
                    self.mod_loader_version['values'] = filtered[-10:]
                    self.mod_loader_version.current(len(filtered[-10:]) - 1)
                    self.mod_loader_version.pack(pady=(10, 0))
                else:
                    self.mod_loader_version.pack_forget()
            except Exception as e:
                print(f"Forge versions fetch failed: {e}")
                self.mod_loader_version.pack_forget()
        threading.Thread(target=run).start()

    def fetch_fabric_versions(self, mc_version):
        def run():
            try:
                url = "https://meta.fabricmc.net/v2/versions/installer"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                versions = [v["version"] for v in resp.json()]
                if versions:
                    self.mod_loader_version['values'] = versions[-10:]
                    self.mod_loader_version.current(len(versions) - 1)
                    self.mod_loader_version.pack(pady=(10, 0))
                else:
                    self.mod_loader_version.pack_forget()
            except Exception as e:
                print(f"Fabric versions fetch failed: {e}")
                self.mod_loader_version.pack_forget()
        threading.Thread(target=run).start()

    def on_server_type_change(self, event=None):
        server_type = self.server_type.get().lower()
        self.filter_versions_by_server_type(server_type)
        if server_type == "forge":
            mc_version = self.mc_version_cb.get()
            self.fetch_forge_versions(mc_version)
        elif server_type == "fabric":
            self.fetch_fabric_versions(self.mc_version_cb.get())
        else:
            self.mod_loader_version.pack_forget()

    def create_java_tab(self):
        ttk.Label(self.tab_java, text="Check if Java is installed").pack(pady=10)
        ttk.Button(self.tab_java, text="Check Java", command=self.check_java).pack()
        self.java_status = ttk.Label(self.tab_java, text="")
        self.java_status.pack(pady=10)

        ttk.Label(self.tab_java, text="Optional: Download & Install OpenJDK 17").pack(pady=(20, 0))
        ttk.Label(self.tab_java, text="Hinweis: Für die Installation werden Administratorrechte benötigt.", foreground="red").pack(pady=(0, 10))
        ttk.Button(self.tab_java, text="Install Java", command=self.install_java_click).pack()

        self.java_progress = ttk.Progressbar(self.tab_java, orient='horizontal', length=300, mode='determinate')
        self.java_progress.pack(pady=10)

    def create_plugins_tab(self):
        self.plugins_label = ttk.Label(self.tab_plugins, text="Plugins werden basierend auf dem gewählten Servertyp angezeigt.")
        self.plugins_label.pack(pady=20)

        self.link1 = ttk.Label(self.tab_plugins, text="Bukkit.org Plugins", foreground="blue", cursor="hand2")
        self.link2 = ttk.Label(self.tab_plugins, text="SpigotMC Plugins", foreground="blue", cursor="hand2")
        self.link1.bind("<Button-1>", lambda e: self.open_url("https://dev.bukkit.org/bukkit-plugins"))
        self.link2.bind("<Button-1>", lambda e: self.open_url("https://www.spigotmc.org/resources/"))

    def create_mods_tab(self):
        from modrinth_mod_manager import ModrinthModManager
        self.mods_frame = ModrinthModManager(self.tab_mods, self.install_path)

    def update_dynamic_tabs(self):
        for widget in self.tab_plugins.winfo_children():
            widget.pack_forget()

        server_type = self.server_type.get().lower()
        if server_type in ["paper", "spigot"]:
            ttk.Label(self.tab_plugins, text="Empfohlene Plugin-Seiten für diesen Servertyp:").pack(pady=(20, 10))
            self.link1.pack()
            self.link2.pack(pady=(5, 20))
        elif server_type in ["forge", "fabric"]:
            ttk.Label(self.tab_plugins, text="Forge & Fabric verwenden Mods. Diese findest du im Tab 'Mods'.").pack(pady=20)
        else:
            ttk.Label(self.tab_plugins, text="Vanilla unterstützt keine Plugins oder Mods.").pack(pady=20)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.install_path.set(folder)

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def check_java(self):
        install_dir = self.install_path.get()
        java_bin_path = None

        for root, dirs, files in os.walk(install_dir):
            if 'java.exe' in files:
                java_bin_path = os.path.join(root, 'java.exe')
                break

        try:
            if java_bin_path:
                result = subprocess.run([java_bin_path, '-version'], capture_output=True, text=True)
            else:
                result = subprocess.run(['java', '-version'], capture_output=True, text=True)

            output = result.stderr.split('\n')[0]
            self.java_status.config(text=output)
            self.java_installed = True
        except FileNotFoundError:
            self.java_status.config(text='Java not found!')
            self.java_installed = False

    def install_java_click(self):
        if not self.is_admin():
            messagebox.showinfo("Adminrechte benötigt", "Die Java-Installation benötigt Administratorrechte. Das Programm wird neu gestartet...")
            self.run_as_admin()
            return
        install_dir = self.install_path.get()
        threading.Thread(target=self.install_java, args=(install_dir,)).start()

    def install_java(self, install_dir):
        jdk_url = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.7%2B7/OpenJDK17U-jdk_x64_windows_hotspot_17.0.7_7.zip"
        jdk_zip = os.path.join(install_dir, "jdk.zip")

        try:
            req = urllib.request.Request(jdk_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                total_size = int(response.getheader('Content-Length').strip())
                block_size = 8192
                downloaded = 0

                with open(jdk_zip, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        f.write(buffer)
                        progress_percent = int(downloaded * 100 / total_size)
                        self.java_progress['value'] = progress_percent
                        self.java_progress.update()

            import zipfile
            with zipfile.ZipFile(jdk_zip, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            os.remove(jdk_zip)
            messagebox.showinfo("Java Installation", "Java wurde installiert.")
            self.java_installed = True
            self.java_status.config(text="Java installiert")
            self.java_progress['value'] = 0
        except Exception as e:
            messagebox.showerror("Java Fehler", f"Fehler beim Download oder Entpacken:\n{e}")
            self.java_progress['value'] = 0

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        params = ' '.join([f'"{x}"' for x in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()

    def download_file(self, url, dest):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
                out_file.write(response.read())
            return True
        except Exception as e:
            messagebox.showerror("Download Error", f"Fehler beim Download:\n{e}")
            return False

    def install_server_click(self):
        install_dir = self.install_path.get()
        version = self.mc_version_cb.get()
        server_type = self.server_type.get().lower()
        mod_loader_version = None
        if server_type in ["forge", "fabric"]:
            mod_loader_version = self.mod_loader_version.get()
        threading.Thread(target=self.install_server, args=(install_dir, version, server_type, mod_loader_version)).start()

    def install_server(self, install_dir, version, server_type, mod_loader_version=None):
        try:
            os.makedirs(install_dir, exist_ok=True)
            os.chdir(install_dir)

            if server_type == "vanilla":
                manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
                manifest = urllib.request.urlopen(manifest_url).read().decode()
                manifest_data = json.loads(manifest)
                version_data = next((v for v in manifest_data["versions"] if v["id"] == version), None)
                if not version_data:
                    raise Exception("Version not found.")
                version_info = json.loads(urllib.request.urlopen(version_data["url"]).read().decode())
                jar_url = version_info["downloads"]["server"]["url"]
                self.status_label.config(text="Vanilla Server wird heruntergeladen...")
                if not self.download_file(jar_url, "server.jar"):
                    self.status_label.config(text="Download fehlgeschlagen.")
                    return

            elif server_type == "paper":
                jar_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/latest/downloads/paper-{version}-latest.jar"
                self.status_label.config(text="Paper Server wird heruntergeladen...")
                if not self.download_file(jar_url, "server.jar"):
                    self.status_label.config(text="Download fehlgeschlagen.")
                    return

            elif server_type == "forge":
                if not mod_loader_version:
                    raise Exception("Bitte Forge Version auswählen.")
                forge_installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mod_loader_version}/forge-{mod_loader_version}-installer.jar"
                self.status_label.config(text="Forge Installer wird heruntergeladen...")
                if not self.download_file(forge_installer_url, "forge-installer.jar"):
                    self.status_label.config(text="Download fehlgeschlagen.")
                    return

                self.status_label.config(text="Forge Installer wird ausgeführt...")
                subprocess.run(["java", "-jar", "forge-installer.jar", "--installServer"], check=True)
                os.remove("forge-installer.jar")

                forge_jars = [f for f in os.listdir() if f.startswith("forge-") and f.endswith(".jar") and "installer" not in f]
                if not forge_jars:
                    raise Exception("Forge Server-JAR nicht gefunden.")
                os.rename(forge_jars[0], "server.jar")

            elif server_type == "fabric":
                if not mod_loader_version:
                    raise Exception("Bitte Fabric Version auswählen.")
                fabric_installer_url = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/0.11.2/fabric-installer-0.11.2.jar"
                self.status_label.config(text="Fabric Installer wird heruntergeladen...")
                if not self.download_file(fabric_installer_url, "fabric-installer.jar"):
                    self.status_label.config(text="Download fehlgeschlagen.")
                    return

                self.status_label.config(text="Fabric Installer wird ausgeführt...")
                subprocess.run(["java", "-jar", "fabric-installer.jar", "server", "-mcversion", version, "-dir", install_dir], check=True)
                os.remove("fabric-installer.jar")

                if not os.path.exists(os.path.join(install_dir, "fabric-server-launch.jar")):
                    raise Exception("Fabric Server-JAR nicht gefunden.")
                os.rename(os.path.join(install_dir, "fabric-server-launch.jar"), "server.jar")

            else:
                raise Exception("Unsupported server type")

            with open("eula.txt", "w") as f:
                f.write("eula=true\n")

            with open("start.bat", "w") as f:
                ram = self.entries['ram'].get()
                java_path = None
                for root, dirs, files in os.walk(install_dir):
                    if 'java.exe' in files:
                        java_path = os.path.join(root, 'java.exe')
                        break
                if java_path:
                    f.write(f'"{java_path}" -Xmx{ram} -jar server.jar nogui\n')
                else:
                    f.write(f'java -Xmx{ram} -jar server.jar nogui\n')
                f.write("pause\n")

            with open("server.properties", "w") as f:
                port = self.entries['port'].get()
                f.write(f"server-port={port}\n")
                f.write("motd=A Minecraft Server by JOTIBI\n")
                f.write("enable-command-block=true\n")
                f.write("max-players=20\n")
                f.write("online-mode=true\n")

            mods_dir = os.path.join(install_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)

            self.status_label.config(text="Server installiert.")
            messagebox.showinfo("Erfolg", "Minecraft Server erfolgreich installiert!")
        except Exception as e:
            self.status_label.config(text="")
            messagebox.showerror("Fehler", str(e))


if __name__ == "__main__":
    app = MinecraftServerGUI()
    app.mainloop()
