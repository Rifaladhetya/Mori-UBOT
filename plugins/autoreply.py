import json
import time
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message

DATA_FILE = Path("autoreply_data.json")
COOLDOWN_SECONDS = 24 * 3600  # 24 Jam

DEFAULT_MESSAGE = (
    "Halo! 👋 Terima kasih sudah menghubungi.\n\n"
    "Pesan Anda sudah diterima. Saya saat ini sedang ada kesibukan atau offline, "
    "dan akan segera membalas begitu senggang. Terima kasih atas pengertiannya! 🙏\n\n"
    "*(Pesan otomatis • Terkirim 1x per 24 jam)*"
)


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"enabled": True, "custom_message": None, "history": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Gagal membaca autoreply_data.json: {e}")
        return {"enabled": True, "custom_message": None, "history": {}}


def save_data(data: dict):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Gagal menyimpan autoreply_data.json: {e}")


# --- HANDLER: AUTO-REPLY PESAN MASUK ---
@Client.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot & ~filters.service)  # type: ignore
async def incoming_private_autoreply(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = str(message.from_user.id)

    # Abaikan akun resmi Telegram / Service (ID 777000)
    if message.from_user.id == 777000:
        return

    data = load_data()
    if not data.get("enabled", True):
        return

    now = time.time()
    history = data.setdefault("history", {})
    last_reply_time = history.get(user_id, 0)

    # Cek apakah sudah lewat 24 jam
    if now - last_reply_time >= COOLDOWN_SECONDS:
        text_to_send = data.get("custom_message") or DEFAULT_MESSAGE
        try:
            await message.reply_text(text_to_send)
            # Update riwayat cooldown user
            history[user_id] = now
            save_data(data)
            print(f"📩 [AUTOREPLY] Terkirim ke user {user_id} ({message.from_user.first_name})")
        except Exception as e:
            print(f"❌ [AUTOREPLY ERROR] Gagal mengirim ke {user_id}: {e}")


# --- COMMAND: KONTROL AUTOREPLY (.autoreply) ---
@Client.on_message(filters.command("autoreply", prefixes=".") & filters.me)  # type: ignore
async def autoreply_control(_, message: Message):
    args = message.command
    data = load_data()

    if len(args) == 1 or args[1].lower() == "status":
        status_str = "🟢 **AKTIF**" if data.get("enabled", True) else "🔴 **NONAKTIF**"
        msg = data.get("custom_message") or DEFAULT_MESSAGE
        total_users = len(data.get("history", {}))
        
        reply_text = (
            f"🤖 **STATUS AUTO-REPLY 24 JAM**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **Status:** {status_str}\n"
            f"👥 **User dalam Cooldown:** `{total_users}` orang\n"
            f"⏱️ **Interval Cooldown:** `24 Jam`\n\n"
            f"📝 **Teks Saat Ini:**\n{msg}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Perintah Tersedia:*\n"
            f"• `.autoreply on` / `.autoreply off`\n"
            f"• `.setautoreply <teks baru>` (ganti isi pesan)\n"
            f"• `.resetautoreply` (reset cooldown semua user)"
        )
        return await message.edit(reply_text)

    action = args[1].lower()
    if action == "on":
        data["enabled"] = True
        save_data(data)
        await message.edit("✅ **Fitur Auto-Reply 24 Jam BERHASIL DIAKTIFKAN!**")
    elif action == "off":
        data["enabled"] = False
        save_data(data)
        await message.edit("🛑 **Fitur Auto-Reply 24 Jam DINONAKTIFKAN!**")
    else:
        await message.edit("❌ **Perintah salah!** Gunakan `.autoreply on`, `.autoreply off`, atau `.autoreply status`")


# --- COMMAND: SET CUSTOM PESAN (.setautoreply) ---
@Client.on_message(filters.command("setautoreply", prefixes=".") & filters.me)  # type: ignore
async def set_autoreply_text(_, message: Message):
    if len(message.command) < 2:
        return await message.edit("❌ **Gagal!** Berikan teks pesan baru setelah perintah.\nContoh: `.setautoreply Halo, saya sedang rapat.`")

    new_text = message.text.split(None, 1)[1]
    data = load_data()
    data["custom_message"] = new_text
    save_data(data)
    await message.edit(f"✅ **Pesan Auto-Reply berhasil diubah!**\n\n📝 **Teks Baru:**\n{new_text}")


# --- COMMAND: RESET COOLDOWN (.resetautoreply) ---
@Client.on_message(filters.command("resetautoreply", prefixes=".") & filters.me)  # type: ignore
async def reset_autoreply_history(_, message: Message):
    data = load_data()
    total = len(data.get("history", {}))
    data["history"] = {}
    save_data(data)
    await message.edit(f"🔄 **Riwayat cooldown {total} pengguna telah di-reset!** Semua user akan menerima auto-reply lagi pada pesan pertama berikutnya.")
