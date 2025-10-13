# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['orchestrator_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        *collect_data_files('customtkinter'),
        ('nodeecli/install_nodejs_refactored.py', 'nodeecli'),
        ('nodeecli/README.md', 'nodeecli'),
        ('vscode/vscode_installer.py', 'vscode'),
        ('vscode/README.md', 'vscode')
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'requests',
        'queue',
        'threading',
        'subprocess'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OrquestradorInstalacoes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)

# Análise separada para o instalador do Node.js
nodejs_analysis = Analysis(
    ['nodeecli/install_nodejs_refactored.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'requests',
        'subprocess',
        'hashlib',
        'tempfile',
        'pathlib',
        'argparse',
        'json',
        'time',
        'shutil',
        'logging',
        'datetime',
        'platform',
        'ctypes',
        'winreg'  # Módulo específico do Windows
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

nodejs_pyz = PYZ(nodejs_analysis.pure, nodejs_analysis.zipped_data, cipher=block_cipher)

nodejs_exe = EXE(
    nodejs_pyz,
    nodejs_analysis.scripts,
    nodejs_analysis.binaries,
    nodejs_analysis.zipfiles,
    nodejs_analysis.datas,
    [],
    name='install_nodejs',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)

# Análise separada para o instalador do VS Code
vscode_analysis = Analysis(
    ['vscode/vscode_installer.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'requests',
        'subprocess',
        'tempfile',
        'pathlib',
        'time',
        'ctypes',
        'platform'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

vscode_pyz = PYZ(vscode_analysis.pure, vscode_analysis.zipped_data, cipher=block_cipher)

vscode_exe = EXE(
    vscode_pyz,
    vscode_analysis.scripts,
    vscode_analysis.binaries,
    vscode_analysis.zipfiles,
    vscode_analysis.datas,
    [],
    name='vscode_installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
