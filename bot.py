import asyncio
import logging
import aiohttp
import os # Environment variable'lardan tokenni o'qish uchun
from aiohttp.resolver import AsyncResolver # DNS Resolver uchun
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties # Yangi qo'shilgan qism


# Bizning FastAPI serverimiz (main.py ishlab turishi kerak)
API_URL = 'https://url-shortener-api.onrender.com/shorten'

# Loglarni yoqish
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- YANGI QO'SHILADIGAN QISMLAR ---

# 1. DNS serverlarni sozlash (Google DNS orqali manzilni aniqlaymiz)
session = aiohttp.ClientSession(
    connector=aiohttp.TCPConnector(resolver=AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"]))
)

# Botni sozlash (TUZATILGAN QISM)
bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML), 
    session=session # Bu qism botni internetga to'g'ri ulash uchun muhim!
)
dp = Dispatcher()

# ---------------- FUNKSIYALAR ----------------

async def shorten_url(long_url: str) -> str:
    """APIga so'rov yuborib, linkni qisqartiradi"""
    payload = {'url': long_url, 'custom_code': None}
    
    try:
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

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"👋 **Salom, {message.from_user.full_name}!**\n\n"
        "Menga uzun link yuboring, men uni qisqartirib beraman. 🚀",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message()
async def handle_url(message: Message):
    user_input = message.text.strip()

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
            f"🔗 <a href='{short_url}'>{short_url}</a>",
            disable_web_page_preview=True
        )
    else:
        await msg.edit_text("❌ Xatolik yuz berdi. `main.py` serveri yonilganmi?")

# ---------------- ISHGA TUSHIRISH ----------------
async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")