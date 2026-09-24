import asyncio
import os
import sys
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

raw_api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")

# Validasi kredensial dasar
if not raw_api_id or not api_hash:
    print("❌ [ERROR] API_ID atau API_HASH belum disetel!")
    print("👉 Salin file '.env.example' menjadi '.env' lalu isi kredensial Telegram kamu:")
    print("   API_ID=12345678")
    print("   API_HASH=abcdef0123456789abcdef0123456789")
    print("   SESSION_STRING= (opsional jika jalan di lokal, Pyrogram akan buat sesi .session otomatis)")
    sys.exit(1)

try:
    api_id = int(raw_api_id)
except ValueError:
    print(f"❌ [ERROR] API_ID harus berupa angka integer, bukan: '{raw_api_id}'")
    sys.exit(1)

# Inisialisasi client
# Jika session_string tidak diisi, Pyrogram akan login interaktif via terminal dan menyimpan mori_ubot.session
client_kwargs = {
    "name": "mori_ubot",
    "api_id": api_id,
    "api_hash": api_hash,
}
if session_string and session_string.strip():
    client_kwargs["session_string"] = session_string.strip()

app = Client(**client_kwargs)

# --- FITUR 1: .ALIVE ---
@app.on_message(filters.command("alive", prefixes=".") & filters.me)
async def alive_command(_, message):
    await message.edit("🤖 **Mori-UBOT Menyala Abangku!** 🔥\n\nSemua sistem sinkron dan siap tempur!")

# --- FITUR 2: .GCAST KHUSUS GRUP ---
@app.on_message(filters.command("gcast", prefixes=".") & filters.me)
async def gcast_handler(client, message):
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
    
    # Mengambil semua dialog dan filter hanya grup / supergroup
    async for dialog in client.get_dialogs():
        if dialog.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
            chat_id = dialog.chat.id
            try:
                # Validasi peer ID
                try:
                    await client.resolve_peer(chat_id)
                except Exception as resolve_error:
                    print(f"Peer ID invalid, skip: {chat_id} - {resolve_error}")
                    failed += 1
                    continue
                
                # Kirim pesan
                if is_reply:
                    await content_msg.copy(chat_id)
                else:
                    await client.send_message(chat_id, content_text)
                
                sent += 1
                await asyncio.sleep(0.3)
                
            except FloodWait as e:
                wait_time = int(getattr(e, "value", 10))
                print(f"FloodWait {wait_time} detik di {dialog.chat.id}")
                await asyncio.sleep(wait_time)
                failed += 1
            except (ValueError, KeyError) as e:
                print(f"Peer error di {dialog.chat.id}: {e}")
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

# --- FITUR 4: .TAGALL (Mention Semua Anggota) ---
@app.on_message(filters.command("tagall", prefixes=".") & filters.me)
async def tag_all_cmd(client, message):
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        return await message.edit("❌ **Fitur ini hanya untuk di dalam grup!**")

    input_str = message.text.split(None, 1)[1] if len(message.command) > 1 else "Panggilan Darurat!"
    
    await message.delete()
    
    mentions = f"📣 **{input_str}**\n\n"
    count = 0
    
    async for member in client.get_chat_members(message.chat.id):
        if not member.user or member.user.is_bot or member.user.is_deleted:
            continue
        first_name = member.user.first_name or "Pengguna"
        mentions += f"[{first_name}](tg://user?id={member.user.id}) "
        count += 1
        
        if count % 5 == 0:
            await client.send_message(message.chat.id, mentions)
            mentions = f"📣 **{input_str}**\n\n"
            count = 0
            await asyncio.sleep(0.5)

    if count > 0 and mentions != f"📣 **{input_str}**\n\n":
        await client.send_message(message.chat.id, mentions)

# --- FITUR 5: .HELP MENU ---
@app.on_message(filters.command("help", prefixes=".") & filters.me)
async def help_cmd(_, message):
    help_text = (
        "📜 **MENU BANTUAN MORI-UBOT** 📜\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✅ `.alive` - Cek status bot\n"
        "🏘️ `.gcast` - Broadcast ke semua grup (Auto-Sync)\n"
        "👤 `.info` - Detail profil (Reply, mention, atau diri sendiri)\n"
        "📣 `.tagall` - Mention semua anggota grup\n"
        "❓ `.help` - Menampilkan menu ini\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *Tips: Gunakan dengan bijak, Abangku!* 🔥"
    )
    await message.edit(help_text)

# --- JALANKAN MESIN ---
if __name__ == "__main__":
    print("🚀 Mori-UBOT menyala... Tanpa drama!")
    app.run()
