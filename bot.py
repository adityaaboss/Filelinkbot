import os
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
OWNER_ID = int(os.environ.get("OWNER_ID"))
SHORTX_API_KEY = os.environ.get("SHORTX_API_KEY")

bot = Client("cutiepiebot",
             bot_token=BOT_TOKEN,
             api_id=API_ID,
             api_hash=API_HASH)

@bot.on_message(filters.private & filters.document | filters.video | filters.audio)
async def handle_file(client, message: Message):
    sent_msg = await message.reply_text("Saving your file...")
    
    # Forward file to DB channel
    forward = await message.forward(DB_CHANNEL)
    
    # Generate internal link
    file_id = str(forward.id)
    expiry_time = int(time.time()) + 24 * 60 * 60  # 24 hours
    
    # Generate shortx link
    link = f"https://t.me/{bot.me.username}?start=F{file_id}_{expiry_time}"
    short_url = requests.get(f"https://shortxlinks.com/api?api={SHORTX_API_KEY}&url={link}").json().get("shortenedUrl")
    
    await sent_msg.edit_text(f"✅ File saved!\n\n🔗 Your 24-hour link:\n{short_url}")

@bot.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) > 1:
        data = message.command[1]
        if data.startswith("F"):
            try:
                fid, exp = data[1:].split("_")
                if time.time() > int(exp):
                    return await message.reply_text("⚠️ This link has expired.")
                file = await client.get_messages(DB_CHANNEL, int(fid))
                return await file.copy(chat_id=message.chat.id)
            except:
                return await message.reply_text("❌ Invalid or corrupted link.")
    else:
        await message.reply_text("👋 Welcome! Send me a file and I’ll give you a 24-hour access link.")

bot.run()
