"""
Sentiment Analysis untuk tweet menggunakan Lexicon based approach.
"""

import os
import re
from typing import Dict, List, Any
import pandas as pd


class SentimentAnalyzer:
    """
    Analisis sentimen tweet (positif/negatif/netral) menggunakan lexicon custom.

    Menggunakan modified-lexicon_v2.txt untuk analisis sentimen dengan
    menjumlahkan skor kata-kata yang ditemukan dalam tweet.

    Attributes:
        lexicon (Dict[str, int]): Dictionary kata dan skor sentimennya
    """

    def __init__(self, lexicon_path: str = None):
        """
        Inisialisasi SentimentAnalyzer.

        Args:
            lexicon_path (str): Path ke file lexicon. Jika None, akan mencari
                          modified-lexicon_v2.txt di root project secara otomatis.
        """
        self.lexicon = {}
        self._load_lexicon(lexicon_path)

    def _load_lexicon(self, lexicon_path: str = None):
        """
        Load lexicon dari file text.
        Format file: kata,skor (per baris)

        Args:
            lexicon_path (str): Path ke file lexicon
        """
        # Tentukan path default jika tidak diberikan
        if lexicon_path is None:
            # Asumsi file berada di root project (2 level di atas file ini)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            lexicon_path = os.path.join(project_root, 'modified-lexicon_v2.txt')

        if not os.path.exists(lexicon_path):
            print(f"Warning: Lexicon file not found at {lexicon_path}")
            return

        try:
            with open(lexicon_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(',')
                    if len(parts) >= 2:
                        word = parts[0].strip().lower()
                        try:
                            score = int(parts[1].strip())
                            self.lexicon[word] = score
                        except ValueError:
                            continue

            print(f"Loaded {len(self.lexicon)} words from lexicon")

        except Exception as e:
            print(f"Error loading lexicon: {str(e)}")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analisis sentimen dari satu text menggunakan lexicon scoring.

        Args:
            text (str): Text tweet yang akan dianalisis

        Returns:
            Dict[str, Any]: Dictionary berisi:
                - polarity: Total skor sentimen
                - subjectivity: 0.0 (Not implemented in lexicon approach)
                - label: Label sentimen ('Positif', 'Negatif', 'Netral')
        """
        if not text or not isinstance(text, str):
            return {
                'polarity': 0,
                'subjectivity': 0.0,
                'label': 'Netral'
            }

        try:
            # Tokenisasi sederhana: lowercase dan ambil kata-kata saja
            words = re.findall(r'\w+', text.lower())

            score = 0
            matched_words = []

            for word in words:
                if word in self.lexicon:
                    word_score = self.lexicon[word]
                    score += word_score
                    matched_words.append(f"{word}({word_score})")

            # Klasifikasi berdasarkan total score
            if score > 0:
                label = 'Positif'
            elif score < 0:
                label = 'Negatif'
            else:
                label = 'Netral'

            return {
                'polarity': score,
                'subjectivity': 0.0, # Lexicon doesn't provide subjectivity
                'label': label,
                # Optional: debug info
                # 'matched_words': matched_words
            }
        except Exception as e:
            print(f"Error in analyze_text: {e}")
            return {
                'polarity': 0,
                'subjectivity': 0.0,
                'label': 'Error',
                'error': str(e)
            }

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'tweet_text') -> pd.DataFrame:
        """
        Analisis sentimen untuk seluruh DataFrame.

        Args:
            df (pd.DataFrame): DataFrame berisi tweet
            text_column (str): Nama kolom yang berisi text tweet

        Returns:
            pd.DataFrame: DataFrame dengan kolom tambahan:
                - sentiment_polarity
                - sentiment_subjectivity
                - sentiment_label
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")

        # Analisis setiap tweet
        sentiments = df[text_column].apply(self.analyze_text)

        # Extract ke kolom terpisah
        df['sentiment_polarity'] = sentiments.apply(lambda x: x['polarity'])
        df['sentiment_subjectivity'] = sentiments.apply(lambda x: x['subjectivity'])
        df['sentiment_label'] = sentiments.apply(lambda x: x['label'])

        return df

    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Dapatkan summary statistik sentimen.

        Args:
            df (pd.DataFrame): DataFrame yang sudah dianalisis

        Returns:
            Dict[str, Any]: Summary berisi:
                - total_tweets: Total tweet
                - positif_count: Jumlah tweet positif
                - negatif_count: Jumlah tweet negatif
                - netral_count: Jumlah tweet netral
                - positif_percentage: Persentase positif
                - negatif_percentage: Persentase negatif
                - netral_percentage: Persentase netral
                - avg_polarity: Rata-rata score
        """
        if 'sentiment_label' not in df.columns:
            raise ValueError("DataFrame belum dianalisis. Jalankan analyze_dataframe() terlebih dahulu")

        total = len(df)
        positif = len(df[df['sentiment_label'] == 'Positif'])
        negatif = len(df[df['sentiment_label'] == 'Negatif'])
        netral = len(df[df['sentiment_label'] == 'Netral'])

        return {
            'total_tweets': total,
            'positif_count': positif,
            'negatif_count': negatif,
            'netral_count': netral,
            'positif_percentage': round((positif / total * 100) if total > 0 else 0, 2),
            'negatif_percentage': round((negatif / total * 100) if total > 0 else 0, 2),
            'netral_percentage': round((netral / total * 100) if total > 0 else 0, 2),
            'avg_polarity': round(df['sentiment_polarity'].mean(), 2) if total > 0 else 0
        }
