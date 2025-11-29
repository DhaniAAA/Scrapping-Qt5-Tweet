"""
Main tweet scraping functionality.
"""

import time
import datetime
from typing import List, Dict, Any
from threading import Event
from urllib.parse import quote

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..config.constants import (
    SCROLL_PAUSE_TIME,
    WEBDRIVER_WAIT_TIMEOUT,
    SESSION_INTERVAL_WAIT,
    MAX_SCROLL_ATTEMPTS_WITHOUT_CHANGE,
    DEFAULT_CLEANUP_DAYS
)
from ..core import AdvancedDeduplicator, ProgressTracker
from .driver_setup import setup_driver
from .tweet_parser import parse_tweet_article


def scrape_tweets(
    driver: webdriver.Chrome,
    query: str,
    target_count: int,
    search_type: str,
    signals: 'LoggerSignals',
    stop_event: Event,
    deduplicator: AdvancedDeduplicator = None,
    progress_tracker: ProgressTracker = None,
    lock: Any = None,
    worker_id: int = 0
) -> List[Dict[str, Any]]:
    """
    Scrape tweets from X.com based on search query.

    Args:
        driver: Selenium WebDriver instance
        query: URL-encoded search query
        target_count: Number of tweets to collect
        search_type: 'top' or 'latest'
        signals: Qt signals for GUI updates
        stop_event: Threading event to stop scraping
        deduplicator: Deduplication system instance
        progress_tracker: Progress tracking instance
        lock: Threading lock for thread safety
        worker_id: ID of the worker thread (0 for main thread)

    Returns:
        List of tweet dictionaries
    """
    prefix = f"[Worker {worker_id}] " if worker_id > 0 else ""

    search_url = f"https://x.com/search?q={query}&src=typed_query"
    if search_type == 'latest':
        search_url += "&f=live"

    signals.log_signal.emit(f"{prefix}Mengunjungi halaman pencarian: {search_url}")
    driver.get(search_url)

    try:
        WebDriverWait(driver, WEBDRIVER_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//article[@data-testid='tweet']"))
        )
        signals.log_signal.emit(f"{prefix}Konten tweet terdeteksi. Memulai proses pengambilan data.")
    except TimeoutException:
        signals.log_signal.emit(f"{prefix}Batas waktu menunggu habis. Tidak ada tweet yang ditemukan.")
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

    # Only start session tracking if running single threaded or if this is the main tracker
    # For parallel, the main process handles overall progress
    if worker_id == 0:
        progress_tracker.start_session(target_count)

    while len(tweets_data) < target_count:
        if stop_event.is_set():
            signals.log_signal.emit(f"{prefix}Proses dihentikan oleh pengguna.")
            break

        # Update progress tracking
        if worker_id == 0:
            progress_tracker.update_progress(len(tweets_data), len(tweets_data))
            stats = progress_tracker.get_statistics()
            signals.log_signal.emit(f"\nTweet: {len(tweets_data)}/{target_count} | Kecepatan: {stats['current_speed']} | ETA: {stats['session_eta']} | Duplikat: {duplicate_count}")
            signals.progress_signal.emit(len(tweets_data), target_count)
            signals.stats_signal.emit(stats)
        elif len(tweets_data) % 10 == 0 and len(tweets_data) > 0:
             signals.log_signal.emit(f"{prefix}Collected: {len(tweets_data)}/{target_count}")

        tweet_articles = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")

        for article in tweet_articles:
            if stop_event.is_set():
                break

            # Use a local log function that includes prefix
            def log_func(msg):
                # signals.log_signal.emit(f"{prefix}{msg}")
                pass # Reduce verbosity during parsing

            parsed_data = parse_tweet_article(article, log_func)

            if parsed_data:
                # Check for duplicates using advanced system
                # Use lock if provided
                if lock:
                    with lock:
                        is_dup, reason = deduplicator.is_duplicate(parsed_data)
                else:
                    is_dup, reason = deduplicator.is_duplicate(parsed_data)

                if not is_dup and parsed_data["url"] not in tweets_data:
                    tweets_data[parsed_data["url"]] = parsed_data

                    if lock:
                        with lock:
                            deduplicator.add_tweet(parsed_data)
                    else:
                        deduplicator.add_tweet(parsed_data)

                    # Emit data row signal for all workers
                    signals.data_row_signal.emit(parsed_data)

                elif is_dup:
                    duplicate_count += 1
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


def main_scraping_function(
    keyword: str,
    target_per_session: int,
    start_date: datetime.date,
    end_date: datetime.date,
    interval: int,
    lang: str,
    search_type: str,
    auth_token_cookie: str,
    export_format: str,
    signals: 'LoggerSignals',
    stop_event: Event
):
    """
    Args:
        keyword: Kata kunci/tagar pencarian
        target_per_session: Jumlah tweet yang akan dikumpulkan per sesi
        start_date: Tanggal mulai pengikisan
        end_date: Tanggal berakhir pengikisan
        interval: Jumlah hari per sesi
        lang: Kode bahasa (misalnya, 'id', 'en')
        search_type: 'top' atau 'latest'
        auth_token_cookie: Token autentikasi dari peramban
        export_format: 'CSV', 'JSON', atau 'Excel'
        signals: Sinyal Qt untuk pembaruan GUI
        stop_event: Peristiwa threading untuk menghentikan pengikisan
    """
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
    cleaned = deduplicator.cleanup_old_entries(DEFAULT_CLEANUP_DAYS)
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
