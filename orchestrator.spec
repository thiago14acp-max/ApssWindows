# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['srcmain.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        *collect_data_files('customtkinter'),
        ('nodeecli/README.md', 'nodeecli'),
        ('vscode/README.md', 'vscode'),
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

# Análise separada para o instalador do MCP Excel Server
mcp_excel_analysis = Analysis(
    ['mcp_excel/mcp_excel_installer.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'subprocess',
        'pathlib',
        'shutil',
        'sys',
        'os',
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

mcp_excel_pyz = PYZ(mcp_excel_analysis.pure, mcp_excel_analysis.zipped_data, cipher=block_cipher)

mcp_excel_exe = EXE(
    mcp_excel_pyz,
    mcp_excel_analysis.scripts,
    mcp_excel_analysis.binaries,
    mcp_excel_analysis.zipfiles,
    mcp_excel_analysis.datas,
    [],
    name='mcp_excel_installer',
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

# Análise separada para o instalador do Git
git_analysis = Analysis(
    ['git/git_installer.py'],
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
        'platform',
        'json',
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

git_pyz = PYZ(git_analysis.pure, git_analysis.zipped_data, cipher=block_cipher)

git_exe = EXE(
    git_pyz,
    git_analysis.scripts,
    git_analysis.binaries,
    git_analysis.zipfiles,
    git_analysis.datas,
    [],
    name='git_installer',
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

# Análise separada para o instalador do Antigravity
antigravity_analysis = Analysis(
    ['antigravity/installer.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'subprocess',
        'pathlib',
        'sys',
        'os',
        'ctypes'
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

antigravity_pyz = PYZ(antigravity_analysis.pure, antigravity_analysis.zipped_data, cipher=block_cipher)

antigravity_exe = EXE(
    antigravity_pyz,
    antigravity_analysis.scripts,
    antigravity_analysis.binaries,
    antigravity_analysis.zipfiles,
    antigravity_analysis.datas,
    [],
    name='antigravity_installer',
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

# Análise separada para o instalador do OpenCode
opencode_analysis = Analysis(
    ['opencode/installer.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'subprocess',
        'pathlib',
        'sys',
        'os',
        'ctypes',
        'requests',
        'hashlib',
        'shutil'
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

opencode_pyz = PYZ(opencode_analysis.pure, opencode_analysis.zipped_data, cipher=block_cipher)

opencode_exe = EXE(
    opencode_pyz,
    opencode_analysis.scripts,
    opencode_analysis.binaries,
    opencode_analysis.zipfiles,
    opencode_analysis.datas,
    [],
    name='opencode_installer',
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
