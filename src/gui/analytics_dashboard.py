"""
Dashboard Visualisasi untuk analisis tweet.
"""

from typing import Dict, List, Any
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class AnalyticsDashboard(QWidget):
    """
    Dashboard visualisasi untuk analisis tweet.

    Menampilkan:
    - Sentiment distribution (pie chart)
    - Top hashtags (bar chart)
    - Top keywords (bar chart)
    - Tweet volume over time (line chart)
    """

    def __init__(self):
        """Inisialisasi Analytics Dashboard."""
        super().__init__()
        self.df = None
        self.sentiment_data = None
        self.trend_data = None
        self.init_ui()

    def init_ui(self):
        """Setup UI dashboard."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("📊 Analytics Dashboard")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Scroll area untuk charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.charts_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        # Info label
        self.info_label = QLabel("Belum ada data. Silakan load data dari file atau scraping terlebih dahulu.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("padding: 20px; font-size: 14px; color: #666;")
        self.charts_layout.addWidget(self.info_label)

        self.setLayout(layout)

    def load_data(self, df: pd.DataFrame, sentiment_data: Dict = None, trend_data: Dict = None):
        """
        Load data untuk visualisasi.

        Args:
            df (pd.DataFrame): DataFrame tweet
            sentiment_data (Dict): Data sentiment analysis
            trend_data (Dict): Data trend detection
        """
        self.df = df
        self.sentiment_data = sentiment_data
        self.trend_data = trend_data
        self.update_dashboard()

    def update_dashboard(self):
        """Update semua visualisasi di dashboard."""
        # Clear existing widgets
        while self.charts_layout.count():
            child = self.charts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self.df is None or len(self.df) == 0:
            self.info_label = QLabel("Tidak ada data untuk ditampilkan.")
            self.info_label.setAlignment(Qt.AlignCenter)
            self.charts_layout.addWidget(self.info_label)
            return

        # Summary statistics
        self.add_summary_stats()

        # Charts
        if MATPLOTLIB_AVAILABLE:
            if self.sentiment_data:
                self.add_sentiment_chart()

            if self.trend_data:
                self.add_hashtags_chart()
                self.add_keywords_chart()
        else:
            no_matplotlib = QLabel("⚠️ Matplotlib tidak terinstall. Install dengan: pip install matplotlib")
            no_matplotlib.setStyleSheet("padding: 20px; background-color: #fff3cd; border-radius: 5px;")
            self.charts_layout.addWidget(no_matplotlib)

    def add_summary_stats(self):
        """Tambahkan summary statistics cards."""
        stats_group = QGroupBox("📈 Summary Statistics")
        stats_layout = QGridLayout()

        # Total tweets
        total_label = self.create_stat_card("Total Tweets", str(len(self.df)), "#4CAF50")
        stats_layout.addWidget(total_label, 0, 0)

        # Sentiment stats
        if self.sentiment_data:
            positif = self.create_stat_card(
                "Positif",
                f"{self.sentiment_data.get('positif_count', 0)} ({self.sentiment_data.get('positif_percentage', 0)}%)",
                "#2196F3"
            )
            negatif = self.create_stat_card(
                "Negatif",
                f"{self.sentiment_data.get('negatif_count', 0)} ({self.sentiment_data.get('negatif_percentage', 0)}%)",
                "#f44336"
            )
            netral = self.create_stat_card(
                "Netral",
                f"{self.sentiment_data.get('netral_count', 0)} ({self.sentiment_data.get('netral_percentage', 0)}%)",
                "#FF9800"
            )

            stats_layout.addWidget(positif, 0, 1)
            stats_layout.addWidget(negatif, 0, 2)
            stats_layout.addWidget(netral, 0, 3)

        stats_group.setLayout(stats_layout)
        self.charts_layout.addWidget(stats_group)

    def create_stat_card(self, title: str, value: str, color: str) -> QWidget:
        """Create a stat card widget."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """)

        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)

        return card

    def add_sentiment_chart(self):
        """Tambahkan pie chart sentiment distribution."""
        if not MATPLOTLIB_AVAILABLE:
            return

        chart_group = QGroupBox("🎭 Sentiment Distribution")
        layout = QVBoxLayout()

        # Figure size yang cukup
        fig = Figure(figsize=(8, 4), dpi=80)
        canvas = FigureCanvasQTAgg(fig)

        # Set minimum height agar tidak gepeng/error saat render
        canvas.setMinimumHeight(400)

        ax = fig.add_subplot(111)

        labels = ['Positif', 'Negatif', 'Netral']
        sizes = [
            self.sentiment_data.get('positif_count', 0),
            self.sentiment_data.get('negatif_count', 0),
            self.sentiment_data.get('netral_count', 0)
        ]
        colors = ['#4CAF50', '#f44336', '#FF9800']

        # Cek apakah ada data
        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        else:
            ax.text(0.5, 0.5, "Tidak ada data sentimen", ha='center', va='center')

        ax.set_title('Sentiment Distribution', fontsize=11, pad=10)

        fig.tight_layout()

        layout.addWidget(canvas)
        chart_group.setLayout(layout)
        self.charts_layout.addWidget(chart_group)

    def add_hashtags_chart(self):
        """Tambahkan bar chart top hashtags."""
        if not MATPLOTLIB_AVAILABLE or not self.trend_data:
            return

        top_hashtags = self.trend_data.get('top_hashtags', [])
        if not top_hashtags:
            return

        chart_group = QGroupBox("🏷️ Top Hashtags")
        layout = QVBoxLayout()

        # Hitung tinggi dinamis berdasarkan jumlah item
        # Base height 1.5 inch + 0.4 inch per item
        num_items = len(top_hashtags[:15])  # Tampilkan sampai 15 hashtag
        fig_height = 1.5 + (num_items * 0.4)

        # Buat figure dengan tinggi dinamis
        fig = Figure(figsize=(8, fig_height), dpi=80)
        canvas = FigureCanvasQTAgg(fig)

        # Set minimum height agar scroll area bekerja
        canvas.setMinimumHeight(int(fig_height * 80))

        ax = fig.add_subplot(111)

        # Ambil data
        hashtags = [f"#{tag}" for tag, _ in top_hashtags[:15]]
        counts = [count for _, count in top_hashtags[:15]]

        # Plot horizontal bar
        ax.barh(hashtags, counts, color='#2196F3', height=0.6)
        ax.set_xlabel('Count', fontsize=10)
        ax.set_title(f'Top {num_items} Hashtags', fontsize=11, pad=10)
        ax.tick_params(axis='both', labelsize=9)
        ax.invert_yaxis()  # Terbanyak di atas
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Adjust layout agar label tidak terpotong
        fig.tight_layout()

        layout.addWidget(canvas)
        chart_group.setLayout(layout)
        self.charts_layout.addWidget(chart_group)

    def add_keywords_chart(self):
        """Tambahkan bar chart top keywords."""
        if not MATPLOTLIB_AVAILABLE or not self.trend_data:
            return

        top_keywords = self.trend_data.get('top_keywords', [])
        if not top_keywords:
            return

        chart_group = QGroupBox("🔑 Top Keywords")
        layout = QVBoxLayout()

        # Hitung tinggi dinamis berdasarkan jumlah item
        # Base height 1.5 inch + 0.4 inch per item
        num_items = len(top_keywords[:20])  # Tampilkan sampai 20 keyword
        fig_height = 1.5 + (num_items * 0.4)

        # Buat figure dengan tinggi dinamis
        fig = Figure(figsize=(8, fig_height), dpi=80)
        canvas = FigureCanvasQTAgg(fig)

        # Set minimum height agar scroll area bekerja
        canvas.setMinimumHeight(int(fig_height * 80))

        ax = fig.add_subplot(111)

        # Ambil data
        keywords = [kw for kw, _ in top_keywords[:20]]
        counts = [count for _, count in top_keywords[:20]]

        # Plot horizontal bar
        ax.barh(keywords, counts, color='#4CAF50', height=0.6)
        ax.set_xlabel('Count', fontsize=10)
        ax.set_title(f'Top {num_items} Keywords', fontsize=11, pad=10)
        ax.tick_params(axis='both', labelsize=9)
        ax.invert_yaxis()  # Terbanyak di atas
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Adjust layout agar label tidak terpotong
        fig.tight_layout()

        layout.addWidget(canvas)
        chart_group.setLayout(layout)
        self.charts_layout.addWidget(chart_group)
