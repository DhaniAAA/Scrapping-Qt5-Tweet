import os
from typing import Dict, Any
from threading import Thread, Event
from datetime import timedelta

import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QComboBox,
    QPushButton, QTextEdit, QSpinBox, QGridLayout, QGroupBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QProgressBar,
    QHBoxLayout, QCheckBox, QFrame, QSplitter, QStackedWidget,
    QFileDialog, QMessageBox, QScrollArea, QSystemTrayIcon, QStyle
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
import winsound

from ..config.constants import WINDOW_WIDTH, WINDOW_HEIGHT, MIN_LEFT_PANEL_WIDTH, MAX_LEFT_PANEL_WIDTH
from ..core import ThemeManager
from ..scraper import main_scraping_function
from ..analysis import SentimentAnalyzer, TrendDetector
from .signals import LoggerSignals
from .analytics_dashboard import AnalyticsDashboard


class TweetScraperGUIV2(QWidget):
    """Main GUI window v2.3.3 - Performance + Analytics Edition"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tweet Scraper X.com v2.3.3 - Performance + Analytics Edition")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.scraping_thread = None
        self.stop_event = Event()
        self.current_dataframe = None  # Store scraped data

        # Initialize theme manager
        self.theme_manager = ThemeManager()

        # Initialize analysis modules
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trend_detector = TrendDetector()
        self.signals = LoggerSignals()
        self.signals.log_signal.connect(self.append_log)
        self.signals.finished_signal.connect(self.on_scraping_finished)
        self.signals.progress_signal.connect(self.update_progress)
        self.signals.data_row_signal.connect(self.add_data_row)
        self.signals.stats_signal.connect(self.update_stats)
        self.signals.notification_signal.connect(self.show_notification)

        # Setup System Tray
        self.setup_tray_icon()

        # Setup UI
        self.init_ui()

        # Apply initial theme
        self.setStyleSheet(self.theme_manager.get_current_theme_style())

    def init_ui(self):
        """Initialize UI dengan navbar dan stacked pages."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Create navbar
        self.create_navbar()
        main_layout.addWidget(self.navbar)

        # Create stacked widget untuk pages
        self.stacked_widget = QStackedWidget()

        # Create pages
        self.scraper_page = self.create_scraper_page()
        self.analytics_page = self.create_analytics_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.scraper_page)
        self.stacked_widget.addWidget(self.analytics_page)

        main_layout.addWidget(self.stacked_widget)

    def setup_tray_icon(self):
        """Setup system tray icon untuk notifikasi."""
        self.tray_icon = QSystemTrayIcon(self)

        # Gunakan standard icon dari style bawaan jika tidak ada icon custom
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setVisible(True)
        self.tray_icon.setToolTip("Tweet Scraper X.com")

    def show_notification(self, title: str, message: str):
        """Tampilkan notifikasi desktop dan mainkan suara."""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                5000  # Durasi 5 detik
            )

            # Mainkan suara "SystemAsterisk" (Ting!)
            try:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
            except Exception:
                pass  # Ignore sound error

    def create_navbar(self):
        """Create navigation bar dengan menu buttons."""
        self.navbar = QWidget()
        self.navbar.setFixedHeight(60)
        self.navbar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-bottom: 3px solid #3498db;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
                border-bottom: 3px solid #2ecc71;
            }
        """)

        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(0, 0, 0, 0)
        navbar_layout.setSpacing(0)
        self.navbar.setLayout(navbar_layout)

        # Logo/Title
        title = QLabel("  Tweet Scraper v2.3.3")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding-left: 20px;")
        navbar_layout.addWidget(title)

        navbar_layout.addStretch()

        # Menu buttons
        self.scraper_btn = QPushButton("🔍 Scraper")
        self.scraper_btn.setCheckable(True)
        self.scraper_btn.setChecked(True)
        self.scraper_btn.clicked.connect(lambda: self.switch_page(0))

        self.analytics_btn = QPushButton("📊 Analytics")
        self.analytics_btn.setCheckable(True)
        self.analytics_btn.clicked.connect(lambda: self.switch_page(1))

        # Theme button
        self.theme_button = QPushButton(self.theme_manager.get_theme_button_text())
        self.theme_button.clicked.connect(self.toggle_theme)

        navbar_layout.addWidget(self.scraper_btn)
        navbar_layout.addWidget(self.analytics_btn)
        navbar_layout.addWidget(self.theme_button)

    def switch_page(self, index: int):
        """Switch between pages."""
        self.stacked_widget.setCurrentIndex(index)

        # Update button states
        self.scraper_btn.setChecked(index == 0)
        self.analytics_btn.setChecked(index == 1)

        # If switching to analytics, check if we have data
        if index == 1 and self.current_dataframe is None:
            QMessageBox.information(
                self,
                "Info",
                "Belum ada data untuk dianalisis.\n\nSilakan:\n1. Scraping tweet terlebih dahulu, atau\n2. Load data dari file CSV/Excel"
            )

    def create_scraper_page(self):
        """Create scraper page (original interface)."""
        page = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        page.setLayout(layout)

        # Left panel (controls)
        # Menggunakan ScrollArea untuk Left Panel agar aman jika layar kecil
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        left_panel = self.create_scraper_left_panel()
        scroll_area.setWidget(left_panel)

        # Right panel (output)
        right_panel = self.create_scraper_right_panel()

        # Layout allocation (Left panel gets more space now for the grid)
        layout.addWidget(scroll_area, 2)
        layout.addWidget(right_panel, 1)

        return page

    def create_analytics_page(self):
        """Create analytics page."""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        page.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel("📊 Analytics Dashboard")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Load data button
        load_btn = QPushButton("📁 Load Data dari File")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_btn.clicked.connect(self.load_data_from_file)
        header_layout.addWidget(load_btn)

        # Analyze button
        analyze_btn = QPushButton("🔬 Analyze Data")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_data)
        header_layout.addWidget(analyze_btn)

        layout.addLayout(header_layout)

        # Dashboard
        self.analytics_dashboard = AnalyticsDashboard()
        layout.addWidget(self.analytics_dashboard)

        return page

    def create_scraper_left_panel(self):
        """Create left panel untuk scraper page."""
        panel = QWidget()
        panel.setMinimumWidth(MIN_LEFT_PANEL_WIDTH)
        # Menghapus strict maximum width agar layout bisa bernafas
        # panel.setMaximumWidth(MAX_LEFT_PANEL_WIDTH)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(15) # Menambah spacing antar elemen utama
        left_layout.setContentsMargins(15, 15, 15, 15)
        panel.setLayout(left_layout)

        # Title
        title_label = QLabel("Scraper Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(title_label)

        # Input sections - MENGGUNAKAN GRID LAYOUT 2x2
        self.create_input_grid_layout(left_layout)

        # Multi-Threading section
        self.create_multithreading_section(left_layout)

        # Controls & Progress
        self.create_control_section(left_layout)
        self.create_progress_section(left_layout)

        left_layout.addStretch()

        return panel

    def create_scraper_right_panel(self):
        """Create right panel untuk scraper page."""
        panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 15, 15, 15)
        right_layout.setSpacing(10)
        panel.setLayout(right_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(400)

        # Log tab
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.tabs.addTab(self.log_output, "📝 Log")

        # Data preview tab
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.tabs.addTab(self.data_table, "📋 Data Preview")

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 8px; font-size: 12px; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.db_status_label = QLabel("Database: Ready")
        self.db_status_label.setStyleSheet("padding: 8px; font-size: 12px; color: #666;")
        status_layout.addWidget(self.db_status_label)

        right_layout.addWidget(self.tabs, 1)
        right_layout.addLayout(status_layout)

        return panel

    def create_input_grid_layout(self, parent_layout):
        """Create GRID arrangement of input sections (2x2) untuk mencegah tumpang tindih."""
        # Mengganti QHBoxLayout (horizontal lurus) dengan QGridLayout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)  # Spacing yang cukup antar groupbox

        # Create each section as a widget
        search_widget = self.create_search_section_widget()
        date_widget = self.create_date_section_widget()
        options_widget = self.create_options_section_widget()
        auth_widget = self.create_auth_section_widget()

        # Add sections to GRID layout (row, column)
        # Baris 1
        grid_layout.addWidget(search_widget, 0, 0)
        grid_layout.addWidget(date_widget, 0, 1)

        # Baris 2
        grid_layout.addWidget(options_widget, 1, 0)
        grid_layout.addWidget(auth_widget, 1, 1)

        # Set column stretch agar seimbang
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        parent_layout.addLayout(grid_layout)

    def create_search_section_widget(self):
        """Create search parameters section as a widget"""
        search_group = QGroupBox("🔍 Parameter Pencarian")
        search_layout = QVBoxLayout()
        search_layout.setSpacing(8)
        search_layout.setContentsMargins(10, 20, 10, 10) # Margin atas lebih besar untuk judul
        search_group.setLayout(search_layout)

        # Keyword
        search_layout.addWidget(QLabel("Kata Kunci:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Topik/hashtag...")
        self.keyword_input.setMinimumHeight(30)
        search_layout.addWidget(self.keyword_input)

        # Language
        lang_layout = QHBoxLayout() # Sub-layout untuk hemat tempat vertikal
        lang_layout.addWidget(QLabel("Bahasa:"))
        self.lang_input = QLineEdit("id")
        self.lang_input.setMinimumHeight(30)
        self.lang_input.setFixedWidth(60)
        lang_layout.addWidget(self.lang_input)

        # Search Type
        lang_layout.addWidget(QLabel("Jenis:"))
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["Top", "Terbaru"])
        self.search_type_combo.setMinimumHeight(30)
        lang_layout.addWidget(self.search_type_combo)

        search_layout.addLayout(lang_layout)

        return search_group

    def create_date_section_widget(self):
        """Create date range section as a widget"""
        date_group = QGroupBox("📅 Rentang Waktu")
        date_layout = QVBoxLayout()
        date_layout.setSpacing(8)
        date_layout.setContentsMargins(10, 20, 10, 10)
        date_group.setLayout(date_layout)

        # Start date
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Mulai:"))
        self.start_date_input = QDateEdit(calendarPopup=True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setMinimumHeight(30)
        self.start_date_input.setCalendarPopup(True)
        row1.addWidget(self.start_date_input)
        date_layout.addLayout(row1)

        # End date
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Selesai:"))
        self.end_date_input = QDateEdit(calendarPopup=True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setMinimumHeight(30)
        self.end_date_input.setCalendarPopup(True)
        row2.addWidget(self.end_date_input)
        date_layout.addLayout(row2)

        # Interval
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Interval (hr):"))
        self.interval_input = QSpinBox()
        self.interval_input.setMinimum(1)
        self.interval_input.setValue(1)
        self.interval_input.setMinimumHeight(30)
        self.interval_input.setMaximum(365)
        row3.addWidget(self.interval_input)
        date_layout.addLayout(row3)

        return date_group

    def create_options_section_widget(self):
        """Create scraping options section as a widget"""
        options_group = QGroupBox("⚙️ Opsi Scraping")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)
        options_layout.setContentsMargins(10, 20, 10, 10)
        options_group.setLayout(options_layout)

        # Tweet count
        options_layout.addWidget(QLabel("Tweet/Sesi:"))
        self.count_input = QSpinBox()
        self.count_input.setRange(10, 1000)
        self.count_input.setValue(100)
        self.count_input.setMinimumHeight(30)
        self.count_input.setSuffix(" tweets")
        options_layout.addWidget(self.count_input)

        # Export format
        options_layout.addWidget(QLabel("Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "JSON", "Excel"])
        self.export_format_combo.setMinimumHeight(30)
        options_layout.addWidget(self.export_format_combo)

        return options_group

    def create_auth_section_widget(self):
        """Create authentication section as a widget"""
        auth_group = QGroupBox("🔐 Autentikasi")
        auth_layout = QVBoxLayout()
        auth_layout.setSpacing(8)
        auth_layout.setContentsMargins(10, 20, 10, 10)
        auth_group.setLayout(auth_layout)

        auth_layout.addWidget(QLabel("Auth Token (Cookie):"))
        self.cookie_input = QLineEdit()
        self.cookie_input.setEchoMode(QLineEdit.Password)
        self.cookie_input.setPlaceholderText("Paste token di sini...")
        self.cookie_input.setMinimumHeight(30)
        auth_layout.addWidget(self.cookie_input)

        # Info label
        info = QLabel("Diperlukan untuk akses penuh")
        info.setStyleSheet("color: gray; font-size: 10px; font-style: italic;")
        auth_layout.addWidget(info)

        return auth_group

    def create_multithreading_section(self, parent_layout):
        """Create multi-threading configuration section"""
        mt_group = QGroupBox("🚀 Multi-Threading")
        mt_layout = QVBoxLayout()
        mt_layout.setSpacing(8)
        mt_group.setLayout(mt_layout)

        # Enable checkbox
        self.mt_enable_checkbox = QCheckBox("Enable Parallel Scraping - Masih Belum Optimal")
        self.mt_enable_checkbox.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.mt_enable_checkbox.setChecked(False)
        self.mt_enable_checkbox.stateChanged.connect(self.on_mt_enable_changed)
        mt_layout.addWidget(self.mt_enable_checkbox)

        # Thread count layout
        thread_layout = QHBoxLayout()
        thread_label = QLabel("Threads:")
        thread_label.setMinimumWidth(60)

        self.mt_thread_spinbox = QSpinBox()
        self.mt_thread_spinbox.setRange(1, 5)
        self.mt_thread_spinbox.setValue(2)
        self.mt_thread_spinbox.setSuffix(" threads")
        self.mt_thread_spinbox.setMinimumHeight(30)
        self.mt_thread_spinbox.setEnabled(False)
        self.mt_thread_spinbox.valueChanged.connect(self.on_mt_thread_changed)

        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.mt_thread_spinbox)
        mt_layout.addLayout(thread_layout)

        # Performance estimate
        self.mt_perf_label = QLabel("⚡ Estimasi: Normal speed (1x)")
        self.mt_perf_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                padding: 8px;
                border-radius: 4px;
                color: #1976d2;
                font-size: 10px;
            }
        """)
        self.mt_perf_label.setWordWrap(True)
        mt_layout.addWidget(self.mt_perf_label)

        parent_layout.addWidget(mt_group)

    def on_mt_enable_changed(self, state):
        """Handle multi-threading enable checkbox change"""
        from PyQt5.QtCore import Qt
        enabled = state == Qt.Checked
        self.mt_thread_spinbox.setEnabled(enabled)
        self.update_mt_performance_estimate()

    def on_mt_thread_changed(self, value):
        """Handle thread count change"""
        self.update_mt_performance_estimate()

    def update_mt_performance_estimate(self):
        """Update performance estimate label"""
        if not self.mt_enable_checkbox.isChecked():
            self.mt_perf_label.setText("⚡ Estimasi: Normal speed (1x)")
            self.mt_perf_label.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    padding: 8px;
                    border-radius: 4px;
                    color: #1976d2;
                    font-size: 10px;
                }
            """)
            return

        threads = self.mt_thread_spinbox.value()
        speedup = min(threads * 0.8, 4.0)  # Realistic speedup

        self.mt_perf_label.setText(f"⚡ Estimasi: {speedup:.1f}x lebih cepat dengan {threads} threads")
        self.mt_perf_label.setStyleSheet("""
            QLabel {
                background-color: #c8e6c9;
                padding: 8px;
                border-radius: 4px;
                color: #2e7d32;
                font-size: 10px;
                font-weight: bold;
            }
        """)

    def get_mt_config(self):
        """Get multi-threading configuration"""
        return {
            'enabled': self.mt_enable_checkbox.isChecked(),
            'thread_count': self.mt_thread_spinbox.value() if self.mt_enable_checkbox.isChecked() else 1
        }

    def create_control_section(self, parent_layout):
        """Create control buttons section - horizontal layout"""
        control_group = QGroupBox("🎮 Kontrol")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        control_group.setLayout(control_layout)

        # Start and Stop buttons side by side
        self.start_button = QPushButton("▶️ Mulai Scraping")
        self.start_button.setObjectName("startBtn")
        self.start_button.setMinimumHeight(45) # Button sedikit lebih tinggi
        self.start_button.clicked.connect(self.start_scraping)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("⏹️ Stop Scraping")
        self.stop_button.setObjectName("stopBtn")
        self.stop_button.setMinimumHeight(45)
        self.stop_button.clicked.connect(self.stop_scraping)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        parent_layout.addWidget(control_group)

    def create_progress_section(self, parent_layout):
        """Create compact progress section dengan layout Grid"""
        progress_group = QGroupBox("📊 Progress")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(10)
        progress_group.setLayout(progress_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(30)
        progress_layout.addWidget(self.progress_bar)

        # Grid statistics layout (2x2) agar tidak tumpang tindih
        stats_layout = QGridLayout()
        stats_layout.setSpacing(10)

        self.stats_labels = {
            'current_speed': QLabel("⚡ Kecepatan: -"),
            'session_eta': QLabel("⏱️ ETA: -"),
            'tweets_collected': QLabel("📊 Tweet: 0/0"),
            'total_progress': QLabel("📈 Total: 0%")
        }

        # Style the labels
        for label in self.stats_labels.values():
            label.setStyleSheet("font-size: 11px; padding: 5px; border: 1px solid #ddd; border-radius: 4px; background-color: #f9f9f9;")

        # Arrange in Grid
        stats_layout.addWidget(self.stats_labels['current_speed'], 0, 0)
        stats_layout.addWidget(self.stats_labels['session_eta'], 0, 1)
        stats_layout.addWidget(self.stats_labels['tweets_collected'], 1, 0)
        stats_layout.addWidget(self.stats_labels['total_progress'], 1, 1)

        progress_layout.addLayout(stats_layout)
        parent_layout.addWidget(progress_group)

    def setup_table(self):
        """Setup data table columns"""
        self.data_table.setColumnCount(8)
        self.data_table.setHorizontalHeaderLabels([
            "Username", "Handle", "Timestamp", "Tweet Text",
            "URL", "Replies", "Retweets", "Likes"
        ])
        self.data_table.setColumnWidth(3, 300)

    def add_data_row(self, data: Dict[str, Any]):
        """Add a row to the data table"""
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
        """Update progress bar"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def update_stats(self, stats: Dict[str, Any]):
        """Update progress statistics display"""
        if 'current_speed' in stats:
            self.stats_labels['current_speed'].setText(f"⚡ Kecepatan: {stats['current_speed']}")
        if 'session_eta' in stats:
            self.stats_labels['session_eta'].setText(f"⏱️ ETA: {stats['session_eta']}")
        if 'tweets_collected' in stats:
            self.stats_labels['tweets_collected'].setText(f"📊 Tweet: {stats['tweets_collected']}")
        if 'total_progress' in stats:
            self.stats_labels['total_progress'].setText(f"📈 Total: {stats['total_progress']}")

    def append_log(self, text: str):
        """Append text to log output"""
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

    def stop_scraping(self):
        """Stop the scraping process"""
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.stop_event.set()
            self.stop_button.setEnabled(False)
            self.append_log("\n--- Mengirim sinyal berhenti... ---")

    def start_scraping(self):
        """Start the scraping process"""
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

        # Get Multi-Threading Config
        mt_config = self.get_mt_config()

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
            "stop_event": self.stop_event,
            "mt_config": mt_config  # Pass MT config
        }

        self.append_log("🚀 Memulai scraping...")
        self.append_log(f"📋 Target: {count} tweet per sesi")
        self.append_log(f"📅 Periode: {start_date} hingga {end_date}")
        self.append_log(f"🔍 Kata kunci: {keyword}")

        if mt_config['enabled']:
            self.append_log(f"⚡ Parallel Scraping: ENABLED ({mt_config['thread_count']} threads)")
        else:
            self.append_log("🐌 Parallel Scraping: DISABLED (Single-thread)")

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Scraping started...")

        self.scraping_thread = Thread(target=self.run_scraper_thread, args=(args,))
        self.scraping_thread.start()

    def run_scraper_thread(self, args: Dict[str, Any]):
        """Run scraper in separate thread"""
        try:
            # Check if multi-threading is enabled
            mt_config = args.get('mt_config', {'enabled': False})

            if mt_config['enabled']:
                # Use ParallelScraper
                from ..scraper.parallel_scraper import ParallelScraper

                scraper = ParallelScraper(
                    num_threads=mt_config['thread_count'],
                    signals=args['signals'],
                    stop_event=args['stop_event']
                )

                # Generate date ranges
                start_date = args['start_date']
                end_date = args['end_date']
                interval = args['interval']
                date_ranges = []

                current_date = start_date
                while current_date <= end_date:
                    chunk_end_date = current_date + timedelta(days=interval)
                    date_ranges.append((current_date, chunk_end_date))
                    current_date = chunk_end_date

                # Run parallel scraping
                all_tweets = scraper.scrape_parallel(
                    keyword=args['keyword'],
                    date_ranges=date_ranges,
                    target_per_session=args['target_per_session'],
                    lang=args['lang'],
                    search_type=args['search_type'],
                    auth_token=args['auth_token_cookie']
                )

                # Save results
                if all_tweets:
                    df = pd.DataFrame(all_tweets)

                    # Generate filename
                    safe_keyword = "".join(c for c in args['keyword'] if c.isalnum())
                    date_str = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
                    base_filename = f"tweets_{safe_keyword}_{args['search_type']}_{date_str}"

                    export_format = args['export_format']
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

                        self.signals.log_signal.emit(f"\n✅ Data disimpan ke: {filename} ({len(df)} tweet)")
                        self.signals.notification_signal.emit("Scraping Selesai", f"Berhasil menyimpan {len(df)} tweet ke {filename}")
                    except Exception as e:
                        self.signals.log_signal.emit(f"\n!!! Gagal menyimpan file: {e} !!!")
                else:
                    self.signals.log_signal.emit("\n⚠️ Tidak ada data yang terkumpul.")

            else:
                # Use original single-threaded scraping
                # Remove mt_config from args before passing to main_scraping_function
                if 'mt_config' in args:
                    del args['mt_config']

                main_scraping_function(**args)

        except Exception as e:
            self.signals.log_signal.emit(f"\n!!! Terjadi kesalahan fatal: {e} !!!")
            self.signals.notification_signal.emit("Scraping Error", f"Gagal: {str(e)[:100]}...")
            import traceback
            self.signals.log_signal.emit(traceback.format_exc())
        finally:
            self.signals.finished_signal.emit()

    def on_scraping_finished(self):
        """Handle scraping finished - save data for analytics."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.append_log("\n--- Proses Selesai ---")

        # Try to load scraped data
        self.load_latest_scraped_data()

        if self.progress_bar.value() < self.progress_bar.maximum():
            self.append_log("Proses mungkin tidak selesai sepenuhnya atau dihentikan.")
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.scraping_thread = None

    def load_latest_scraped_data(self):
        """Load latest scraped data file."""
        try:
            # Find latest CSV file
            files = [f for f in os.listdir('.') if f.startswith('tweets_') and f.endswith('.csv')]
            if files:
                latest_file = max(files, key=os.path.getctime)
                self.current_dataframe = pd.read_csv(latest_file)
                self.append_log(f"✅ Data loaded: {latest_file} ({len(self.current_dataframe)} tweets)")
        except Exception as e:
            self.append_log(f"⚠️ Gagal load data: {e}")

    def load_data_from_file(self):
        """Load data dari file CSV/Excel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Data File",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.current_dataframe = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.current_dataframe = pd.read_excel(file_path)
                else:
                    QMessageBox.warning(self, "Error", "Format file tidak didukung!")
                    return

                QMessageBox.information(
                    self,
                    "Success",
                    f"Data berhasil di-load!\n\nTotal tweets: {len(self.current_dataframe)}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal load file:\n{e}")

    def analyze_data(self):
        """Analyze data dan update dashboard."""
        if self.current_dataframe is None or len(self.current_dataframe) == 0:
            QMessageBox.warning(self, "Warning", "Tidak ada data untuk dianalisis!")
            return

        try:
            # Sentiment analysis
            self.current_dataframe = self.sentiment_analyzer.analyze_dataframe(self.current_dataframe)
            sentiment_summary = self.sentiment_analyzer.get_sentiment_summary(self.current_dataframe)

            # Trend detection
            trend_data = self.trend_detector.detect_trends(self.current_dataframe)

            # Update dashboard
            self.analytics_dashboard.load_data(
                self.current_dataframe,
                sentiment_summary,
                trend_data
            )

            QMessageBox.information(
                self,
                "Success",
                "Analisis selesai!\n\nDashboard telah diupdate dengan hasil analisis."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal melakukan analisis: Pastikan column tweet_text ada di data\n{e}")

    def toggle_theme(self):
        """Toggle theme."""
        new_theme = self.theme_manager.toggle_theme()
        self.setStyleSheet(self.theme_manager.get_current_theme_style())
        self.theme_button.setText(self.theme_manager.get_theme_button_text())