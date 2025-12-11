"""
Qt signals for communication between threads and GUI.
"""

from PyQt5.QtCore import QObject, pyqtSignal


class LoggerSignals(QObject):
    """Signals for updating GUI from scraping thread"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    progress_signal = pyqtSignal(int, int)
    data_row_signal = pyqtSignal(dict)
    stats_signal = pyqtSignal(dict)  # Signal for progress statistics
    notification_signal = pyqtSignal(str, str)  # title, message
