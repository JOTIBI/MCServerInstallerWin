import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--noconsole',
    '--icon=icon.ico',
    '--name=MinecraftServerInstaller',
    '--add-data=icon.ico;.',
    '--hidden-import=requests',
    '--version-file=version.txt'
])
