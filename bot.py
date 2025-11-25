import asyncio
import logging
import aiohttp
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ---------------- SOZLAMALAR ----------------
API_TOKEN = os.environ.get("BOT_TOKEN")
# Server manzili (oxirida /shorten bo'lishi shart)
API_URL = 'https://url-shortener-api.onrender.com/shorten'

# Loglarni yoqish
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- FUNKSIYALAR ----------------

async def shorten_url(long_url: str) -> str:
    """APIga so'rov yuborib, linkni qisqartiradi"""
    # main.py kutayotgan format
    payload = {'url': long_url, 'custom_code': None}
    
    try:
        # Oddiy sessiya yaratamiz (DNS muammosi bo'lmasligi uchun)
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('short_url') or data.get('shortUrl')
                else:
                    error_text = await resp.text()
                    logger.error(f"API Error: {resp.status} - {error_text}")
                    return None
    except Exception as e:
        logger.error(f"Ulanishda xatolik: {e}")
        return None

def is_valid_url(url: str) -> bool:
    return "." in url and not " " in url

# ---------------- HANDLERS ----------------

async def cmd_start(message: Message):
    await message.answer(
        f"👋 **Salom, {message.from_user.full_name}!**\n\n"
        "Menga uzun link yuboring, men uni qisqartirib beraman. 🚀",
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_url(message: Message):
    user_input = message.text.strip()

    # Linkda http bo'lmasa qo'shamiz
    if not user_input.startswith(("http://", "https://")):
        user_input = "http://" + user_input

    if not is_valid_url(user_input):
        await message.reply("❌ Iltimos, to'g'ri link yuboring.")
        return

    msg = await message.reply("⏳ **Qisqartirilmoqda...**", parse_mode=ParseMode.MARKDOWN)

    short_url = await shorten_url(user_input)

    if short_url:
        await msg.edit_text(
            f"✅ **Tayyor!**\n\n"
            f"🔗 {short_url}",
            disable_web_page_preview=True
        )
    else:
        await msg.edit_text("❌ Xatolik yuz berdi. Server ishlamayapti.")

# ---------------- ISHGA TUSHIRISH ----------------
async def main():
    # Botni yaratish
    bot = Bot(
        token=API_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Handlerlarni ulash
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(handle_url)

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")