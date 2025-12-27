from pyrogram import Client, filters
from os import getenv

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
app.run()