"""
Progress tracking system with time estimation and performance statistics.
"""

import time
from typing import Dict, Any


class ProgressTracker:
    """
    Sistem tracking progress dengan estimasi waktu dan statistik performa.

    Class ini melacak progress scraping dan menghitung:
    - Kecepatan scraping (tweets per minute)
    - Estimasi waktu selesai (ETA)
    - Progress percentage
    - Statistik performa (best speed, avg time, dll)

    Attributes:
        start_time (float): Waktu mulai scraping keseluruhan
        session_start_time (float): Waktu mulai sesi saat ini
        total_target (int): Target total tweet untuk semua sesi
        current_count (int): Jumlah tweet terkumpul saat ini
        session_target (int): Target tweet untuk sesi saat ini
        session_count (int): Jumlah tweet terkumpul di sesi ini
        session_number (int): Nomor sesi saat ini
        total_sessions (int): Total jumlah sesi
        tweets_per_minute_history (List[float]): History kecepatan per sesi
        session_times (List[float]): History durasi per sesi
    """

    def __init__(self):
        """
        Inisialisasi ProgressTracker dengan nilai default.

        Semua counter dimulai dari 0/None.
        """
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
        """
        Initialize tracking untuk entire scraping process.

        Args:
            total_target (int): Total tweet yang ingin dikumpulkan
            total_sessions (int): Total jumlah sesi scraping

        Note:
            Method ini harus dipanggil sebelum mulai scraping.
        """
        self.start_time = time.time()
        self.total_target = total_target
        self.total_sessions = total_sessions
        self.current_count = 0
        self.session_number = 0
        self.tweets_per_minute_history.clear()
        self.session_times.clear()

    def start_session(self, session_target: int):
        """
        Initialize tracking untuk sesi saat ini.

        Args:
            session_target (int): Target tweet untuk sesi ini

        Note:
            Session number akan otomatis increment.
        """
        self.session_start_time = time.time()
        self.session_target = session_target
        self.session_count = 0
        self.session_number += 1

    def update_progress(self, current_session_count: int, total_count: int):
        """
        Update progress counters.

        Args:
            current_session_count (int): Jumlah tweet di sesi ini
            total_count (int): Total tweet terkumpul keseluruhan
        """
        self.session_count = current_session_count
        self.current_count = total_count

    def get_current_speed(self) -> float:
        """
        Get kecepatan scraping saat ini (tweets per minute) untuk sesi ini.

        Returns:
            float: Tweets per minute, atau 0.0 jika belum ada data
        """
        if not self.session_start_time:
            return 0.0

        elapsed_minutes = (time.time() - self.session_start_time) / 60
        if elapsed_minutes == 0:
            return 0.0

        return self.session_count / elapsed_minutes

    def get_average_speed(self) -> float:
        """
        Get rata-rata kecepatan scraping (tweets per minute) untuk semua sesi.

        Returns:
            float: Average tweets per minute, atau 0.0 jika belum ada data
        """
        if not self.start_time:
            return 0.0

        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes == 0:
            return 0.0

        return self.current_count / elapsed_minutes

    def get_session_eta(self) -> str:
        """
        Get estimasi waktu remaining untuk sesi saat ini.

        Returns:
            str: ETA dalam format readable (e.g., "5m 30d", "2j 15m")
                 atau "Menghitung..." jika belum bisa dihitung
        """
        current_speed = self.get_current_speed()
        if current_speed == 0:
            return "Menghitung..."

        remaining_tweets = self.session_target - self.session_count
        if remaining_tweets <= 0:
            return "Selesai"

        eta_minutes = remaining_tweets / current_speed
        return self.format_time(eta_minutes * 60)

    def get_total_eta(self) -> str:
        """
        Get estimasi waktu remaining untuk seluruh proses scraping.

        Returns:
            str: ETA dalam format readable atau "Menghitung..."
        """
        avg_speed = self.get_average_speed()
        if avg_speed == 0:
            return "Menghitung..."

        remaining_tweets = self.total_target - self.current_count
        if remaining_tweets <= 0:
            return "Selesai"

        eta_minutes = remaining_tweets / avg_speed
        return self.format_time(eta_minutes * 60)

    def finish_session(self):
        """
        Mark sesi saat ini sebagai selesai dan record statistiknya.

        Menyimpan durasi sesi dan kecepatan ke history untuk
        perhitungan statistik.
        """
        if self.session_start_time:
            session_duration = time.time() - self.session_start_time
            self.session_times.append(session_duration)

            if session_duration > 0:
                session_speed = self.session_count / (session_duration / 60)
                self.tweets_per_minute_history.append(session_speed)

    def get_progress_percentage(self) -> float:
        """
        Get overall progress percentage.

        Returns:
            float: Progress 0-100%
        """
        if self.total_target == 0:
            return 0.0
        return (self.current_count / self.total_target) * 100

    def get_session_percentage(self) -> float:
        """
        Get progress percentage untuk sesi saat ini.

        Returns:
            float: Progress 0-100%
        """
        if self.session_target == 0:
            return 0.0
        return (self.session_count / self.session_target) * 100

    def format_time(self, seconds: float) -> str:
        """
        Format seconds menjadi readable time string.

        Args:
            seconds (float): Waktu dalam detik

        Returns:
            str: Format:
                - < 60s: "30d"
                - < 3600s: "5m 30d"
                - >= 3600s: "2j 15m"
        """
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
        """
        Get comprehensive statistics tentang progress scraping.

        Returns:
            Dict[str, Any]: Dictionary berisi:
                - current_speed: Kecepatan saat ini
                - average_speed: Rata-rata kecepatan
                - session_progress: Progress sesi (%)
                - total_progress: Progress total (%)
                - session_eta: ETA sesi
                - total_eta: ETA total
                - session_number: Nomor sesi (e.g., "3/10")
                - tweets_collected: Tweet terkumpul (e.g., "300/1000")
                - avg_session_time: Rata-rata waktu per sesi (optional)
                - best_speed: Kecepatan terbaik (optional)

        Example:
            >>> stats = tracker.get_statistics()
            >>> print(stats['current_speed'])  # "45.2 tweet/menit"
            >>> print(stats['total_eta'])  # "15m 30d"
        """
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
