# -*- mode: python ; coding: utf-8 -*-

# PyInstaller spec file for Tweet Scraper Enhanced Edition
# Updated for refactored structure

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
        ('src', 'src'),  # Include the entire src directory
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'selenium',
        'webdriver_manager',
        'pandas',
        'openpyxl',
        'src',
        'src.config',
        'src.config.constants',
        'src.core',
        'src.core.deduplicator',
        'src.core.progress_tracker',
        'src.core.theme_manager',
        'src.core.styles',
        'src.core.styles.themes',
        'src.scraper',
        'src.scraper.driver_setup',
        'src.scraper.tweet_parser',
        'src.scraper.tweet_scraper',
        'src.gui',
        'src.gui.signals',
        'src.gui.main_window',
    ],
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
    name='TweetScraper',
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
    icon=None,  # Add icon path here if you have one
)
