"""
Tweet parsing functionality.
"""

from typing import Dict, Any, Callable, Optional
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


def parse_tweet_article(tweet_article: Any, logger: Callable[[str], None]) -> Optional[Dict[str, Any]]:
    """
    Parse a tweet article element and extract tweet data.

    Args:
        tweet_article: Selenium WebElement yang mewakili sebuah tweet
        logger: Fungsi pencatatan untuk melaporkan kesalahan

    Returns:
        Dict yang berisi data tweet atau None jika penguraian gagal
    """
    try:
        tweet_url_elements = tweet_article.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
        tweet_url = tweet_url_elements[0].get_attribute('href') if tweet_url_elements else None
        if not tweet_url:
            return None

        username = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']//span").text
        handle = tweet_article.find_element(By.XPATH, ".//span[contains(text(), '@')]").text
        timestamp = tweet_article.find_element(By.XPATH, ".//time").get_attribute('datetime')
        # Try to expand "Show more" if present
        try:
            show_more = tweet_article.find_elements(By.XPATH, ".//span[contains(text(), 'Show more')]")
            if show_more:
                show_more[0].click()
                # Short sleep might be needed for text to expand in some cases,
                # but often Selenium wait is implicit if we access text immediately after?
                # Let's hope the text update is instant or handled by next finding.
        except Exception:
            pass  # If click fails, continue with whatever text is visible

        tweet_text = tweet_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text.replace('\n', ' ')
        reply_count = tweet_article.find_element(By.XPATH, ".//button[@data-testid='reply']").text or "0"
        retweet_count = tweet_article.find_element(By.XPATH, ".//button[@data-testid='retweet']").text or "0"
        like_count = tweet_article.find_element(By.XPATH, ".//button[@data-testid='like']").text or "0"

        return {
            "username": username,
            "handle": handle,
            "timestamp": timestamp,
            "tweet_text": tweet_text,
            "url": tweet_url,
            "reply_count": reply_count,
            "retweet_count": retweet_count,
            "like_count": like_count
        }
    except (NoSuchElementException, StaleElementReferenceException) as e:
        logger(f"Peringatan: Gagal mem-parsing satu tweet, melompati. Kesalahan: {e}")
        return None
