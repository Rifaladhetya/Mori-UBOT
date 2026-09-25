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
        "🛡️ **Status:** Localhost / Aktif\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Semua sistem sinkron dan siap tempur!*"
    )
    
    if LOGO_PATH.exists():
        try:
            send_kwargs = {
                "chat_id": message.chat.id,
                "photo": str(LOGO_PATH),
                "caption": caption,
            }
            if message.reply_to_message:
                send_kwargs["reply_to_message_id"] = message.reply_to_message.id
            await client.send_photo(**send_kwargs)
            await message.delete()
            return
        except Exception as e:
            print(f"Gagal kirim foto alive, fallback ke teks: {e}")

    await message.edit(caption)
