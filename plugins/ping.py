import time
from pyrogram import Client, filters

@Client.on_message(filters.command("ping", prefixes=".") & filters.me)  # type: ignore
async def ping_cmd(_, message):
    start = time.perf_counter()
    await message.edit("🏓 **Pinging...**")
    end = time.perf_counter()
    latency = round((end - start) * 1000, 2)
    
    await message.edit(
        f"🏓 **PONG!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📶 **Kecepatan:** `{latency} ms`\n"
        f"🔥 **Status:** Sempurna, Abangku!\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
