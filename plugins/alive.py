from pyrogram import Client, filters

@Client.on_message(filters.command("alive", prefixes=".") & filters.me)  # type: ignore
async def alive_command(_, message):
    await message.edit("🤖 **Mori-UBOT Menyala Abangku!** 🔥\n\nSemua sistem sinkron dan siap tempur!")
