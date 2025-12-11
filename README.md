# Tweet Scraper X.com (v2.3.3)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green) ![Selenium](https://img.shields.io/badge/Selenium-WebScraping-orange)

**[English Version]** | [Versi Bahasa Indonesia](#tweet-scraper-xcom--indonesian-version)

---

## 🇬🇧 English Version

### Overview

A powerful and user-friendly desktop application for scraping tweets from X.com (formerly Twitter). Built with **Python** and **PyQt5**, it offers advanced features like parallel scraping, sentiment analysis, trend detection, and a comprehensive analytics dashboard.

### Key Features

- **🚀 Multi-Threaded Scraping**: Significantly faster data collection using parallel threads.
- **📊 Analytics Dashboard**: Built-in visualization for sentiment distribution (Pie Chart), top hashtags, and keywords (Bar Charts).
- **🧠 Custom Sentiment Analysis**: Uses a specialized Indonesian lexicon (`modified-lexicon_v2.txt`) for accurate sentiment scoring (Positive, Negative, Neutral).
- **📈 Trend Detection**: Automatically identifies trending topics and keywords from scraped data.
- **💾 Flexible Export**: Save data in **CSV**, **JSON**, or **Excel** formats.
- **🔔 Smart Notifications**: Desktop notifications and sound alerts ("Ting!") when scraping finishes or errors occur.
- **🎨 Modern UI**: Responsive GUI with Dark/Light mode support.
- **🔐 Authentication**: Supports cookie-based authentication to scrape deeper and faster.

### Prerequisites

- Python 3.8 or higher
- Google Chrome Browser
- Internet Connection

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/YourUsername/TweetScrapper.git
    cd TweetScrapper
    ```

2.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    _Note: Ensure `selenium`, `pandas`, `PyQt5`, `matplotlib`, `openpyxl`, and `winsound` (windows default) are installed._

3.  **Prepare Lexicon**
    Ensure `modified-lexicon_v2.txt` is present in the project root for sentiment analysis to work correctly.

### Usage

1.  **Run the Application**

    ```bash
    python main.py
    ```

2.  **Login / Auth Token**

    - To ensure uninterrupted scraping, paste your X.com `auth_token` cookie into the "Autentikasi" field in the GUI.

3.  **Start Scraping**

    - Enter a **Keyword** (e.g., "Python", "#AI").
    - Select **Search Type** (Latest/Top).
    - Set **Date Range** and **Limit**.
    - (Optional) Enable **Multi-Threading** for speed.
    - Click **▶️ Mulai Scraping**.

4.  **View Analytics**
    - Once finished, switch to the **Analytics Dashboard** tab to view charts and statistics.

### Project Structure

```
TweetScrapper/
├── src/
│   ├── analysis/       # Sentiment & Trend logic
│   ├── config/         # Constants
│   ├── core/           # Deduplicator, Theme Manager
│   ├── gui/            # PyQt5 Windows & Widgets
│   └── scraper/        # Selenium Scraper Logic
├── modified-lexicon_v2.txt  # Custom Sentiment Lexicon
├── main.py             # Entry point
└── README.md           # Documentation
```

### Disclaimer

This tool is for educational and research purposes only. Please respect X.com's Terms of Service and `robots.txt` policies. Users are responsible for how they use the scraped data.

---

<br>

## 🇮🇩 Tweet Scraper X.com - Indonesian Version

### Ringkasan

Aplikasi desktop yang canggih dan mudah digunakan untuk mengambil data tweet dari X.com (Twitter). Dibangun dengan **Python** dan **PyQt5**, aplikasi ini menawarkan fitur-fitur seperti scraping paralel, analisis sentimen, deteksi tren, dan dashboard analitik yang lengkap.

### Fitur Utama

- **🚀 Scraping Multi-Thread**: Pengumpulan data jauh lebih cepat menggunakan _parallel threads_ (banyak proses sekaligus).
- **📊 Dashboard Analitik**: Visualisasi bawaan untuk distribusi sentimen (Digram Lingkaran), top hashtag, dan kata kunci (Diagram Batang).
- **🧠 Analisis Sentimen Khusus**: Menggunakan kamus bahasa Indonesia khusus (`modified-lexicon_v2.txt`) untuk penilaian sentimen yang akurat (Positif, Negatif, Netral).
- **📈 Deteksi Tren**: Mengidentifikasi topik dan kata kunci yang sedang tren secara otomatis dari data yang diambil.
- **💾 Ekspor Fleksibel**: Simpan data dalam format **CSV**, **JSON**, atau **Excel**.
- **🔔 Notifikasi Pintar**: Notifikasi desktop dan suara ("Ting!") saat proses selesai atau terjadi error.
- **🎨 UI Modern**: Tampilan antarmuka responsif dengan dukungan Mode Gelap/Terang.
- **🔐 Autentikasi**: Mendukung penggunaan cookie autentikasi untuk akses scraping yang lebih dalam dan stabil.

### Prasyarat

- Python 3.8 atau lebih baru
- Browser Google Chrome
- Koneksi Internet

### Instalasi

1.  **Clone repositori**

    ```bash
    git clone https://github.com/UsernameAnda/TweetScrapper.git
    cd TweetScrapper
    ```

2.  **Install dependensi**

    ```bash
    pip install -r requirements.txt
    ```

    _Catatan: Pastikan `selenium`, `pandas`, `PyQt5`, `matplotlib`, `openpyxl`, dan library pendukung lainnya terinstall._

3.  **Siapkan Lexicon**
    Pastikan file `modified-lexicon_v2.txt` ada di folder utama proyek agar analisis sentimen bahasa Indonesia berfungsi.

### Cara Penggunaan

1.  **Jalankan Aplikasi**

    ```bash
    python main.py
    ```

2.  **Login / Token Auth**

    - Masukkan cookie `auth_token` akun X.com Anda ke kolom "Autentikasi" di aplikasi untuk hasil terbaik.

3.  **Mulai Scraping**

    - Masukkan **Kata Kunci** (misal: "Pemilu", "#Teknologi").
    - Pilih **Tipe Pencarian** (Latest/Top).
    - Atur **Rentang Tanggal** dan **Jumlah Tweet**.
    - (Opsional) Aktifkan **Multi-Threading** di menu opsi untuk kecepatan ekstra.
    - Klik **▶️ Mulai Scraping**.

4.  **Lihat Analitik**
    - Setelah selesai, pindah ke tab **Analytics Dashboard** untuk melihat grafik sentimen dan tren data yang baru saja diambil.

### Struktur Proyek

```
TweetScrapper/
├── src/
│   ├── analysis/       # Logika Sentimen & Tren
│   ├── config/         # Konstanta
│   ├── core/           # Deduplikator, Manajer Tema
│   ├── gui/            # Jendela & Widget PyQt5
│   └── scraper/        # Logika Selenium Scraper
├── modified-lexicon_v2.txt  # Kamus Sentimen Custom
├── main.py             # File Utama
└── README.md           # Dokumentasi
```

### Penafian (Disclaimer)

Alat ini dibuat hanya untuk tujuan pendidikan dan penelitian. Harap hormati Ketentuan Layanan (Terms of Service) X.com. Pengguna bertanggung jawab penuh atas penggunaan data yang diambil.
