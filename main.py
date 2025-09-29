import sys
import time
import datetime
import hashlib
import json
import os
import sqlite3
from typing import Callable, List, Dict, Any, Set
import pandas as pd
from threading import Thread, Event
from urllib.parse import quote
from difflib import SequenceMatcher

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QDateEdit, QComboBox, QPushButton, QTextEdit, QSpinBox, QGridLayout, QGroupBox,
                             QTabWidget, QTableWidget, QTableWidgetItem, QProgressBar, QHBoxLayout, QCheckBox,
                             QFrame, QSplitter)
from PyQt5.QtCore import QDate, pyqtSignal, QObject, QSettings, Qt
from PyQt5.QtGui import QPalette, QColor

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# --- Constants ---
SCROLL_PAUSE_TIME = 5
WEBDRIVER_WAIT_TIMEOUT = 20
SESSION_INTERVAL_WAIT = 10
MAX_SCROLL_ATTEMPTS_WITHOUT_CHANGE = 3

# --- Deduplication System ---
class AdvancedDeduplicator:
    """Sistem deduplication canggih untuk tweet dengan multiple detection methods"""

    def __init__(self, db_path: str = "tweet_dedup.db", similarity_threshold: float = 0.85):
        self.db_path = db_path
        self.similarity_threshold = similarity_threshold
        self.session_hashes: Set[str] = set()
        self.session_urls: Set[str] = set()
        self.init_database()

    def init_database(self):
        """Inisialisasi database SQLite untuk persistent storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tweet_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_hash TEXT UNIQUE,
                    content_hash TEXT,
                    text_hash TEXT,
                    url TEXT,
                    username TEXT,
                    timestamp TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing database: {e}")

    def generate_hashes(self, tweet_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate multiple types of hashes for comprehensive deduplication"""
        url = tweet_data.get('url', '')
        text = tweet_data.get('tweet_text', '')
        username = tweet_data.get('username', '')
        timestamp = tweet_data.get('timestamp', '')

        # URL hash (primary identifier)
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()

        # Content hash (text + username for retweet detection)
        content_data = f"{text.lower().strip()}{username}"
        content_hash = hashlib.md5(content_data.encode('utf-8')).hexdigest()

        # Text-only hash (for similar content detection)
        text_normalized = ' '.join(text.lower().split())  # Normalize whitespace
        text_hash = hashlib.md5(text_normalized.encode('utf-8')).hexdigest()

        return {
            'url_hash': url_hash,
            'content_hash': content_hash,
            'text_hash': text_hash
        }

    def is_similar_text(self, text1: str, text2: str) -> bool:
        """Check if two texts are similar using sequence matching"""
        if not text1 or not text2:
            return False

        # Normalize texts
        text1_norm = ' '.join(text1.lower().split())
        text2_norm = ' '.join(text2.lower().split())

        # Calculate similarity ratio
        similarity = SequenceMatcher(None, text1_norm, text2_norm).ratio()
        return similarity >= self.similarity_threshold

    def is_duplicate(self, tweet_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Check if tweet is duplicate using multiple methods
        Returns: (is_duplicate, reason)
        """
        hashes = self.generate_hashes(tweet_data)
        url = tweet_data.get('url', '')
        text = tweet_data.get('tweet_text', '')

        # 1. Check session-level duplicates (in-memory)
        if hashes['url_hash'] in self.session_hashes:
            return True, "URL sudah ada dalam sesi ini"

        if url in self.session_urls:
            return True, "URL duplikat dalam sesi"

        # 2. Check database for persistent duplicates
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check URL hash
            cursor.execute("SELECT url FROM tweet_hashes WHERE url_hash = ?", (hashes['url_hash'],))
            if cursor.fetchone():
                conn.close()
                return True, "URL sudah ada dalam database"

            # Check content hash (exact content match)
            cursor.execute("SELECT url FROM tweet_hashes WHERE content_hash = ?", (hashes['content_hash'],))
            if cursor.fetchone():
                conn.close()
                return True, "Konten identik ditemukan"

            # Check for similar text content
            cursor.execute("SELECT url, username, timestamp FROM tweet_hashes WHERE text_hash = ?", (hashes['text_hash'],))
            similar_tweets = cursor.fetchall()

            for similar_url, similar_username, similar_timestamp in similar_tweets:
                # Additional similarity check for text_hash matches
                cursor.execute("SELECT url FROM tweet_hashes WHERE url = ?", (similar_url,))
                if cursor.fetchone():
                    conn.close()
                    return True, f"Teks serupa ditemukan dari @{similar_username}"

            conn.close()

        except Exception as e:
            print(f"Database error during duplicate check: {e}")

        return False, ""

    def add_tweet(self, tweet_data: Dict[str, Any]) -> bool:
        """Add tweet to deduplication system"""
        try:
            hashes = self.generate_hashes(tweet_data)

            # Add to session cache
            self.session_hashes.add(hashes['url_hash'])
            self.session_urls.add(tweet_data.get('url', ''))

            # Add to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO tweet_hashes
                (url_hash, content_hash, text_hash, url, username, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                hashes['url_hash'],
                hashes['content_hash'],
                hashes['text_hash'],
                tweet_data.get('url', ''),
                tweet_data.get('username', ''),
                tweet_data.get('timestamp', '')
            ))
            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error adding tweet to deduplication system: {e}")
            return False

    def get_stats(self) -> Dict[str, int]:
        """Get deduplication statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tweet_hashes")
            total_stored = cursor.fetchone()[0]
            conn.close()

            return {
                'session_count': len(self.session_hashes),
                'total_stored': total_stored,
                'session_urls': len(self.session_urls)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'session_count': 0, 'total_stored': 0, 'session_urls': 0}

    def clear_session(self):
        """Clear session-level cache"""
        self.session_hashes.clear()
        self.session_urls.clear()

    def cleanup_old_entries(self, days: int = 30):
        """Remove entries older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM tweet_hashes
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted
        except Exception as e:
            print(f"Error cleaning up old entries: {e}")
            return 0

# --- Progress Tracking System ---
class ProgressTracker:
    """Sistem tracking progress dengan estimasi waktu dan statistik performa"""

    def __init__(self):
        self.start_time = None
        self.session_start_time = None
        self.total_target = 0
        self.current_count = 0
        self.session_target = 0
        self.session_count = 0
        self.session_number = 0
        self.total_sessions = 0
        self.tweets_per_minute_history = []
        self.session_times = []

    def start_scraping(self, total_target: int, total_sessions: int):
        """Initialize tracking for entire scraping process"""
        self.start_time = time.time()
        self.total_target = total_target
        self.total_sessions = total_sessions
        self.current_count = 0
        self.session_number = 0
        self.tweets_per_minute_history.clear()
        self.session_times.clear()

    def start_session(self, session_target: int):
        """Initialize tracking for current session"""
        self.session_start_time = time.time()
        self.session_target = session_target
        self.session_count = 0
        self.session_number += 1

    def update_progress(self, current_session_count: int, total_count: int):
        """Update progress counters"""
        self.session_count = current_session_count
        self.current_count = total_count

    def get_current_speed(self) -> float:
        """Get current tweets per minute for this session"""
        if not self.session_start_time:
            return 0.0

        elapsed_minutes = (time.time() - self.session_start_time) / 60
        if elapsed_minutes == 0:
            return 0.0

        return self.session_count / elapsed_minutes

    def get_average_speed(self) -> float:
        """Get average tweets per minute across all sessions"""
        if not self.start_time:
            return 0.0

        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes == 0:
            return 0.0

        return self.current_count / elapsed_minutes

    def get_session_eta(self) -> str:
        """Get estimated time remaining for current session"""
        current_speed = self.get_current_speed()
        if current_speed == 0:
            return "Menghitung..."

        remaining_tweets = self.session_target - self.session_count
        if remaining_tweets <= 0:
            return "Selesai"

        eta_minutes = remaining_tweets / current_speed
        return self.format_time(eta_minutes * 60)

    def get_total_eta(self) -> str:
        """Get estimated time remaining for entire scraping process"""
        avg_speed = self.get_average_speed()
        if avg_speed == 0:
            return "Menghitung..."

        remaining_tweets = self.total_target - self.current_count
        if remaining_tweets <= 0:
            return "Selesai"

        eta_minutes = remaining_tweets / avg_speed
        return self.format_time(eta_minutes * 60)

    def finish_session(self):
        """Mark current session as finished and record statistics"""
        if self.session_start_time:
            session_duration = time.time() - self.session_start_time
            self.session_times.append(session_duration)

            if session_duration > 0:
                session_speed = self.session_count / (session_duration / 60)
                self.tweets_per_minute_history.append(session_speed)

    def get_progress_percentage(self) -> float:
        """Get overall progress percentage"""
        if self.total_target == 0:
            return 0.0
        return (self.current_count / self.total_target) * 100

    def get_session_percentage(self) -> float:
        """Get current session progress percentage"""
        if self.session_target == 0:
            return 0.0
        return (self.session_count / self.session_target) * 100

    def format_time(self, seconds: float) -> str:
        """Format seconds into readable time string"""
        if seconds < 60:
            return f"{int(seconds)}d"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}d"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}j {minutes}m"

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        current_speed = self.get_current_speed()
        avg_speed = self.get_average_speed()

        stats = {
            'current_speed': f"{current_speed:.1f} tweet/menit",
            'average_speed': f"{avg_speed:.1f} tweet/menit",
            'session_progress': f"{self.get_session_percentage():.1f}%",
            'total_progress': f"{self.get_progress_percentage():.1f}%",
            'session_eta': self.get_session_eta(),
            'total_eta': self.get_total_eta(),
            'session_number': f"{self.session_number}/{self.total_sessions}",
            'tweets_collected': f"{self.current_count}/{self.total_target}"
        }

        if self.session_times:
            avg_session_time = sum(self.session_times) / len(self.session_times)
            stats['avg_session_time'] = self.format_time(avg_session_time)

        if self.tweets_per_minute_history:
            best_speed = max(self.tweets_per_minute_history)
            stats['best_speed'] = f"{best_speed:.1f} tweet/menit"

        return stats

# --- Theme Management System ---
class ThemeManager:
    """Sistem manajemen tema dark/light dengan persistent storage"""

    def __init__(self):
        self.settings = QSettings("TweetScraper", "Themes")
        self.current_theme = self.settings.value("theme", "light", type=str)

    def get_light_theme(self) -> str:
        """Return light theme stylesheet"""
        return """
            QWidget {
                font-size: 14px;
                background-color: #ffffff;
                color: #333333;
            }
            QLabel {
                font-weight: bold;
                color: #333333;
            }
            QPushButton#startBtn {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                border: none;
            }
            QPushButton#startBtn:hover {
                background-color: #45a049;
            }
            QPushButton#startBtn:disabled {
                background-color: #A5D6A7;
            }
            QPushButton#stopBtn {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                border: none;
            }
            QPushButton#stopBtn:hover {
                background-color: #da190b;
            }
            QPushButton#stopBtn:disabled {
                background-color: #ef9a9a;
            }
            QPushButton#themeBtn {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-size: 14px;
            }
            QPushButton#themeBtn:hover {
                background-color: #1976D2;
            }
            QTextEdit, QTableWidget {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                color: #333333;
            }
            QLineEdit, QDateEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #ffffff;
                color: #333333;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                margin-bottom: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #4CAF50;
            }
        """

    def get_dark_theme(self) -> str:
        """Return dark theme stylesheet"""
        return """
            QWidget {
                font-size: 14px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton#startBtn {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                border: none;
            }
            QPushButton#startBtn:hover {
                background-color: #45a049;
            }
            QPushButton#startBtn:disabled {
                background-color: #2e5930;
            }
            QPushButton#stopBtn {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                border: none;
            }
            QPushButton#stopBtn:hover {
                background-color: #da190b;
            }
            QPushButton#stopBtn:disabled {
                background-color: #5c2e2e;
            }
            QPushButton#themeBtn {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
                font-size: 14px;
            }
            QPushButton#themeBtn:hover {
                background-color: #F57C00;
            }
            QTextEdit, QTableWidget {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                color: #ffffff;
            }
            QLineEdit, QDateEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #3c3c3c;
                color: #ffffff;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QProgressBar {
                text-align: center;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                margin-bottom: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                border-bottom: 2px solid #4CAF50;
            }
        """

    def get_current_theme_style(self) -> str:
        """Get current theme stylesheet"""
        if self.current_theme == "dark":
            return self.get_dark_theme()
        else:
            return self.get_light_theme()

    def toggle_theme(self) -> str:
        """Toggle between light and dark theme"""
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"

        # Save to settings
        self.settings.setValue("theme", self.current_theme)
        return self.current_theme

    def get_theme_button_text(self) -> str:
        """Get appropriate button text for current theme"""
        if self.current_theme == "light":
            return "🌙 Mode Gelap"
        else:
            return "☀️ Mode Terang"

def setup_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def _parse_tweet_article(tweet_article: Any, logger: Callable[[str], None]) -> Dict[str, Any] | None:
    try:
        tweet_url_elements = tweet_article.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
        tweet_url = tweet_url_elements[0].get_attribute('href') if tweet_url_elements else None
        if not tweet_url:
            return None

        username = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']//span").text
        handle = tweet_article.find_element(By.XPATH, ".//span[contains(text(), '@')]").text
        timestamp = tweet_article.find_element(By.XPATH, ".//time").get_attribute('datetime')
        tweet_text = tweet_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text.replace('\n', ' ')
        reply_count = tweet_article.find_element(By.XPATH, ".//button[@data-testid='reply']").text or "0"
        retweet_count = tweet_article.find_element(By.XPATH, ".//button[@data-testid='retweet']").text or "0"
        like_count = tweet_article.find_element(By.XPATH, ".//button[@data-testid='like']").text or "0"

        return {
            "username": username, "handle": handle, "timestamp": timestamp,
            "tweet_text": tweet_text, "url": tweet_url, "reply_count": reply_count,
            "retweet_count": retweet_count, "like_count": like_count
        }
    except (NoSuchElementException, StaleElementReferenceException) as e:
        logger(f"Peringatan: Gagal mem-parsing satu tweet, melompati. Kesalahan: {e}")
        return None

def scrape_tweets(driver: webdriver.Chrome, query: str, target_count: int, search_type: str, signals: 'LoggerSignals', stop_event: Event, deduplicator: AdvancedDeduplicator = None, progress_tracker: ProgressTracker = None) -> List[Dict[str, Any]]:
    search_url = f"https://x.com/search?q={query}&src=typed_query"
    if search_type == 'latest':
        search_url += "&f=live"

    signals.log_signal.emit(f"Mengunjungi halaman pencarian: {search_url}")
    driver.get(search_url)

    try:
        WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//article[@data-testid='tweet']"))
        )
        signals.log_signal.emit("Konten tweet terdeteksi. Memulai proses pengambilan data.")
    except TimeoutException:
        signals.log_signal.emit("Batas waktu menunggu habis. Tidak ada tweet yang ditemukan.")
        return []

    tweets_data: Dict[str, Dict[str, Any]] = {}
    duplicate_count = 0
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0

    # Initialize deduplicator if not provided
    if deduplicator is None:
        deduplicator = AdvancedDeduplicator()

    # Initialize progress tracker if not provided
    if progress_tracker is None:
        progress_tracker = ProgressTracker()

    progress_tracker.start_session(target_count)

    while len(tweets_data) < target_count:
        if stop_event.is_set():
            signals.log_signal.emit("Proses dihentikan oleh pengguna.")
            break

        # Update progress tracking
        progress_tracker.update_progress(len(tweets_data), len(tweets_data))
        stats = progress_tracker.get_statistics()

        signals.log_signal.emit(f"\nTweet: {len(tweets_data)}/{target_count} | Kecepatan: {stats['current_speed']} | ETA: {stats['session_eta']} | Duplikat: {duplicate_count}")
        signals.progress_signal.emit(len(tweets_data), target_count)
        signals.stats_signal.emit(stats)

        tweet_articles = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")

        for article in tweet_articles:
            if stop_event.is_set(): break
            parsed_data = _parse_tweet_article(article, signals.log_signal.emit)

            if parsed_data:
                # Check for duplicates using advanced system
                is_dup, reason = deduplicator.is_duplicate(parsed_data)

                if not is_dup and parsed_data["url"] not in tweets_data:
                    tweets_data[parsed_data["url"]] = parsed_data
                    deduplicator.add_tweet(parsed_data)
                    signals.data_row_signal.emit(parsed_data)
                elif is_dup:
                    duplicate_count += 1
                    if duplicate_count % 10 == 0:  # Log every 10 duplicates
                        signals.log_signal.emit(f"Duplikat terdeteksi: {reason}")
                elif parsed_data["url"] in tweets_data:
                    duplicate_count += 1

        if len(tweets_data) >= target_count:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            if scroll_attempts > MAX_SCROLL_ATTEMPTS_WITHOUT_CHANGE:
                signals.log_signal.emit("Berhenti scroll karena tinggi halaman tidak berubah.")
                break
        else:
            scroll_attempts = 0
        last_height = new_height

    signals.progress_signal.emit(len(tweets_data), target_count)

    # Finish session tracking
    progress_tracker.finish_session()

    # Log final statistics
    dedup_stats = deduplicator.get_stats()
    progress_stats = progress_tracker.get_statistics()

    signals.log_signal.emit(f"Sesi selesai - Waktu: {progress_stats.get('avg_session_time', 'N/A')} | Kecepatan: {progress_stats['current_speed']} | Duplikat: {duplicate_count}")
    signals.log_signal.emit(f"Database: {dedup_stats['total_stored']} tweet unik tersimpan")

    return list(tweets_data.values())[:target_count]

def main_scraping_function(keyword: str, target_per_session: int, start_date: datetime.date, end_date: datetime.date,
                           interval: int, lang: str, search_type: str, auth_token_cookie: str,
                           export_format: str, signals: 'LoggerSignals', stop_event: Event):
    if not auth_token_cookie:
        signals.log_signal.emit("Cookie tidak tersedia. Harap masukkan auth_token.")
        return

    # Initialize advanced deduplicator
    deduplicator = AdvancedDeduplicator()
    signals.log_signal.emit("Sistem deduplication canggih diinisialisasi.")

    # Initialize progress tracker
    progress_tracker = ProgressTracker()

    # Calculate total sessions and target
    total_days = (end_date - start_date).days + 1
    total_sessions = (total_days + interval - 1) // interval  # Ceiling division
    total_target = target_per_session * total_sessions

    progress_tracker.start_scraping(total_target, total_sessions)
    signals.log_signal.emit(f"Target: {total_target} tweet dalam {total_sessions} sesi")

    # Cleanup old entries (older than 30 days)
    cleaned = deduplicator.cleanup_old_entries(30)
    if cleaned > 0:
        signals.log_signal.emit(f"Membersihkan {cleaned} entri lama dari database.")

    driver = setup_driver()
    signals.log_signal.emit("Mengunjungi x.com dan menyuntikkan cookie...")
    driver.get("https://x.com")
    time.sleep(2)
    driver.add_cookie({'name': 'auth_token', 'value': auth_token_cookie, 'domain': '.x.com'})

    all_scraped_data = []
    current_date = start_date

    while current_date <= end_date:
        if stop_event.is_set():
            signals.log_signal.emit("Proses dihentikan sebelum sesi berikutnya.")
            break

        chunk_end_date = current_date + datetime.timedelta(days=interval)
        since_str = current_date.strftime('%Y-%m-%d')
        until_str = chunk_end_date.strftime('%Y-%m-%d')

        # Update progress tracker for overall progress
        progress_tracker.update_progress(0, len(all_scraped_data))
        overall_stats = progress_tracker.get_statistics()

        signals.log_signal.emit(f"\n--- Sesi {progress_tracker.session_number}/{total_sessions}: {since_str} hingga {until_str} ---")
        signals.log_signal.emit(f"Progress keseluruhan: {overall_stats['total_progress']} | ETA total: {overall_stats['total_eta']}")

        raw_query = f"{keyword} lang:{lang} until:{until_str} since:{since_str}"
        query = quote(raw_query)
        session_data = scrape_tweets(driver, query, target_per_session, search_type, signals, stop_event, deduplicator, progress_tracker)

        if session_data:
            all_scraped_data.extend(session_data)

        signals.log_signal.emit(f"Sesi selesai. Total tweet terkumpul: {len(all_scraped_data)}")
        current_date = chunk_end_date
        if current_date <= end_date and not stop_event.is_set():
            signals.log_signal.emit(f"Menunggu {SESSION_INTERVAL_WAIT} detik sebelum sesi berikutnya...")
            time.sleep(SESSION_INTERVAL_WAIT)

    if not all_scraped_data:
        signals.log_signal.emit("Tidak ada data yang terkumpul untuk disimpan.")
    else:
        df = pd.DataFrame(all_scraped_data)

        # Advanced deduplication already handled during scraping, but do final cleanup
        initial_count = len(df)
        df.drop_duplicates(subset=['url'], inplace=True)
        final_count = len(df)

        if initial_count != final_count:
            signals.log_signal.emit(f"Pembersihan akhir: {initial_count - final_count} duplikat tambahan dihapus.")

        # Get final deduplication stats
        final_stats = deduplicator.get_stats()
        signals.log_signal.emit(f"Total tweet unik dalam database: {final_stats['total_stored']}")

        safe_keyword = "".join(c for c in keyword if c.isalnum())
        base_filename = f"tweets_{safe_keyword}_{search_type}_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"

        try:
            if export_format == 'CSV':
                filename = f"{base_filename}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
            elif export_format == 'JSON':
                filename = f"{base_filename}.json"
                df.to_json(filename, orient='records', indent=4)
            elif export_format == 'Excel':
                filename = f"{base_filename}.xlsx"
                df.to_excel(filename, index=False)

            signals.log_signal.emit(f"\nData disimpan ke: {filename} ({len(df)} tweet unik)")
        except Exception as e:
            signals.log_signal.emit(f"\n!!! Gagal menyimpan file: {e} !!!")

    driver.quit()

class LoggerSignals(QObject):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    progress_signal = pyqtSignal(int, int)
    data_row_signal = pyqtSignal(dict)
    stats_signal = pyqtSignal(dict)  # New signal for progress statistics

class TweetScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tweet Scraper X.com - Enhanced Edition")
        self.setGeometry(100, 100, 1400, 700)  # Wider and shorter window

        self.scraping_thread = None
        self.stop_event = Event()

        # Initialize theme manager
        self.theme_manager = ThemeManager()

        self.signals = LoggerSignals()
        self.signals.log_signal.connect(self.append_log)
        self.signals.finished_signal.connect(self.on_scraping_finished)
        self.signals.progress_signal.connect(self.update_progress)
        self.signals.data_row_signal.connect(self.add_data_row)
        self.signals.stats_signal.connect(self.update_stats)

        # Main layout - horizontal split
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full use
        main_layout.setSpacing(5)  # Small spacing between panels
        self.setLayout(main_layout)

        # Apply initial theme
        self.setStyleSheet(self.theme_manager.get_current_theme_style())

        # Create left panel for controls and right panel for output
        self.create_left_panel()
        self.create_right_panel()

        # Add panels to main layout - left panel now takes more space for horizontal layout
        main_layout.addWidget(self.left_panel, 2)  # More space for horizontal sections
        main_layout.addWidget(self.right_panel, 1)  # Right panel takes remaining space

    def create_left_panel(self):
        """Create left panel with compact horizontal layout"""
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(800)  # Wider to accommodate horizontal layout
        self.left_panel.setMaximumWidth(1200)  # Increased max width
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)  # Add consistent spacing
        left_layout.setContentsMargins(15, 15, 15, 15)  # Add margins
        self.left_panel.setLayout(left_layout)

        # Header with theme toggle
        header_layout = QHBoxLayout()
        title_label = QLabel("Tweet Scraper")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.theme_button = QPushButton(self.theme_manager.get_theme_button_text())
        self.theme_button.setObjectName("themeBtn")
        self.theme_button.setFixedHeight(35)  # Fixed height for consistency
        self.theme_button.clicked.connect(self.toggle_theme)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_button)
        left_layout.addLayout(header_layout)

        # Row 1: Horizontal arrangement of main input sections
        self.create_horizontal_input_sections(left_layout)

        # Row 2: Control buttons
        self.create_control_section(left_layout)

        # Row 3: Progress section
        self.create_progress_section(left_layout)

        # Add stretch to push everything to top
        left_layout.addStretch()

    def create_horizontal_input_sections(self, parent_layout):
        """Create horizontal arrangement of input sections"""
        # Create horizontal layout for the main input sections
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(10)

        # Create each section as a widget
        search_widget = self.create_search_section_widget()
        date_widget = self.create_date_section_widget()
        options_widget = self.create_options_section_widget()
        auth_widget = self.create_auth_section_widget()

        # Add sections to horizontal layout
        horizontal_layout.addWidget(search_widget, 1)  # Give more space to search
        horizontal_layout.addWidget(date_widget, 1)
        horizontal_layout.addWidget(options_widget, 1)
        horizontal_layout.addWidget(auth_widget, 1)

        parent_layout.addLayout(horizontal_layout)

    def create_search_section_widget(self):
        """Create search parameters section as a widget"""
        search_group = QGroupBox("🔍 Parameter Pencarian")
        search_layout = QVBoxLayout()  # Changed to vertical for compact display
        search_layout.setSpacing(5)
        search_group.setLayout(search_layout)

        # Keyword
        search_layout.addWidget(QLabel("Kata Kunci:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Topik/hashtag...")
        self.keyword_input.setMinimumHeight(25)
        search_layout.addWidget(self.keyword_input)

        # Language
        search_layout.addWidget(QLabel("Bahasa:"))
        self.lang_input = QLineEdit("id")
        self.lang_input.setMinimumHeight(25)
        search_layout.addWidget(self.lang_input)

        # Search Type
        search_layout.addWidget(QLabel("Jenis:"))
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Top", "Terbaru"])
        self.search_type_combo.setMinimumHeight(25)
        search_layout.addWidget(self.search_type_combo)

        return search_group

    def create_date_section_widget(self):
        """Create date range section as a widget"""
        date_group = QGroupBox("📅 Rentang Waktu")
        date_layout = QVBoxLayout()
        date_layout.setSpacing(5)
        date_group.setLayout(date_layout)

        # Start date
        date_layout.addWidget(QLabel("Mulai:"))
        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setMinimumHeight(25)
        self.start_date_input.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_input)

        # End date
        date_layout.addWidget(QLabel("Selesai:"))
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setMinimumHeight(25)
        self.end_date_input.setCalendarPopup(True)
        date_layout.addWidget(self.end_date_input)

        # Interval
        date_layout.addWidget(QLabel("Interval (hari):"))
        self.interval_input = QSpinBox()
        self.interval_input.setMinimum(1)
        self.interval_input.setValue(1)
        self.interval_input.setMinimumHeight(25)
        self.interval_input.setMaximum(365)
        date_layout.addWidget(self.interval_input)

        return date_group

    def create_options_section_widget(self):
        """Create scraping options section as a widget"""
        options_group = QGroupBox("⚙️ Opsi Scraping")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(5)
        options_group.setLayout(options_layout)

        # Tweet count
        options_layout.addWidget(QLabel("Tweet/Sesi:"))
        self.count_input = QSpinBox()
        self.count_input.setRange(10, 1000)
        self.count_input.setValue(100)
        self.count_input.setMinimumHeight(25)
        self.count_input.setSuffix(" tweets")
        options_layout.addWidget(self.count_input)

        # Export format
        options_layout.addWidget(QLabel("Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "JSON", "Excel"])
        self.export_format_combo.setMinimumHeight(20)
        options_layout.addWidget(self.export_format_combo)

        return options_group

    def create_auth_section_widget(self):
        """Create authentication section as a widget"""
        auth_group = QGroupBox("🔐 Autentikasi")
        auth_layout = QVBoxLayout()
        auth_layout.setSpacing(5)
        auth_group.setLayout(auth_layout)

        auth_layout.addWidget(QLabel("Auth Token:"))
        self.cookie_input = QLineEdit()
        self.cookie_input.setEchoMode(QLineEdit.Password)
        self.cookie_input.setPlaceholderText("Token dari browser...")
        self.cookie_input.setMinimumHeight(25)
        auth_layout.addWidget(self.cookie_input)

        return auth_group







    def create_control_section(self, parent_layout):
        """Create control buttons section - horizontal layout"""
        control_group = QGroupBox("🎮 Kontrol")
        control_layout = QHBoxLayout()  # Changed to horizontal
        control_layout.setSpacing(15)  # Add spacing between buttons
        control_group.setLayout(control_layout)

        # Start and Stop buttons side by side
        self.start_button = QPushButton("▶️ Mulai Scraping")
        self.start_button.setObjectName("startBtn")
        self.start_button.setMinimumHeight(40)  # Larger buttons
        self.start_button.clicked.connect(self.start_scraping)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("⏹️ Stop Scraping")
        self.stop_button.setObjectName("stopBtn")
        self.stop_button.setMinimumHeight(40)  # Larger buttons
        self.stop_button.clicked.connect(self.stop_scraping)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        parent_layout.addWidget(control_group)

    def create_progress_section(self, parent_layout):
        """Create compact horizontal progress section"""
        progress_group = QGroupBox("📊 Progress")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)
        progress_group.setLayout(progress_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        progress_layout.addWidget(self.progress_bar)

        # Horizontal statistics layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        self.stats_labels = {
            'current_speed': QLabel("⚡ Kecepatan: -"),
            'session_eta': QLabel("⏱️ ETA: -"),
            'tweets_collected': QLabel("📊 Tweet: 0/0"),
            'total_progress': QLabel("📈 Total: 0%")
        }

        # Style the labels for better readability
        for label in self.stats_labels.values():
            label.setStyleSheet("font-size: 11px; padding: 3px; border: 1px solid #ddd; border-radius: 3px;")

        # Arrange horizontally
        stats_layout.addWidget(self.stats_labels['current_speed'])
        stats_layout.addWidget(self.stats_labels['session_eta'])
        stats_layout.addWidget(self.stats_labels['tweets_collected'])
        stats_layout.addWidget(self.stats_labels['total_progress'])

        progress_layout.addLayout(stats_layout)
        parent_layout.addWidget(progress_group)

    def create_right_panel(self):
        """Create right panel with output and data display"""
        self.right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 15, 15, 15)  # Add margins
        right_layout.setSpacing(10)
        self.right_panel.setLayout(right_layout)

        # Tabs for log and data
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(400)  # Set minimum height for tabs

        # Log tab
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(self.log_output.font())  # Use system font
        self.tabs.addTab(self.log_output, "📝 Log")

        # Data preview tab
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)  # Better readability
        self.tabs.addTab(self.data_table, "📋 Data Preview")

        # Add status bar at bottom
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 5, 5, 5)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 8px; border-top: 1px solid #ccc; font-size: 12px; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # Add database info
        self.db_status_label = QLabel("Database: Ready")
        self.db_status_label.setStyleSheet("padding: 8px; font-size: 12px; color: #666;")
        status_layout.addWidget(self.db_status_label)

        right_layout.addWidget(self.tabs, 1)  # Give tabs stretch factor
        right_layout.addLayout(status_layout)

    def setup_table(self):
        self.data_table.setColumnCount(8)
        self.data_table.setHorizontalHeaderLabels(["Username", "Handle", "Timestamp", "Tweet Text", "URL", "Replies", "Retweets", "Likes"])
        self.data_table.setColumnWidth(3, 300)

    def add_data_row(self, data: Dict[str, Any]):
        row_position = self.data_table.rowCount()
        self.data_table.insertRow(row_position)
        self.data_table.setItem(row_position, 0, QTableWidgetItem(data.get("username")))
        self.data_table.setItem(row_position, 1, QTableWidgetItem(data.get("handle")))
        self.data_table.setItem(row_position, 2, QTableWidgetItem(data.get("timestamp")))
        self.data_table.setItem(row_position, 3, QTableWidgetItem(data.get("tweet_text")))
        self.data_table.setItem(row_position, 4, QTableWidgetItem(data.get("url")))
        self.data_table.setItem(row_position, 5, QTableWidgetItem(data.get("reply_count")))
        self.data_table.setItem(row_position, 6, QTableWidgetItem(data.get("retweet_count")))
        self.data_table.setItem(row_position, 7, QTableWidgetItem(data.get("like_count")))

    def update_progress(self, value, maximum):
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def update_stats(self, stats: Dict[str, Any]):
        """Update progress statistics display"""
        # Update horizontal stats display
        if 'current_speed' in stats:
            self.stats_labels['current_speed'].setText(f"⚡ Kecepatan: {stats['current_speed']}")
        if 'session_eta' in stats:
            self.stats_labels['session_eta'].setText(f"⏱️ ETA: {stats['session_eta']}")
        if 'tweets_collected' in stats:
            self.stats_labels['tweets_collected'].setText(f"📊 Tweet: {stats['tweets_collected']}")
        if 'total_progress' in stats:
            self.stats_labels['total_progress'].setText(f"📈 Total: {stats['total_progress']}")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        new_theme = self.theme_manager.toggle_theme()
        self.setStyleSheet(self.theme_manager.get_current_theme_style())
        self.theme_button.setText(self.theme_manager.get_theme_button_text())
        self.append_log(f"Tema diubah ke: {new_theme}")

    def append_log(self, text: str):
        self.log_output.append(text)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

        # Update status bar with latest activity
        if "tweet" in text.lower():
            self.status_label.setText("Scraping in progress...")
        elif "selesai" in text.lower():
            self.status_label.setText("Scraping completed")
        elif "error" in text.lower() or "gagal" in text.lower():
            self.status_label.setText("Error occurred")

    def update_database_status(self, count: int):
        """Update database status in status bar"""
        self.db_status_label.setText(f"Database: {count} tweets stored")

    def on_scraping_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.append_log("\n--- Proses Selesai ---")
        if self.progress_bar.value() < self.progress_bar.maximum():
             self.append_log("Proses mungkin tidak selesai sepenuhnya atau dihentikan.")
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.scraping_thread = None

    def stop_scraping(self):
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.stop_event.set()
            self.stop_button.setEnabled(False)
            self.append_log("\n--- Mengirim sinyal berhenti... ---")

    def start_scraping(self):
        # Validation
        if not self.keyword_input.text().strip():
            self.append_log("❌ Error: Kata kunci tidak boleh kosong!")
            return

        if not self.cookie_input.text().strip():
            self.append_log("❌ Error: Auth token cookie diperlukan!")
            return

        self.log_output.clear()
        self.data_table.setRowCount(0)
        self.setup_table()
        self.progress_bar.setValue(0)
        self.stop_event.clear()

        # Update status
        self.status_label.setText("Initializing scraping...")

        keyword = self.keyword_input.text().strip()
        start_date = self.start_date_input.date().toPyDate()
        end_date = self.end_date_input.date().toPyDate()
        interval = self.interval_input.value()
        lang = self.lang_input.text().strip()
        count = self.count_input.value()
        search_type = 'latest' if self.search_type_combo.currentIndex() == 1 else 'top'
        auth_token = self.cookie_input.text().strip()
        export_format = self.export_format_combo.currentText()

        args = {
            "keyword": keyword,
            "target_per_session": count,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "lang": lang,
            "search_type": search_type,
            "auth_token_cookie": auth_token,
            "export_format": export_format,
            "signals": self.signals,
            "stop_event": self.stop_event
        }

        self.append_log("🚀 Memulai scraping...")
        self.append_log(f"📋 Target: {count} tweet per sesi")
        self.append_log(f"📅 Periode: {start_date} hingga {end_date}")
        self.append_log(f"🔍 Kata kunci: {keyword}")

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Scraping started...")

        self.scraping_thread = Thread(target=self.run_scraper_thread, args=(args,))
        self.scraping_thread.start()

    def run_scraper_thread(self, args: Dict[str, Any]):
        try:
            main_scraping_function(**args)
        except Exception as e:
            self.signals.log_signal.emit(f"\n!!! Terjadi kesalahan fatal: {e} !!!")
        finally:
            self.signals.finished_signal.emit()

def run_app():
    app = QApplication(sys.argv)
    window = TweetScraperGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
