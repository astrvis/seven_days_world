import os
import sys

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/res', 'res'),
        ('src/settings.json', '.'),
        (os.path.join(sys.prefix, 'Lib', 'site-packages', 'rapidocr'), 'rapidocr'),
    ],
    hiddenimports=[
        'flet',
        'mss',
        'cv2',
        'pydirectinput',
        'pygetwindow',
        'rapidocr',
        'onnxruntime',
        'win32gui',
        'win32api',
        'win32con',
        'torch',
        'torchvision',
        'torchaudio',
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
    [],
    exclude_binaries=True,
    name='阿星的小助手',
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
    icon='src/public/favicon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='阿星的小助手',
)