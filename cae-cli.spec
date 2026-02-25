# -*- mode: python ; coding: utf-8 -*-
"""
CLI版本打包配置
使用: pyinstaller cae-cli.spec
"""
from PyInstaller.utils.hooks import collect_all

datas = [('src', 'src'), ('data', 'data'), ('knowledge', 'knowledge'), ('prompts', 'prompts')]
binaries = []
hiddenimports = ['click', 'rich', 'yaml', 'numpy', 'jinja2', 'pint', 'markdown', 'requests']

tmp_ret = collect_all('rich')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('markdown')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src\\sw_helper\\cli.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PySide6', 'PySide', 'chromadb', 'sentence_transformers', 'torch', 'transformers', 'tcl', 'tk'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cae-cli',
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
)
