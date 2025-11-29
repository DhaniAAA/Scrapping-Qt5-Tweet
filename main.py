"""
Tweet Scraper - Performance Edition v2.3.0
Main entry point for the application.

This is a powerful Twitter/X.com scraper with advanced features:
- Advanced deduplication system
- Progress tracking with ETA
- Dark/Light theme support
- Multi-session scraping
- Export to CSV, JSON, or Excel
- **NEW v2.3.0** Multi-Threading (2-5x faster!)

Author: DhaniAAA
Version: 2.3.0

"""

import sys
from PyQt5.QtWidgets import QApplication

from src.gui.main_window_v2 import TweetScraperGUIV2


def run_app():
    """Initialize and run the Tweet Scraper application v2.3.0"""
    app = QApplication(sys.argv)
    window = TweetScraperGUIV2()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
