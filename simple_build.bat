@echo off
echo Building Tweet Scraper with PyInstaller...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name=TweetScraper ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=selenium ^
    --hidden-import=webdriver_manager ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --add-data="requirements.txt;." ^
    --clean ^
    main.py

echo.
echo Build completed! Check the 'dist' folder for TweetScraper.exe
pause
