# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\src', 'src'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\data\\config.yaml', 'data'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\data\\languages.json', 'data'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\data\\learning_progress.json', 'data'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\data\\materials.json', 'data'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\data\\quiz\\basic_mechanical.yaml', 'data\\quiz'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\knowledge\\fasteners.md', 'knowledge'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\knowledge\\materials.md', 'knowledge'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\knowledge\\standard_parts.md', 'knowledge'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\knowledge\\tolerances.md', 'knowledge'), ('E:\\workspace\\projects\\caw-cli\\caw-cli-main\\scripts\\first_run_check.py', 'scripts')]
binaries = []
hiddenimports = ['click', 'rich', 'yaml', 'numpy', 'jinja2', 'pint', 'chromadb', 'sentence_transformers', 'sw_helper.utils.rag_engine', 'sw_helper.learning.progress_tracker', 'sw_helper.learning.quiz_manager', 'sw_helper.main_menu', 'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'gui', 'gui.main_window', 'gui.theme', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineCore', 'PySide6.QtWebChannel', 'gui.web_view']
tmp_ret = collect_all('chromadb')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sentence_transformers')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rich')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['E:\\workspace\\projects\\caw-cli\\caw-cli-main\\src\\main_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.QtWebEngineWidgets'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
