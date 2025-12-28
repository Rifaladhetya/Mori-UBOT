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
    # Logika ambil konten (teks atau reply)
    msg = message.reply_to_message or message
    
    if message.reply_to_message:
        content = message.reply_to_message
    else:
        if len(message.command) < 2:
            return await message.edit("❌ **Gagal!** Berikan teks atau balas ke pesan.")
        content = message.text.split(None, 1)[1]

    await message.edit("🏘️ **Menyebarkan pesan massal HANYA ke Grup...**")
    
    sent = 0
    failed = 0
    
    async for dialog in client.get_dialogs():
        try:
            # FILTER : Hanya Supergroup dan Group (Menghapus 'private')
            if dialog.chat.type in ["supergroup", "group"]:
                if message.reply_to_message:
                    await content.copy(dialog.chat.id)
                else:
                    await client.send_message(dialog.chat.id, content)
                sent += 1
                await asyncio.sleep(0.3) # Jeda aman biar gak disangka robot (ya emang bot sih)
        except Exception:
            failed += 1
            continue

    await message.edit(f"✅ **Broadcast Grup Selesai!**\n\n🏘️ Grup Berhasil: `{sent}`\n🔴 Gagal/Dilarang: `{failed}`")

app.run()

