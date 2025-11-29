"""
Sentiment Analysis untuk tweet menggunakan TextBlob.
"""

from typing import Dict, List, Any
from textblob import TextBlob
import pandas as pd


class SentimentAnalyzer:
    """
    Analisis sentimen tweet (positif/negatif/netral).

    Menggunakan TextBlob untuk analisis sentimen dengan support
    untuk Bahasa Indonesia dan Inggris.

    Attributes:
        polarity_threshold (float): Threshold untuk klasifikasi sentimen

    Example:
        >>> analyzer = SentimentAnalyzer()
        >>> sentiment = analyzer.analyze_text("I love this product!")
        >>> print(sentiment['label'])  # 'Positif'
    """

    def __init__(self, polarity_threshold: float = 0.1):
        """
        Inisialisasi SentimentAnalyzer.

        Args:
            polarity_threshold (float): Threshold untuk klasifikasi.
                - > threshold: Positif
                - < -threshold: Negatif
                - else: Netral
        """
        self.polarity_threshold = polarity_threshold

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analisis sentimen dari satu text.

        Args:
            text (str): Text tweet yang akan dianalisis

        Returns:
            Dict[str, Any]: Dictionary berisi:
                - polarity: Nilai polarity (-1 to 1)
                - subjectivity: Nilai subjectivity (0 to 1)
                - label: Label sentimen ('Positif', 'Negatif', 'Netral')

        Example:
            >>> result = analyzer.analyze_text("Great product!")
            >>> print(result['label'])  # 'Positif'
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Klasifikasi berdasarkan polarity
            if polarity > self.polarity_threshold:
                label = 'Positif'
            elif polarity < -self.polarity_threshold:
                label = 'Negatif'
            else:
                label = 'Netral'

            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'label': label
            }
        except Exception as e:
            return {
                'polarity': 0.0,
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
                - avg_polarity: Rata-rata polarity
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
            'avg_polarity': round(df['sentiment_polarity'].mean(), 3) if total > 0 else 0
        }
