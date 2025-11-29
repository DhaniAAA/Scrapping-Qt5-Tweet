"""
Trend Detection untuk mengidentifikasi trending topics dan hashtags.
"""

from typing import Dict, List, Any, Tuple
from collections import Counter
import pandas as pd
import re
from datetime import datetime, timedelta


class TrendDetector:
    """
    Deteksi trending topics, hashtags, dan mentions dari tweet.

    Class ini menganalisis tweet untuk menemukan:
    - Top hashtags
    - Top mentions
    - Top keywords
    - Spike detection (lonjakan volume tweet)

    Example:
        >>> detector = TrendDetector()
        >>> trends = detector.detect_trends(df)
        >>> print(trends['top_hashtags'])
    """

    def __init__(self):
        """Inisialisasi TrendDetector."""
        self._stopwords_cache = None

    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags dari text.

        Args:
            text (str): Text tweet

        Returns:
            List[str]: List hashtags (tanpa #)
        """
        hashtags = re.findall(r'#(\w+)', text)
        return [tag.lower() for tag in hashtags]

    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract mentions dari text.

        Args:
            text (str): Text tweet

        Returns:
            List[str]: List mentions (tanpa @)
        """
        mentions = re.findall(r'@(\w+)', text)
        return [mention.lower() for mention in mentions]

    def extract_keywords(self, text: str, min_length: int = 4) -> List[str]:
        """
        Extract keywords dari text (kata-kata penting).

        Args:
            text (str): Text tweet
            min_length (int): Panjang minimum kata

        Returns:
            List[str]: List keywords
        """
        # Remove URLs, hashtags, mentions
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'@\w+', '', text)

        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())

        # Load stopwords dari modified-lexicon_text.txt
        stopwords = self._load_stopwords()

        keywords = [word for word in words if len(word) >= min_length and word not in stopwords]
        return keywords

    def _load_stopwords(self) -> set:
        """
        Load stopwords dari file modified-lexicon_text.txt.

        Returns:
            set: Set of stopwords
        """
        # Use cache if available
        if self._stopwords_cache is not None:
            return self._stopwords_cache

        stopwords = set()
        try:
            import os
            # Try to find the file in current directory or parent directory
            possible_paths = [
                'modified-lexicon_text.txt',
                '../modified-lexicon_text.txt',
                '../../modified-lexicon_text.txt',
                os.path.join(os.path.dirname(__file__), '../../modified-lexicon_text.txt')
            ]

            lexicon_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    lexicon_path = path
                    break

            if lexicon_path:
                with open(lexicon_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and ',' in line:
                            word = line.split(',')[0].strip()
                            if word:
                                stopwords.add(word.lower())
            else:
                # Fallback ke basic stopwords jika file tidak ditemukan
                stopwords = {
                    'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan', 'ini', 'itu',
                    'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                    'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
                    'might', 'can', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
                }
        except Exception as e:
            # Fallback ke basic stopwords jika ada error
            stopwords = {
                'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan', 'ini', 'itu',
                'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
                'might', 'can', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
            }

        # Cache the result
        self._stopwords_cache = stopwords
        return stopwords

    def get_top_hashtags(self, df: pd.DataFrame, top_n: int = 10, text_column: str = 'tweet_text') -> List[Tuple[str, int]]:
        """
        Dapatkan top hashtags dari DataFrame.

        Args:
            df (pd.DataFrame): DataFrame berisi tweet
            top_n (int): Jumlah top hashtags yang ingin ditampilkan
            text_column (str): Nama kolom text

        Returns:
            List[Tuple[str, int]]: List tuple (hashtag, count)
        """
        all_hashtags = []
        for text in df[text_column]:
            all_hashtags.extend(self.extract_hashtags(str(text)))

        counter = Counter(all_hashtags)
        return counter.most_common(top_n)

    def get_top_mentions(self, df: pd.DataFrame, top_n: int = 10, text_column: str = 'tweet_text') -> List[Tuple[str, int]]:
        """
        Dapatkan top mentions dari DataFrame.

        Args:
            df (pd.DataFrame): DataFrame berisi tweet
            top_n (int): Jumlah top mentions yang ingin ditampilkan
            text_column (str): Nama kolom text

        Returns:
            List[Tuple[str, int]]: List tuple (mention, count)
        """
        all_mentions = []
        for text in df[text_column]:
            all_mentions.extend(self.extract_mentions(str(text)))

        counter = Counter(all_mentions)
        return counter.most_common(top_n)

    def get_top_keywords(self, df: pd.DataFrame, top_n: int = 20, text_column: str = 'tweet_text') -> List[Tuple[str, int]]:
        """
        Dapatkan top keywords dari DataFrame.

        Args:
            df (pd.DataFrame): DataFrame berisi tweet
            top_n (int): Jumlah top keywords yang ingin ditampilkan
            text_column (str): Nama kolom text

        Returns:
            List[Tuple[str, int]]: List tuple (keyword, count)
        """
        all_keywords = []
        for text in df[text_column]:
            all_keywords.extend(self.extract_keywords(str(text)))

        counter = Counter(all_keywords)
        return counter.most_common(top_n)

    def detect_spike(self, df: pd.DataFrame, timestamp_column: str = 'timestamp', window_hours: int = 1) -> Dict[str, Any]:
        """
        Deteksi spike (lonjakan) volume tweet.

        Args:
            df (pd.DataFrame): DataFrame berisi tweet
            timestamp_column (str): Nama kolom timestamp
            window_hours (int): Window waktu untuk deteksi (jam)

        Returns:
            Dict[str, Any]: Informasi spike:
                - has_spike: Boolean apakah ada spike
                - peak_time: Waktu peak
                - peak_count: Jumlah tweet di peak
                - avg_count: Rata-rata tweet per window
        """
        if timestamp_column not in df.columns:
            return {'has_spike': False, 'error': 'Timestamp column not found'}

        # Convert to datetime
        df['_temp_timestamp'] = pd.to_datetime(df[timestamp_column])

        # Group by time window
        df['_temp_window'] = df['_temp_timestamp'].dt.floor(f'{window_hours}H')
        window_counts = df.groupby('_temp_window').size()

        if len(window_counts) == 0:
            return {'has_spike': False}

        avg_count = window_counts.mean()
        std_count = window_counts.std()
        peak_window = window_counts.idxmax()
        peak_count = window_counts.max()

        # Spike jika > mean + 2*std
        threshold = avg_count + (2 * std_count) if std_count > 0 else avg_count * 1.5
        has_spike = peak_count > threshold

        return {
            'has_spike': has_spike,
            'peak_time': str(peak_window),
            'peak_count': int(peak_count),
            'avg_count': round(avg_count, 2),
            'threshold': round(threshold, 2)
        }

    def detect_trends(self, df: pd.DataFrame, text_column: str = 'tweet_text') -> Dict[str, Any]:
        """
        Deteksi semua trends dalam satu fungsi.

        Args:
            df (pd.DataFrame): DataFrame berisi tweet
            text_column (str): Nama kolom text

        Returns:
            Dict[str, Any]: Dictionary berisi semua trend data:
                - top_hashtags: Top 10 hashtags
                - top_mentions: Top 10 mentions
                - top_keywords: Top 20 keywords
                - spike_info: Informasi spike detection
        """
        return {
            'top_hashtags': self.get_top_hashtags(df, top_n=10, text_column=text_column),
            'top_mentions': self.get_top_mentions(df, top_n=10, text_column=text_column),
            'top_keywords': self.get_top_keywords(df, top_n=20, text_column=text_column),
            'spike_info': self.detect_spike(df) if 'timestamp' in df.columns else {'has_spike': False}
        }
