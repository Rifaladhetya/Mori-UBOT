from pyrogram import Client, filters

@Client.on_message(filters.command("info", prefixes=".") & filters.me)  # type: ignore
async def info_cmd(client, message):
    if len(message.command) > 1:
        target = message.command[1]
        user_id = int(target) if target.isdigit() else target
    elif message.reply_to_message:
        if message.reply_to_message.from_user:
            user_id = message.reply_to_message.from_user.id
        elif message.reply_to_message.sender_chat:
            user_id = message.reply_to_message.sender_chat.id
        else:
            return await message.edit("❌ **Gagal menentukan pengirim pesan!**")
    else:
        user_id = "me"
    
    try:
        user = await client.get_users(user_id)
        username = f"@{user.username}" if user.username else "-"
        info_text = (
            f"👤 **INFORMASI PENGGUNA**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"👤 **Nama Depan:** {user.first_name}\n"
            f"👥 **Nama Belakang:** {user.last_name or '-'}\n"
            f"🔗 **Username:** {username}\n"
            f"🤖 **Bot:** {'Iya' if user.is_bot else 'Bukan'}\n"
            f"🌟 **Premium:** {'Iya' if getattr(user, 'is_premium', False) else 'Bukan'}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await message.edit(info_text)
    except Exception as e:
        await message.edit(f"❌ **Gagal mengambil info:** `{e}`")
