# 🤖 Mori-UBOT

Userbot Telegram sederhana berbasis Pyrogram v2. Bisa dijalankan di komputer lokal (Windows/Linux/macOS) maupun deploy di cloud (Koyeb/Heroku).

---

## 🛠️ Fitur Tersedia
- `.alive` - Cek status bot.
- `.gcast <pesan / reply>` - Broadcast pesan ke semua grup/supergroup.
- `.info <reply / username / ID>` - Cek profil detail pengguna Telegram.
- `.tagall <pesan>` - Mention semua member di dalam grup.
- `.help` - Menampilkan daftar perintah bantuan.

---

## 💻 Cara Menjalankan di Lokal (PC / Laptop)

### 1. Kloning Repo & Masuk ke Folder
```bash
git clone https://github.com/Rifaladhetya/Mori-UBOT.git
cd Mori-UBOT
```

### 2. Buat Virtual Environment & Install Dependensi
Disarankan menggunakan Python 3.10 atau 3.11:
```bash
# Menggunakan uv (cepat):
uv venv --python 3.11
uv pip install -r requirements.txt

# ATAU menggunakan python standar:
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Konfigurasi Lingkungan (`.env`)
Salin file template `.env.example`:
```bash
cp .env.example .env
```
Buka file `.env` dan isi:
- `API_ID`: ID aplikasi dari https://my.telegram.org
- `API_HASH`: Hash aplikasi dari https://my.telegram.org
- `SESSION_STRING`: *(Opsional)* Jika dikosongkan, Pyrogram akan meminta nomor HP dan OTP di terminal untuk membuat file `mori_ubot.session` secara lokal.

### 4. Jalankan Bot
```bash
python main.py
```

---

## ☁️ Deploy ke Koyeb (24 Jam)
Siapkan `API_ID`, `API_HASH`, dan `SESSION_STRING` (wajib untuk cloud), lalu klik tombol di bawah:

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/Rifaladhetya/Mori-UBOT&branch=main&name=mori-ubot)
