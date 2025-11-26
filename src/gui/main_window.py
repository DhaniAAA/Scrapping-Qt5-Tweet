"""
Main GUI window for Tweet Scraper application.
"""

from typing import Dict, Any
from threading import Thread, Event

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QComboBox,
    QPushButton, QTextEdit, QSpinBox, QGridLayout, QGroupBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QProgressBar,
    QHBoxLayout, QCheckBox, QFrame, QSplitter
)
from PyQt5.QtCore import QDate, Qt

from ..config.constants import WINDOW_WIDTH, WINDOW_HEIGHT, MIN_LEFT_PANEL_WIDTH, MAX_LEFT_PANEL_WIDTH
from ..core import ThemeManager
from ..scraper import main_scraping_function
from .signals import LoggerSignals


class TweetScraperGUI(QWidget):
    """Main GUI window for the Tweet Scraper application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tweet Scraper X.com - Enhanced Edition")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        # Apply initial theme
        self.setStyleSheet(self.theme_manager.get_current_theme_style())

        # Create left panel for controls and right panel for output
        self.create_left_panel()
        self.create_right_panel()

        # Add panels to main layout
        main_layout.addWidget(self.left_panel, 2)
        main_layout.addWidget(self.right_panel, 1)

    def create_left_panel(self):
        """Create left panel with compact horizontal layout"""
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(MIN_LEFT_PANEL_WIDTH)
        self.left_panel.setMaximumWidth(MAX_LEFT_PANEL_WIDTH)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(15, 15, 15, 15)
        self.left_panel.setLayout(left_layout)

        # Header with theme toggle
        header_layout = QHBoxLayout()
        title_label = QLabel("Tweet Scraper")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.theme_button = QPushButton(self.theme_manager.get_theme_button_text())
        self.theme_button.setObjectName("themeBtn")
        self.theme_button.setFixedHeight(35)
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
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(10)

        # Create each section as a widget
        search_widget = self.create_search_section_widget()
        date_widget = self.create_date_section_widget()
        options_widget = self.create_options_section_widget()
        auth_widget = self.create_auth_section_widget()

        # Add sections to horizontal layout
        horizontal_layout.addWidget(search_widget, 1)
        horizontal_layout.addWidget(date_widget, 1)
        horizontal_layout.addWidget(options_widget, 1)
        horizontal_layout.addWidget(auth_widget, 1)

        parent_layout.addLayout(horizontal_layout)

    def create_search_section_widget(self):
        """Create search parameters section as a widget"""
        search_group = QGroupBox("🔍 Parameter Pencarian")
        search_layout = QVBoxLayout()
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
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        control_group.setLayout(control_layout)

        # Start and Stop buttons side by side
        self.start_button = QPushButton("▶️ Mulai Scraping")
        self.start_button.setObjectName("startBtn")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_scraping)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("⏹️ Stop Scraping")
        self.stop_button.setObjectName("stopBtn")
        self.stop_button.setMinimumHeight(40)
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
        right_layout.setContentsMargins(10, 15, 15, 15)
        right_layout.setSpacing(10)
        self.right_panel.setLayout(right_layout)

        # Tabs for log and data
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(400)

        # Log tab
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(self.log_output.font())
        self.tabs.addTab(self.log_output, "📝 Log")

        # Data preview tab
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
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

        right_layout.addWidget(self.tabs, 1)
        right_layout.addLayout(status_layout)

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

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        new_theme = self.theme_manager.toggle_theme()
        self.setStyleSheet(self.theme_manager.get_current_theme_style())
        self.theme_button.setText(self.theme_manager.get_theme_button_text())
        self.append_log(f"Tema diubah ke: {new_theme}")

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

    def on_scraping_finished(self):
        """Handle scraping finished event"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.append_log("\n--- Proses Selesai ---")
        if self.progress_bar.value() < self.progress_bar.maximum():
             self.append_log("Proses mungkin tidak selesai sepenuhnya atau dihentikan.")
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.scraping_thread = None

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
        """Run scraper in separate thread"""
        try:
            main_scraping_function(**args)
        except Exception as e:
            self.signals.log_signal.emit(f"\n!!! Terjadi kesalahan fatal: {e} !!!")
        finally:
            self.signals.finished_signal.emit()
