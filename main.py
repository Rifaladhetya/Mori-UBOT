from pyrogram import Client, filters
from os import getenv
import asyncio

api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")
session_string = getenv("SESSION_STRING")

app = Client("my_bot", api_id=api_id, api_hash=api_hash, session_string=session_string)

@app.on_message(filters.command("alive", prefixes=".") & filters.me)
async def alive_command(_, message):
    await message.edit("🤖 **Sistem Userbot: ONLINE!**\n\nSiap melayani Paduka Raja! 👑")

print("Bot sedang berjalan... Jangan lupa napas!")

# --- G-Cast Khusus Grup ---
@app.on_message(filters.command("gcast", prefixes=".") & filters.me)
async def gcast_handler(client, message):
    msg = message.reply_to_message or message
    
    if message.reply_to_message:
        content = message.reply_to_message
    else:
        if len(message.command) < 2:
            return await message.edit("❌ **Gagal!** Berikan teks atau balas ke pesan.")
        content = message.text.split(None, 1)[1]

    await message.edit("🏘️ **Sinkronisasi Database & Memulai Broadcast...**")
    
    sent = 0
    failed = 0
    
    # Kita pakai get_dialogs() untuk memaksa bot mendata ulang semua chat
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["supergroup", "group"]:
            try:
                # Kita kirim ke ID yang sudah diverifikasi oleh dialog
                if message.reply_to_message:
                    await content.copy(dialog.chat.id)
                else:
                    await client.send_message(dialog.chat.id, content)
                sent += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"Gagal kirim ke {dialog.chat.id}: {e}")
                failed += 1
                continue

    await message.edit(f"✅ **Broadcast Grup Selesai!**\n\n🏘️ Grup Berhasil: `{sent}`\n🔴 Gagal: `{failed}`")

app.run()


