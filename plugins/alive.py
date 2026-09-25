from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message

LOGO_PATH = Path("assets/logo.png")

@Client.on_message(filters.command("alive", prefixes=".") & filters.me)  # type: ignore
async def alive_command(client: Client, message: Message):
    caption = (
        "🤖 **Mori-UBOT Menyala Abangku!** 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Engine:** Pyrogram v2\n"
        "🛡️ **System:** Localhost / Active\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Semua sistem sinkron dan siap tempur!*"
    )
    
    if LOGO_PATH.exists():
        try:
            await message.delete()
            await client.send_photo(message.chat.id, photo=str(LOGO_PATH), caption=caption)
            return
        except Exception as e:
            print(f"Gagal mengirim foto alive: {e}")
            
    await message.edit(caption)
