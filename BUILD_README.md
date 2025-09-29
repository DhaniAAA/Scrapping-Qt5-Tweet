# Tweet Scraper - Build Instructions

## Metode 1: Menggunakan auto-py-to-exe (Recommended - GUI)

1. Install auto-py-to-exe:
   ```
   pip install auto-py-to-exe
   ```

2. Jalankan script GUI builder:
   ```
   python build_gui.py
   ```

3. Atau jalankan langsung:
   ```
   auto-py-to-exe
   ```

4. Konfigurasi di GUI:
   - Script Location: pilih `main.py`
   - Onefile: pilih "One File"
   - Console Window: pilih "Window Based (hide the console)"
   - Additional Files: tambahkan `requirements.txt`
   - Advanced > Hidden Imports: tambahkan:
     ```
     PyQt5.QtCore,PyQt5.QtGui,PyQt5.QtWidgets,selenium,webdriver_manager,pandas,openpyxl
     ```

5. Klik "Convert .py to .exe"

## Metode 2: Menggunakan PyInstaller langsung

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Jalankan script build:
   ```
   python build_exe.py
   ```

3. Atau gunakan script batch:
   ```
   build.bat
   ```

4. Atau gunakan command sederhana:
   ```
   simple_build.bat
   ```

## Metode 3: Manual PyInstaller Command

```bash
pyinstaller --onefile --windowed --name=TweetScraper main.py
```

## Output

Setelah build berhasil, file executable akan tersedia di:
- `dist/TweetScraper.exe`

## Troubleshooting

### Error: Module not found
- Pastikan semua dependencies terinstall: `pip install -r requirements.txt`
- Tambahkan hidden imports yang hilang

### Error: File not found
- Pastikan `main.py` ada di direktori yang sama
- Periksa path file yang ditambahkan

### Executable tidak jalan
- Test di command prompt: `dist/TweetScraper.exe`
- Periksa antivirus (mungkin memblokir)
- Coba build dengan `--console` untuk melihat error

## Tips

1. **Ukuran file besar**: Normal untuk PyQt5 apps (~50-100MB)
2. **Startup lambat**: Normal untuk first run
3. **Antivirus warning**: Whitelist file atau folder dist/
4. **Testing**: Selalu test di komputer lain sebelum distribusi

## Dependencies yang dibutuhkan

- PyQt5>=5.15.0
- selenium>=4.0.0
- webdriver-manager>=3.8.0
- pandas>=1.3.0
- openpyxl>=3.0.0
