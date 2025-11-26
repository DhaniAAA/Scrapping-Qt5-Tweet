"""
WebDriver setup and configuration.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from ..config.constants import DEFAULT_USER_AGENT


def setup_driver() -> webdriver.Chrome:
    """
    Setup and configure Chrome WebDriver for scraping.

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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
