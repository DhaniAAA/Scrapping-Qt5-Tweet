"""
WebDriver setup and configuration.
"""

from threading import Lock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from ..config.constants import DEFAULT_USER_AGENT


# Global cache for ChromeDriver path
_DRIVER_PATH_CACHE = None
_DRIVER_PATH_LOCK = Lock()


def get_driver_path() -> str:
    """
    Thread-safe ChromeDriver installation dan caching.

    Install ChromeDriver hanya sekali, kemudian reuse path untuk semua threads.
    Ini mencegah race condition dan file access conflicts.

    Returns:
        str: Path ke ChromeDriver executable
    """
    global _DRIVER_PATH_CACHE

    # Double-checked locking pattern untuk performa
    if _DRIVER_PATH_CACHE is None:
        with _DRIVER_PATH_LOCK:
            # Check lagi di dalam lock (another thread might have initialized)
            if _DRIVER_PATH_CACHE is None:
                _DRIVER_PATH_CACHE = ChromeDriverManager().install()

    return _DRIVER_PATH_CACHE


def setup_driver() -> webdriver.Chrome:
    """
    Setup and configure Chrome WebDriver for scraping.

    Thread-safe: Menggunakan cached driver path untuk menghindari
    race condition saat multiple threads memanggil fungsi ini.

    Returns:
        webdriver.Chrome: Instance WebDriver Chrome yang sudah dikonfigurasi
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument(f'user-agent={DEFAULT_USER_AGENT}')

    # Gunakan cached driver path (thread-safe)
    service = Service(get_driver_path())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
