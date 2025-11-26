"""
Theme management system with persistent storage.
"""

from PyQt5.QtCore import QSettings

from .styles.themes import LIGHT_THEME, DARK_THEME


class ThemeManager:
    """Sistem manajemen tema dark/light dengan persistent storage"""

    def __init__(self):
        self.settings = QSettings("TweetScraper", "Themes")
        self.current_theme = self.settings.value("theme", "light", type=str)

    def get_current_theme_style(self) -> str:
        """Get current theme stylesheet"""
        if self.current_theme == "dark":
            return DARK_THEME
        else:
            return LIGHT_THEME

    def toggle_theme(self) -> str:
        """Toggle between light and dark theme"""
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"

        # Save to settings
        self.settings.setValue("theme", self.current_theme)
        return self.current_theme

    def get_theme_button_text(self) -> str:
        """Get appropriate button text for current theme"""
        if self.current_theme == "light":
            return "🌙 Mode Gelap"
        else:
            return "☀️ Mode Terang"
