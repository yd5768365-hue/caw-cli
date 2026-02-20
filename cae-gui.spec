# -*- mode: python ; coding: utf-8 -*-
"""
GUI版本打包配置
使用: pyinstaller cae-gui.spec
"""
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# 收集所有依赖
datas = [
    ('src', 'src'),
    ('data', 'data'),
    ('knowledge', 'knowledge'),
]

binaries = []
hiddenimports = [
    'click',
    'rich',
    'yaml',
    'numpy',
    'jinja2',
    'pint',
    'markdown',
    'requests',
]

# 收集rich
tmp_ret = collect_all('rich')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# 收集markdown  
tmp_ret = collect_all('markdown')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# 收集requests
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# PySide6设为可选，不强制打包


a = Analysis(
    ['src\\main_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cae-cli-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 显示控制台输出安装提示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cae-cli-gui',
)
