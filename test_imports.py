"""
Test script untuk memverifikasi bahwa semua modul dapat di-import dengan benar.
Jalankan script ini untuk memastikan refactoring berhasil.
"""

import sys

def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("Testing Module Imports - Tweet Scraper Refactored")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Config module
    try:
        from src.config import constants
        print("[OK] Config module imported successfully")
        print(f"   - SCROLL_PAUSE_TIME: {constants.SCROLL_PAUSE_TIME}")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Config module import failed: {e}")
        tests_failed += 1

    # Test 2: Core modules
    try:
        from src.core import AdvancedDeduplicator, ProgressTracker, ThemeManager
        print("[OK] Core modules imported successfully")
        print(f"   - AdvancedDeduplicator: {AdvancedDeduplicator}")
        print(f"   - ProgressTracker: {ProgressTracker}")
        print(f"   - ThemeManager: {ThemeManager}")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Core modules import failed: {e}")
        tests_failed += 1

    # Test 3: Scraper modules
    try:
        from src.scraper import setup_driver, parse_tweet_article, scrape_tweets, main_scraping_function
        print("[OK] Scraper modules imported successfully")
        print(f"   - setup_driver: {setup_driver}")
        print(f"   - parse_tweet_article: {parse_tweet_article}")
        print(f"   - scrape_tweets: {scrape_tweets}")
        print(f"   - main_scraping_function: {main_scraping_function}")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Scraper modules import failed: {e}")
        tests_failed += 1

    # Test 4: GUI modules
    try:
        from src.gui import LoggerSignals, TweetScraperGUI
        print("[OK] GUI modules imported successfully")
        print(f"   - LoggerSignals: {LoggerSignals}")
        print(f"   - TweetScraperGUI: {TweetScraperGUI}")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] GUI modules import failed: {e}")
        tests_failed += 1

    # Test 5: Theme styles
    try:
        from src.core.styles import LIGHT_THEME, DARK_THEME
        print("[OK] Theme styles imported successfully")
        print(f"   - LIGHT_THEME length: {len(LIGHT_THEME)} chars")
        print(f"   - DARK_THEME length: {len(DARK_THEME)} chars")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Theme styles import failed: {e}")
        tests_failed += 1

    # Test 6: Create instances
    try:
        from src.core import AdvancedDeduplicator, ProgressTracker, ThemeManager

        dedup = AdvancedDeduplicator()
        tracker = ProgressTracker()
        theme = ThemeManager()

        print("[OK] Core instances created successfully")
        print(f"   - Deduplicator DB: {dedup.db_path}")
        print(f"   - Tracker initialized: {tracker.total_target}")
        print(f"   - Theme current: {theme.current_theme}")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Instance creation failed: {e}")
        tests_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Test Summary:")
    print(f"  [OK] Passed: {tests_passed}")
    print(f"  [FAIL] Failed: {tests_failed}")
    print(f"  Total: {tests_passed + tests_failed}")
    print("=" * 60)

    if tests_failed == 0:
        print("\n*** All tests passed! Refactoring successful! ***")
        return True
    else:
        print(f"\n*** {tests_failed} test(s) failed. Please check the errors above. ***")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
