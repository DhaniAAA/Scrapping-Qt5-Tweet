# Tweet Scraper - Enhanced Edition

## Overview
Tweet Scraper is a powerful application for collecting tweet data from X.com (Twitter) with advanced features for data analysis and export.

## Key Features
- Scrape tweets based on keywords and date ranges
- Advanced deduplication system to avoid duplicate data
- Progress tracking with time estimation
- Export to CSV, JSON, and Excel formats
- User-friendly GUI with dark/light themes
- Persistent storage using SQLite database

## System Requirements
- Windows 10/11 (64-bit)
- Active internet connection
- Chrome browser (for webdriver)
- Minimum 4GB RAM
- 500MB free disk space

## How to Use
1. Open the Tweet Scraper application
2. Enter your search keywords
3. Select date range
4. Enter auth token from your browser (see guide below)
5. Click "Start Scraping"

## Getting Auth Token
1. Open X.com in Chrome browser
2. Log in to your account
3. Press F12 to open Developer Tools
4. Select the "Application" or "Storage" tab
5. Select "Cookies" > "https://x.com"
6. Find the cookie named "auth_token"
7. Copy the value from the cookie
8. Paste into the "Auth Token" field in the application

## Building Executable
To build the executable file:
1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the build GUI:
   ```
   python build_gui.py
   ```
3. Follow the on-screen instructions

## Tips for Usage
- Use specific keywords for more relevant results
- Limit date ranges for better performance
- Use appropriate day intervals based on tweet targets
- Save auth token for future use

## Troubleshooting
- If scraping fails, check internet connection
- Ensure auth token is still valid (re-login if needed)
- Restart application if experiencing errors
- Check antivirus that might block webdriver

## License
This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support
For further assistance, please contact the developer or refer to the full documentation.

## Disclaimer
This application is created for research and educational purposes. Ensure usage complies with X.com's Terms of Service and applicable laws.

**Version:** 1.0  
**Date:** 9-29-2025