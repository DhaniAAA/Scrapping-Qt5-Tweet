# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('modified-lexicon_v2.txt', '.')],
    hiddenimports=[
        # PyQt5
        'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport', 'PyQt5.QtSvg',
        # Selenium - Chrome
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.webdriver',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.chrome.remote_connection',
        # Selenium - Common
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.common.action_chains',
        'selenium.webdriver.common.desired_capabilities',
        'selenium.webdriver.common.options',
        'selenium.webdriver.common.service',
        'selenium.webdriver.common.utils',
        # Selenium - Support
        'selenium.webdriver.support',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.wait',
        'selenium.webdriver.support.expected_conditions',
        # Selenium - Remote
        'selenium.webdriver.remote.webdriver',
        'selenium.webdriver.remote.webelement',
        'selenium.webdriver.remote.command',
        'selenium.webdriver.remote.remote_connection',
        'selenium.webdriver.remote.errorhandler',
        # Webdriver Manager
        'webdriver_manager',
        'webdriver_manager.chrome',
        'webdriver_manager.core.driver_cache',
        'webdriver_manager.core.download_manager',
        'webdriver_manager.core.os_manager',
        # Data
        'pandas', 'openpyxl', 'openpyxl.styles',
        # Analytics
        'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends.backend_qt5agg',
        'textblob',
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
)
