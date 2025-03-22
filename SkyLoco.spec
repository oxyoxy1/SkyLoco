# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py', 'ui_widgets.py', 'weather_api.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('background_music.mp3', '.'),
        ('cloudy_icon.png', '.'),
        ('icon.ico', '.'),
        ('rain_icon.png', '.'),
        ('splash_image.png', '.'),
        ('sun_icon.png', '.'),
        ('wind_icon.png', '.'),
        ('weather_data.json', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SkyLoco',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
