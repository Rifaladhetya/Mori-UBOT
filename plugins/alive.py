from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("alive", prefixes=".") & filters.me)  # type: ignore
async def alive_command(_, message: Message):
    text = (
        "🤖 **Mori-UBOT Menyala Abangku!** 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Engine:** Pyrogram v2\n"
        "🛡️ **Status:** Localhost / Aktif\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Semua sistem sinkron dan siap tempur!*"
    )
    await message.edit(text)
