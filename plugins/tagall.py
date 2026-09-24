import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType

@Client.on_message(filters.command("tagall", prefixes=".") & filters.me)  # type: ignore
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
