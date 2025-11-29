"""
Constants and configuration values for Tweet Scraper.

Module ini berisi semua konstanta yang digunakan di seluruh aplikasi.
Ubah nilai di sini untuk mengkonfigurasi behavior aplikasi.
"""

# ==================== Scraping Configuration ====================
# Konfigurasi untuk proses scraping tweet

SCROLL_PAUSE_TIME = 5
"""int: Waktu jeda (detik) setelah scroll halaman untuk loading konten baru"""

WEBDRIVER_WAIT_TIMEOUT = 20
"""int: Maksimal waktu tunggu (detik) untuk WebDriver menunggu elemen muncul"""

SESSION_INTERVAL_WAIT = 10
"""int: Waktu jeda (detik) antar sesi scraping untuk menghindari rate limit"""

MAX_SCROLL_ATTEMPTS_WITHOUT_CHANGE = 3
"""int: Maksimal percobaan scroll tanpa perubahan tinggi halaman sebelum berhenti"""


# ==================== Database Configuration ====================
# Konfigurasi untuk sistem deduplication database

DEFAULT_DB_PATH = "tweet_dedup.db"
"""str: Path file database SQLite untuk menyimpan hash tweet"""

DEFAULT_SIMILARITY_THRESHOLD = 0.85
"""float: Threshold similarity (0-1) untuk deteksi tweet serupa.
Semakin tinggi = semakin strict"""

DEFAULT_CLEANUP_DAYS = 30
"""int: Jumlah hari untuk menyimpan data lama sebelum dibersihkan otomatis"""


# ==================== User Agent ====================
# User agent untuk WebDriver agar terlihat seperti browser normal

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
"""str: User agent string untuk Chrome WebDriver"""


# ==================== Window Configuration ====================
# Konfigurasi ukuran window GUI aplikasi

WINDOW_WIDTH = 1366
"""int: Lebar default window aplikasi (pixels)"""

WINDOW_HEIGHT = 768
"""int: Tinggi default window aplikasi (pixels)"""

MIN_LEFT_PANEL_WIDTH = 768
"""int: Lebar minimum panel kiri (pixels)"""

MAX_LEFT_PANEL_WIDTH = 1366
"""int: Lebar maksimum panel kiri (pixels)"""
