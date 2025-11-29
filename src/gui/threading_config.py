"""
GUI Configuration untuk Multi-Threading.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MultiThreadingConfig(QWidget):
    """
    Widget konfigurasi multi-threading untuk scraper.

    Memungkinkan user untuk:
    - Enable/disable multi-threading
    - Set jumlah threads (1-5)
    - Lihat estimasi peningkatan kecepatan
    """

    def __init__(self):
        """Inisialisasi Multi-Threading Config Widget."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Setup UI."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Enable checkbox
        self.enable_checkbox = QCheckBox("🚀 Enable Multi-Threading (Parallel Scraping)")
        self.enable_checkbox.setFont(QFont("Arial", 10, QFont.Bold))
        self.enable_checkbox.setChecked(False)
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        layout.addWidget(self.enable_checkbox)

        # Thread count selector
        thread_layout = QHBoxLayout()
        thread_label = QLabel("Jumlah Threads:")
        thread_label.setMinimumWidth(120)

        self.thread_spinbox = QSpinBox()
        self.thread_spinbox.setRange(1, 5)
        self.thread_spinbox.setValue(2)
        self.thread_spinbox.setSuffix(" threads")
        self.thread_spinbox.setEnabled(False)
        self.thread_spinbox.valueChanged.connect(self.on_thread_count_changed)

        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.thread_spinbox)
        thread_layout.addStretch()

        layout.addLayout(thread_layout)

        # Info label
        self.info_label = QLabel("💡 Multi-threading akan meningkatkan kecepatan scraping 2-3x lebih cepat")
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                padding: 10px;
                border-radius: 5px;
                color: #1976d2;
                font-size: 11px;
            }
        """)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # Performance estimate
        self.perf_label = QLabel("⚡ Estimasi: Normal speed")
        self.perf_label.setStyleSheet("font-size: 10px; color: #666; padding: 5px;")
        layout.addWidget(self.perf_label)

        self.setLayout(layout)

    def on_enable_changed(self, state):
        """Handle enable checkbox change."""
        enabled = state == Qt.Checked
        self.thread_spinbox.setEnabled(enabled)
        self.update_performance_estimate()

    def on_thread_count_changed(self, value):
        """Handle thread count change."""
        self.update_performance_estimate()

    def update_performance_estimate(self):
        """Update performance estimate label."""
        if not self.is_enabled():
            self.perf_label.setText("⚡ Estimasi: Normal speed (1x)")
            return

        threads = self.get_thread_count()
        speedup = min(threads * 0.8, 4.0)  # Realistic speedup

        self.perf_label.setText(f"⚡ Estimasi: {speedup:.1f}x lebih cepat dengan {threads} threads")

    def is_enabled(self) -> bool:
        """Check if multi-threading is enabled."""
        return self.enable_checkbox.isChecked()

    def get_thread_count(self) -> int:
        """Get selected thread count."""
        return self.thread_spinbox.value() if self.is_enabled() else 1

    def get_config(self) -> dict:
        """Get configuration dictionary."""
        return {
            'enabled': self.is_enabled(),
            'thread_count': self.get_thread_count()
        }
