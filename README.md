# 🤖 Mori-UBOT

Userbot Telegram sederhana berbasis Pyrogram v2 dengan sistem arsitektur Modular Plugin & Hot-Reload.

> ⚠️ **Pemberitahuan Penting:**  
> Repositori ini **hanya dirancang dan dioptimalkan untuk berjalan di localhost / server lokal** (PC, Laptop, atau VPS pribadi). Tidak direkomendasikan untuk platform cloud serverless tanpa persistent storage karena sesi autentikasi (`*.session`) disimpan secara lokal di mesin Anda.

---

## 💻 Panduan Menjalankan di Localhost

### 1. Kloning Repo & Masuk ke Folder
```bash
git clone https://github.com/jarvisnya/Mori-UBOT.git
cd Mori-UBOT
```

### 2. Pasang Virtual Environment & Dependensi
Disarankan menggunakan Python 3.10 atau 3.11:
```bash
# Menggunakan uv (direkomendasikan):
uv venv --python 3.11
uv pip install -r requirements.txt

# ATAU menggunakan venv bawaan Python:
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Konfigurasi Lingkungan (`.env`)
Salin file template `.env.example`:
```bash
cp .env.example .env
```
Buka file `.env` dan isi kredensial Telegram milik Anda sendiri:
```env
API_ID=12345678
API_HASH=abcdef0123456789abcdef0123456789
SESSION_STRING=
```
- `API_ID` & `API_HASH`: Dapatkan dari https://my.telegram.org.
- `SESSION_STRING`: Kosongkan saja untuk penggunaan lokal. Pyrogram akan meminta nomor telepon dan kode OTP di terminal saat pertama kali dijalankan, lalu otomatis menyimpan sesi login secara lokal ke file `mori_ubot.session`.

### 4. Menjalankan Bot
```bash
python main.py
```

---

## 🔒 Keamanan & Privasi
- File kredensial (`.env`), string sesi, dan file database sesi (`*.session`) telah masuk ke `.gitignore` sehingga tidak akan terunggah ke repositori publik.
- **Peringatan:** Jangan pernah membagikan file `.env` atau `mori_ubot.session` Anda kepada siapa pun.
