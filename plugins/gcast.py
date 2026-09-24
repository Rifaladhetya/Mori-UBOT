import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

@Client.on_message(filters.command("gcast", prefixes=".") & filters.me)  # type: ignore
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
                if is_reply and content_msg:
                    await content_msg.copy(chat_id)
                elif content_text:
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
