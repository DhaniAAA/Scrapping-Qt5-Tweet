"""
Tweet Scraper - Enhanced Edition
Main entry point for the application.

This is a powerful Twitter/X.com scraper with advanced features:
- Advanced deduplication system
- Progress tracking with ETA
- Dark/Light theme support
- Multi-session scraping
- Export to CSV, JSON, or Excel

Author: Tweet Scraper Team
Version: 2.0.0
"""

import sys
from PyQt5.QtWidgets import QApplication

from src.gui import TweetScraperGUI


def run_app():
    """Initialize and run the Tweet Scraper application"""
    app = QApplication(sys.argv)
    window = TweetScraperGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
