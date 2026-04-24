"""
Telegram Bot for URL Shortener
Handles /shorten command via FastAPI webhook
"""
import os
import logging
import aiohttp
from aiogram import Bot, types
from datetime import datetime

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN)


async def send_url_shortened(
    chat_id: int,
    original_url: str,
    short_code: str,
    qr_code_bytes: bytes = None
) -> bool:
    """Send shortened URL and optional QR code to user"""
    try:
        short_url = f"{API_BASE_URL}/{short_code}"
        
        message_text = (
            f"✅ **Link Qisqartirildi!**\n\n"
            f"🔗 {short_url}\n\n"
            f"📊 **Analytics**: `/stats {short_code}`"
        )
        
        await bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
        # Send QR code if available
        if qr_code_bytes:
            await bot.send_photo(
                chat_id=chat_id,
                photo=types.BufferedInputFile(qr_code_bytes, filename="qr.png"),
                caption="📱 QR kod"
            )
        
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False


async def send_error_message(chat_id: int, error_text: str) -> bool:
    """Send error message to user"""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=f"❌ Xatolik: {error_text}",
            parse_mode="Markdown"
        )
        return True
    except Exception as e:
        logger.error(f"Error sending error message: {e}")
        return False


async def send_analytics(chat_id: int, analytics: dict) -> bool:
    """Send analytics to user"""
    try:
        text = (
            f"📊 **Analytics - {analytics['shortcode']}**\n\n"
            f"🔗 Original: {analytics['original_url'][:50]}...\n"
            f"👁️ Clicks: {analytics['total_clicks']}\n"
            f"📅 Created: {analytics['created_at']}\n"
            f"⏰ Last accessed: {analytics['last_accessed'] or 'Never'}\n"
            f"📈 Days active: {analytics['days_active']}"
        )
        
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown"
        )
        return True
    except Exception as e:
        logger.error(f"Error sending analytics: {e}")
        return False


async def notify_user_start(chat_id: int, first_name: str) -> bool:
    """Send start message"""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"👋 **Salom, {first_name}!**\n\n"
                f"Menga uzun link yuboring, men uni qisqartirib beraman. 🚀\n\n"
                f"**Buyruqlar:**\n"
                f"/shorten `<link>` - Link qisqartiring\n"
                f"/stats `<shortcode>` - Analytics ko'ring"
            ),
            parse_mode="Markdown"
        )
        return True
    except Exception as e:
        logger.error(f"Error sending start message: {e}")
        return False
