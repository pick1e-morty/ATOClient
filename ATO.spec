# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = []
binaries += collect_dynamic_libs('UnifyNetSDK')


a = Analysis(
    ['C:/Users/Administrator/Documents/CodeProject/ATO/app/ATO.py'],
    pathex=[],
    binaries=binaries,
    datas=[('C:/Users/Administrator/Documents/CodeProject/ATO/app/AppData', 'AppData/'), ('C:/Users/Administrator/Documents/CodeProject/ATO/app/main_window/resource', 'app/main_window/resource/'), ('C:/Users/Administrator/Documents/CodeProject/ATO/app/app_setting_widget/resource', 'app/app_setting_widget/resource/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['C:/Users/Administrator/Documents/CodeProject/ATO/hook.py'],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ATO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Administrator\\Documents\\CodeProject\\ATO\\app\\resource\\_soft_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ATO',
)
