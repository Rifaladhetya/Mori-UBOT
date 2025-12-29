from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from os import getenv
import asyncio

# --- SETUP AKUN ---
api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")
session_string = getenv("SESSION_STRING")

app = Client("mori_ubot", api_id=api_id, api_hash=api_hash, session_string=session_string)

# --- FITUR 1: .ALIVE ---
@app.on_message(filters.command("alive", prefixes=".") & filters.me)
async def alive_command(_, message):
    await message.edit("🤖 **Mori-UBOT Menyala Abangku!** 🔥\n\nSemua sistem sinkron dan siap tempur!")

# --- FITUR 2: .GCAST KHUSUS GRUP ---
@app.on_message(filters.command("gcast", prefixes=".") & filters.me)
async def gcast_handler(client, message):
    # Tentukan apakah reply atau kirim teks biasa
    is_reply = bool(message.reply_to_message)
    
    if is_reply:
        content_msg = message.reply_to_message
        content_text = None
    else:
        if len(message.command) < 2:
            return await message.edit("❌ **Gagal!** Kasih teks atau reply pesan dulu, Abangku!")
        content_text = message.text.split(None, 1)[1]
        content_msg = None

    await message.edit("🔄 **Sedang Sync Database & Mengirim ke Grup...**")
    
    sent = 0
    failed = 0
    
    # Proses Sync: Mengambil semua dialog dan filter hanya grup
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["supergroup", "group"]:
            try:
                if is_reply:
                    await content_msg.copy(dialog.chat.id)
                else:
                    await client.send_message(dialog.chat.id, content_text)
                
                sent += 1
                await asyncio.sleep(0.3)
                
            except FloodWait as e:
                print(f"FloodWait {e.value} detik di {dialog.chat.id}")
                await asyncio.sleep(e.value)
                failed += 1
            except Exception as e:
                print(f"Gagal di {dialog.chat.id}: {e}")
                failed += 1

    await message.edit(
        f"✅ **Broadcast Selesai!**\n\n"
        f"🏘️ Grup Terjangkau: `{sent}`\n"
        f"🔴 Gagal: `{failed}`"
    )

# --- FITUR 3: .INFO USER ---
@app.on_message(filters.command("info", prefixes=".") & filters.me)
async def info_cmd(client, message):
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else "me"
    
    try:
        user = await client.get_users(user_id)
        info_text = (
            f"👤 **INFORMASI PENGGUNA**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"👤 **Nama Depan:** {user.first_name}\n"
            f"👥 **Nama Belakang:** {user.last_name or '-'}\n"
            f"🔗 **Username:** @{user.username or '-'}\n"
            f"🤖 **Bot:** {'Iya' if user.is_bot else 'Bukan'}\n"
            f"🌟 **Premium:** {'Iya' if user.is_premium else 'Bukan'}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await message.edit(info_text)
    except Exception as e:
        await message.edit(f"❌ **Gagal mengambil info:** `{e}`")

# --- FITUR 4: .TAGALL (Mention Semua Anggota) ---
@app.on_message(filters.command("tagall", prefixes=".") & filters.me)
async def tag_all_cmd(client, message):
    if message.chat.type not in ["supergroup", "group"]:
        return await message.edit("❌ **Fitur ini hanya untuk di dalam grup!**")

    input_str = message.text.split(None, 1)[1] if len(message.command) > 1 else "Panggilan Darurat!"
    
    await message.delete()
    
    mentions = f"📣 **{input_str}**\n\n"
    count = 0
    
    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_bot or member.user.is_deleted:
            continue
        mentions += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
        count += 1
        
        if count % 5 == 0:
            await client.send_message(message.chat.id, mentions)
            mentions = ""
            await asyncio.sleep(0.5)

    if mentions:
        await client.send_message(message.chat.id, mentions)

# --- FITUR 5: .HELP MENU ---
@app.on_message(filters.command("help", prefixes=".") & filters.me)
async def help_cmd(_, message):
    help_text = (
        "📜 **MENU BANTUAN MORI-UBOT** 📜\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ `.alive` - Cek status bot\n"
        "🏘️ `.gcast` - Broadcast ke semua grup (Auto-Sync)\n"
        "👤 `.info` - Detail profil (Reply atau sendiri)\n"
        "📣 `.tagall` - Mention semua anggota grup\n"
        "❓ `.help` - Menampilkan menu ini\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *Tips: Gunakan dengan bijak, Abangku!* 🔥"
    )
    await message.edit(help_text)

# --- JALANKAN MESIN ---
print("Bot menyala... Tanpa drama!")
app.run()
