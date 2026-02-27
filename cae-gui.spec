# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置 - CAE-CLI GUI
支持外部模型文件：用户只需下载 gguf 模型放到 exe 同目录即可
"""
import os
from pathlib import Path

block_cipher = None

# 项目根目录
root_dir = Path(SPECPATH)

# 收集数据文件（只包含 UI 资源，不包含大模型文件）
datas = [
    # GUI 资源文件
    (root_dir / "src" / "gui" / "cae_ui.html", "gui"),
    (root_dir / "src" / "gui" / "terminal_ui.html", "gui"),
]

# 收集隐藏导入
hiddenimports = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineCore",
    "shiboken6",
    # AI 模块
    "sw_helper.ai.local_gguf",
    "sw_helper.ai.local_embedding",
    # 求解器模块
    "integrations.cae.solvers",
    "integrations.cae.solvers.base",
    "integrations.cae.solvers.calculix_solver",
    "integrations.cae.solvers.simple_fem",
    "integrations.cae.solvers.scipy_solver",
]

a = Analysis(
    [root_dir / "src" / "main_gui.py"],
    pathex=[str(root_dir / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PyQt5",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="cae-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 应用，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="cae-gui",
)
