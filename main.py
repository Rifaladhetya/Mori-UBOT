from pyrogram import Client, filters
from os import getenv
import asyncio

# Mengambil variabel rahasia dari server (biar aman dari mata-mata)
api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")
session_string = getenv("SESSION_STRING")

app = Client("my_bot", api_id=api_id, api_hash=api_hash, session_string=session_string)

@app.on_message(filters.command("alive", prefixes=".") & filters.me)
async def alive_command(_, message):
    # Biar kelihatan keren, kita edit pesannya
    await message.edit("🤖 **Sistem Userbot: ONLINE!**\n\nSiap melayani Paduka Raja! 👑")

print("Bot sedang berjalan... Jangan lupa napas!")

# --- FITUR: G-Cast (Global Broadcast) ---
@app.on_message(filters.command("gcast", prefixes=".") & filters.me)
async def gcast_handler(client, message):
    # Cek apakah kamu mereply sebuah pesan atau mengetik teks setelah perintah
    msg = message.reply_to_message or message
    
    # Ambil teks/media yang mau di-broadcast
    if message.reply_to_message:
        content = message.reply_to_message
    else:
        if len(message.command) < 2:
            return await message.edit("❌ **Gagal!** Berikan teks atau balas ke sebuah pesan.")
        content = message.text.split(None, 1)[1]

    await message.edit("🚀 **Memulai Broadcast ke seluruh obrolan...**")
    
    sent = 0
    failed = 0
    
    # Ambil semua daftar obrolan (Dialogs)
    async for dialog in client.get_dialogs():
        try:
            # Kirim pesan ke Grup (Supergroup/Group) dan Private Chat
            if dialog.chat.type in ["supergroup", "group", "private"]:
                if message.reply_to_message:
                    await content.copy(dialog.chat.id)
                else:
                    await client.send_message(dialog.chat.id, content)
                sent += 1
                await asyncio.sleep(0.3) # Jeda sedikit biar gak kena spam/limit Telegram
        except Exception:
            failed += 1
            continue

    await message.edit(f"✅ **Broadcast Selesai!**\n\n🟢 Berhasil: `{sent}`\n🔴 Gagal: `{failed}`")

app.run()
