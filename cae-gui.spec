# -*- mode: python ; coding: utf-8 -*-
"""
GUI版本打包配置
使用: pyinstaller cae-gui.spec
"""
from PyInstaller.utils.hooks import collect_all

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

tmp_ret = collect_all('rich')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('markdown')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src\\main_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'chromadb', 'sentence_transformers', 'torch', 'transformers'],
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
    console=True,
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
