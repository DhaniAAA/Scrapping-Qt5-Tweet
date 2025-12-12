"""
Author: DhaniAAA
Version: 2.3.3

"""

import sys
from PyQt5.QtWidgets import QApplication

from src.gui.main_window_v2 import TweetScraperGUIV2


def run_app():
    """Initialize and run the Tweet Scraper application v2.3.3"""
    app = QApplication(sys.argv)
    window = TweetScraperGUIV2()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
