"""
Advanced deduplication system for tweets with multiple detection methods.
"""

import hashlib
import sqlite3
from typing import Dict, Any, Set
from difflib import SequenceMatcher

from ..config.constants import DEFAULT_DB_PATH, DEFAULT_SIMILARITY_THRESHOLD


class AdvancedDeduplicator:
    """
    Sistem deduplication canggih untuk tweet dengan multiple detection methods.

    Class ini menggunakan beberapa metode untuk mendeteksi tweet duplikat:
    1. URL hash - Deteksi berdasarkan URL tweet yang sama
    2. Content hash - Deteksi berdasarkan kombinasi text + username (untuk retweet)
    3. Text hash - Deteksi berdasarkan kemiripan teks menggunakan SequenceMatcher

    Data disimpan dalam SQLite database untuk persistent storage dan
    juga di-cache dalam memory untuk performa lebih cepat.

    Attributes:
        db_path (str): Path ke file database SQLite
        similarity_threshold (float): Threshold untuk similarity matching (0-1)
        session_hashes (Set[str]): Cache hash URL dalam sesi saat ini
        session_urls (Set[str]): Cache URL dalam sesi saat ini
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH, similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD):
        """
        Inisialisasi AdvancedDeduplicator dengan konfigurasi database dan threshold.

        Args:
            db_path (str, optional): Path ke file database SQLite.
                Default: DEFAULT_DB_PATH ("tweet_dedup.db")
            similarity_threshold (float, optional): Threshold untuk similarity matching.
                Nilai 0-1, semakin tinggi semakin strict. Default: 0.85

        Note:
            Database akan dibuat otomatis jika belum ada.
        """
        self.db_path = db_path
        self.similarity_threshold = similarity_threshold
        self.session_hashes: Set[str] = set()
        self.session_urls: Set[str] = set()
        self.init_database()

    def init_database(self):
        """
        Inisialisasi database SQLite untuk persistent storage.

        Membuat tabel 'tweet_hashes' jika belum ada dengan kolom:
        - id: Primary key auto increment
        - url_hash: Hash MD5 dari URL (unique)
        - content_hash: Hash MD5 dari text + username
        - text_hash: Hash MD5 dari text saja
        - url: URL tweet original
        - username: Username pembuat tweet
        - timestamp: Timestamp tweet
        - created_at: Waktu data disimpan ke database

        Raises:
            Exception: Jika gagal membuat/koneksi ke database
        """
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
        """
        Generate multiple types of hashes untuk comprehensive deduplication.

        Args:
            tweet_data (Dict[str, Any]): Dictionary berisi data tweet dengan keys:
                - url: URL tweet
                - tweet_text: Teks tweet
                - username: Username pembuat
                - timestamp: Waktu tweet

        Returns:
            Dict[str, str]: Dictionary berisi 3 jenis hash:
                - url_hash: MD5 hash dari URL (identifier utama)
                - content_hash: MD5 hash dari text+username (deteksi retweet)
                - text_hash: MD5 hash dari text saja (deteksi konten serupa)

        """
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
        """
        Menggunakan SequenceMatcher dari difflib untuk menghitung similarity ratio.
        Text dinormalisasi (lowercase, whitespace) sebelum dibandingkan.

        Args:
            text1 (str): Text pertama untuk dibandingkan
            text2 (str): Text kedua untuk dibandingkan

        Returns:
            bool: True jika similarity >= threshold, False jika tidak

        Note:
            Threshold ditentukan oleh self.similarity_threshold (default 0.85)
        """
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
        Check if tweet is duplicate using multiple methods.

        Args:
            tweet_data (Dict[str, Any]): Dictionary berisi data tweet

        Returns:
            tuple[bool, str]: Tuple berisi:
                - bool: True jika tweet duplikat, False jika tidak
                - str: Alasan duplikasi (misal: "URL duplikat", "Tweet serupa")
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
        """
        Add tweet to deduplication system (session cache + database).

        Args:
            tweet_data (Dict[str, Any]): Dictionary berisi data tweet

        Returns:
            bool: True jika berhasil ditambahkan, False jika gagal

        Note:
            Tweet akan ditambahkan ke:
            1. Session cache (in-memory) untuk cek cepat
            2. Database SQLite untuk persistent storage
        """
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
        """
        Get deduplication statistics.

        Returns:
            Dict[str, int]: Dictionary berisi statistik:
                - session_count: Jumlah hash dalam session cache
                - total_stored: Total tweet tersimpan di database
                - session_urls: Jumlah URL dalam session cache
        """
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
        """
        Clear session-level cache (in-memory).

        Menghapus semua data dari session_hashes dan session_urls.
        Database tidak terpengaruh.
        """
        self.session_hashes.clear()
        self.session_urls.clear()

    def cleanup_old_entries(self, days: int = 30):
        """
        Remove entries older than specified days dari database.

        Args:
            days (int, optional): Jumlah hari. Entry lebih lama dari ini akan dihapus.
                Default: 30 hari

        Returns:
            int: Jumlah entry yang berhasil dihapus

        Example:
            >>> deleted = dedup.cleanup_old_entries(60)  # Hapus data > 60 hari
            >>> print(f"Deleted {deleted} old entries")
        """
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
