from pyrogram import Client, filters

@Client.on_message(filters.command("help", prefixes=".") & filters.me)  # type: ignore
async def help_cmd(_, message):
    help_text = (
        "📜 **MENU BANTUAN MORI-UBOT** 📜\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ `.alive` - Cek status bot\n"
        "🏘️ `.gcast <teks/reply>` - Broadcast ke semua grup\n"
        "👤 `.info <reply/user/id>` - Detail profil Telegram\n"
        "📣 `.tagall <pesan>` - Mention semua anggota grup\n"
        "🔄 `.reload [plugin]` - Hot-reload plugin tanpa restart\n"
        "⚡ `.restart` - Restart bot penuh\n"
        "📦 `.plugins` - Daftar plugin aktif\n"
        "❓ `.help` - Menampilkan menu ini\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *Tips: Gunakan dengan bijak, Abangku!* 🔥"
    )
    await message.edit(help_text)
