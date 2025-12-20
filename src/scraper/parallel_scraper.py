"""
Parallel Scraper untuk multi-threading scraping.
"""

from typing import Dict, List, Any, Optional
from threading import Thread, Lock, Event
from queue import Queue
import time
from datetime import datetime, timedelta

from selenium import webdriver
from ..config.constants import SCROLL_PAUSE_TIME
from ..core import AdvancedDeduplicator, ProgressTracker
from .driver_setup import setup_driver
from .tweet_scraper import scrape_tweets


class ParallelScraper:
    """
    Scraper paralel dengan multiple browser instances.

    Menggunakan thread pool untuk scraping paralel, meningkatkan
    kecepatan scraping hingga 3-5x lebih cepat.

    Features:
    - Multiple browser instances (configurable)
    - Task queue distribution
    - Thread-safe deduplication
    - Progress aggregation
    - Auto error recovery

    Example:
        >>> scraper = ParallelScraper(num_threads=3)
        >>> results = scraper.scrape_parallel(
        ...     keyword="python",
        ...     date_ranges=[...],
        ...     target_per_session=100
        ... )
    """

    def __init__(self, num_threads: int = 2, signals=None, stop_event: Event = None):
        """
        Inisialisasi Parallel Scraper.

        Args:
            num_threads (int): Jumlah thread/browser instances (default: 2)
            signals: PyQt signals untuk logging
            stop_event (Event): Event untuk stop scraping
        """
        self.num_threads = min(num_threads, 5)  # Max 5 threads untuk safety
        self.signals = signals
        self.stop_event = stop_event or Event()

        # Thread-safe components
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.lock = Lock()

        # Shared deduplicator (thread-safe dengan lock)
        self.deduplicator = AdvancedDeduplicator()

        # Statistics
        self.total_scraped = 0
        self.active_threads = 0
        self.errors = []

    def log(self, message: str):
        """Thread-safe logging."""
        if self.signals:
            self.signals.log_signal.emit(message)
        else:
            print(message)

    def scrape_parallel(
        self,
        keyword: str,
        date_ranges: List[tuple],
        target_per_session: int,
        lang: str = "id",
        search_type: str = "top",
        auth_token: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Scraping paralel dengan multiple threads.

        Args:
            keyword (str): Kata kunci pencarian
            date_ranges (List[tuple]): List of (start_date, end_date) tuples
            target_per_session (int): Target tweet per session
            lang (str): Bahasa
            search_type (str): Tipe pencarian
            auth_token (str): Auth token

        Returns:
            List[Dict[str, Any]]: List semua tweet yang berhasil di-scrape
        """
        self.log(f"🚀 Memulai parallel scraping dengan {self.num_threads} threads...")

        # Pre-install ChromeDriver sebelum threads dimulai (thread-safe)
        # Ini mencegah race condition saat semua worker mencoba install bersamaan
        from .driver_setup import get_driver_path
        self.log("📥 Menyiapkan ChromeDriver...")
        get_driver_path()  # Install dan cache driver path
        self.log("✅ ChromeDriver siap digunakan")

        # Populate task queue
        for idx, (start_date, end_date) in enumerate(date_ranges):
            task = {
                'session_id': idx + 1,
                'keyword': keyword,
                'start_date': start_date,
                'end_date': end_date,
                'target': target_per_session,
                'lang': lang,
                'search_type': search_type,
                'auth_token': auth_token
            }
            self.task_queue.put(task)

        self.log(f"📋 Total {len(date_ranges)} sesi akan di-scrape secara paralel")

        # Start worker threads
        threads = []
        for i in range(self.num_threads):
            thread = Thread(target=self._worker, args=(i + 1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            self.active_threads += 1

        # Wait for all tasks to complete
        self.task_queue.join()

        # Stop all threads
        for _ in range(self.num_threads):
            self.task_queue.put(None)  # Poison pill

        for thread in threads:
            thread.join()

        # Collect all results
        all_tweets = []
        while not self.result_queue.empty():
            tweets = self.result_queue.get()
            all_tweets.extend(tweets)

        self.log(f"✅ Parallel scraping selesai! Total: {len(all_tweets)} tweets")

        if self.errors:
            self.log(f"⚠️ {len(self.errors)} error terjadi selama scraping")

        return all_tweets

    def _worker(self, worker_id: int):
        """
        Worker thread untuk scraping.

        Args:
            worker_id (int): ID worker thread
        """
        self.log(f"🔧 Worker #{worker_id} started")
        driver = None

        try:
            # Setup driver untuk worker ini
            driver = setup_driver()
            self.log(f"✅ Worker #{worker_id} driver ready")

            while not self.stop_event.is_set():
                # Get task from queue
                task = self.task_queue.get()

                if task is None:  # Poison pill
                    break

                try:
                    self.log(f"🔄 Worker #{worker_id} processing session {task['session_id']}")

                    # Scrape tweets untuk task ini
                    tweets = self._scrape_session(driver, task, worker_id)

                    # Put results in result queue
                    self.result_queue.put(tweets)

                    with self.lock:
                        self.total_scraped += len(tweets)

                    self.log(f"✅ Worker #{worker_id} selesai session {task['session_id']}: {len(tweets)} tweets")

                except Exception as e:
                    error_msg = f"❌ Worker #{worker_id} error pada session {task['session_id']}: {e}"
                    self.log(error_msg)
                    self.errors.append(error_msg)
                    self.result_queue.put([])  # Empty result

                finally:
                    self.task_queue.task_done()

        except Exception as e:
            self.log(f"❌ Worker #{worker_id} fatal error: {e}")

        finally:
            if driver:
                try:
                    driver.quit()
                    self.log(f"🔧 Worker #{worker_id} driver closed")
                except:
                    pass

            with self.lock:
                self.active_threads -= 1

    def _scrape_session(
        self,
        driver: webdriver.Chrome,
        task: Dict[str, Any],
        worker_id: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape satu session dengan driver yang diberikan.

        Args:
            driver: WebDriver instance
            task: Task dictionary
            worker_id: ID worker

        Returns:
            List[Dict[str, Any]]: List tweets
        """
        # Build Query String
        from urllib.parse import quote

        # Construct raw query like main_scraping_function does
        start_date_str = task['start_date'].strftime('%Y-%m-%d')
        end_date_str = task['end_date'].strftime('%Y-%m-%d')

        raw_query = f"{task['keyword']} lang:{task['lang']} until:{end_date_str} since:{start_date_str}"
        query_encoded = quote(raw_query)

        # Set auth cookie
        driver.get("https://x.com")
        driver.add_cookie({
            'name': 'auth_token',
            'value': task['auth_token'],
            'domain': '.x.com'
        })

        # Scrape tweets
        # scrape_tweets will handle navigation to search URL
        tweets = scrape_tweets(
            driver=driver,
            query=query_encoded,
            target_count=task['target'],
            search_type=task['search_type'],
            signals=self.signals,
            stop_event=self.stop_event,
            deduplicator=self.deduplicator,
            lock=self.lock,
            worker_id=worker_id
        )

        return tweets

    def get_stats(self) -> Dict[str, Any]:
        """
        Dapatkan statistik scraping.

        Returns:
            Dict[str, Any]: Statistik scraping
        """
        return {
            'total_scraped': self.total_scraped,
            'active_threads': self.active_threads,
            'errors_count': len(self.errors),
            'dedup_stats': self.deduplicator.get_stats()
        }
