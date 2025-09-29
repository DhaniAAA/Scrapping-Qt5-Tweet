#!/usr/bin/env python3
"""
GUI Builder untuk Tweet Scraper menggunakan auto-py-to-exe
Alternatif yang lebih mudah untuk membuat executable
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_auto_py_to_exe():
    """Check if auto-py-to-exe is installed"""
    try:
        import auto_py_to_exe
        print("✅ auto-py-to-exe sudah terinstall")
        return True
    except ImportError:
        print("❌ auto-py-to-exe belum terinstall")
        return False

def install_auto_py_to_exe():
    """Install auto-py-to-exe"""
    print("📦 Menginstall auto-py-to-exe...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "auto-py-to-exe"])
        print("✅ auto-py-to-exe berhasil diinstall")
        return True
    except subprocess.CalledProcessError:
        print("❌ Gagal menginstall auto-py-to-exe")
        return False

def create_config_json():
    """Create configuration file for auto-py-to-exe"""
    config = {
        "version": "auto-py-to-exe-configuration_v1",
        "pyinstaller_options": [
            {
                "optionDest": "filenames",
                "value": "main.py"
            },
            {
                "optionDest": "onefile",
                "value": True
            },
            {
                "optionDest": "console",
                "value": False
            },
            {
                "optionDest": "name",
                "value": "TweetScraper"
            },
            {
                "optionDest": "ascii",
                "value": False
            },
            {
                "optionDest": "clean_build",
                "value": True
            },
            {
                "optionDest": "strip",
                "value": False
            },
            {
                "optionDest": "noupx",
                "value": False
            },
            {
                "optionDest": "uac_admin",
                "value": False
            },
            {
                "optionDest": "uac_uiaccess",
                "value": False
            },
            {
                "optionDest": "win_private_assemblies",
                "value": False
            },
            {
                "optionDest": "win_no_prefer_redirects",
                "value": False
            },
            {
                "optionDest": "bootloader_ignore_signals",
                "value": False
            },
            {
                "optionDest": "disable_windowed_traceback",
                "value": False
            },
            {
                "optionDest": "hiddenimports",
                "value": "PyQt5.QtCore,PyQt5.QtGui,PyQt5.QtWidgets,selenium,webdriver_manager,pandas,openpyxl"
            },
            {
                "optionDest": "datas",
                "value": "requirements.txt;."
            }
        ],
        "nonPyinstallerOptions": {
            "increaseRecursionLimit": True,
            "manualArguments": ""
        }
    }
    
    import json
    with open('auto-py-to-exe-config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("✅ File konfigurasi dibuat: auto-py-to-exe-config.json")

def launch_auto_py_to_exe():
    """Launch auto-py-to-exe GUI"""
    print("🚀 Meluncurkan auto-py-to-exe GUI...")
    try:
        # Launch auto-py-to-exe
        subprocess.Popen([sys.executable, "-m", "auto_py_to_exe"])
        print("✅ auto-py-to-exe GUI diluncurkan!")
        print("\n📋 Panduan penggunaan:")
        print("1. Pilih 'main.py' sebagai script location")
        print("2. Pilih 'One File' untuk single executable")
        print("3. Pilih 'Window Based' untuk hide console")
        print("4. Tambahkan 'requirements.txt' di Additional Files")
        print("5. Klik 'Convert .py to .exe'")
        return True
    except Exception as e:
        print(f"❌ Error meluncurkan auto-py-to-exe: {e}")
        return False

def create_simple_build_script():
    """Create simple PyInstaller command"""
    script_content = '''@echo off
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
'''
    
    with open('simple_build.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script build sederhana dibuat: simple_build.bat")

def create_readme():
    """Create README for building executable"""
    readme_content = """# Tweet Scraper - Build Instructions

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
"""
    
    with open('BUILD_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README build instructions dibuat: BUILD_README.md")

def main():
    """Main function"""
    print("🚀 Tweet Scraper - GUI Builder Setup")
    print("=" * 50)
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("❌ File main.py tidak ditemukan!")
        return
    
    # Create helper files
    create_config_json()
    create_simple_build_script()
    create_readme()
    
    print("\n📋 Pilihan build method:")
    print("1. auto-py-to-exe (GUI - Recommended)")
    print("2. Buka README untuk panduan lengkap")
    
    choice = input("\nPilih metode (1-2): ").strip()
    
    if choice == "1":
        if not check_auto_py_to_exe():
            if not install_auto_py_to_exe():
                return
        launch_auto_py_to_exe()
        
    elif choice == "2":
        if os.path.exists('BUILD_README.md'):
            try:
                # Try to open with default text editor
                os.startfile('BUILD_README.md')
            except:
                print("Buka file BUILD_README.md untuk panduan lengkap")
        
    else:
        print("Pilihan tidak valid")

if __name__ == "__main__":
    main()
