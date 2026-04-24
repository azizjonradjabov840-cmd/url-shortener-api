"""
FastAPI URL Shortener with Telegram Bot Webhook Integration
PostgreSQL + Vercel Ready
"""
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, AnyHttpUrl, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import init_db, get_db, URL, engine, Base
from app.utils import (
    generate_shortcode,
    is_valid_url,
    is_valid_custom_alias,
    generate_qr_code,
    format_analytics,
    sanitize_url,
)
from app.bot import (
    send_url_shortened,
    send_error_message,
    send_analytics,
    notify_user_start,
    bot
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Environment variables
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "secret-key")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
BOT_TOKEN = os.environ.get("BOT_TOKEN")


# Pydantic Models
class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    custom_alias: Optional[str] = Field(None, min_length=4, max_length=32)


class ShortenResponse(BaseModel):
    shortcode: str
    custom_alias: Optional[str]
    short_url: str
    qr_code_url: Optional[str]


class UrlInfoResponse(BaseModel):
    shortcode: str
    original_url: str
    custom_alias: Optional[str]
    clicks: int
    last_accessed: Optional[str]
    created_at: str


class AnalyticsResponse(BaseModel):
    shortcode: str
    custom_alias: Optional[str]
    original_url: str
    total_clicks: int
    last_accessed: Optional[str]
    created_at: str
    days_active: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting URL Shortener API...")
    
    # Ensure tables exist on startup in the deployed environment
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created or verified successfully")
    except Exception as e:
        logger.warning(f"⚠️ Table creation warning: {e}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"⚠️ Database initialization warning: {e}")
        # Continue even if DB init fails (tables might already exist)
    
    # Set webhook for Telegram bot
    if BOT_TOKEN:
        try:
            webhook_url = f"{API_BASE_URL}/webhook"
            await bot.set_webhook(url=webhook_url, secret_token=TELEGRAM_WEBHOOK_SECRET)
            logger.info(f"✅ Webhook set to {webhook_url}")
        except Exception as e:
            logger.warning(f"⚠️ Webhook setup warning: {e}")
            # Continue anyway - webhook might already be set
    
    yield
    
    logger.info("Shutting down...")
    if BOT_TOKEN:
        try:
            await bot.session.close()
        except Exception as e:
            logger.debug(f"Session close: {e}")


app = FastAPI(
    title="URL Shortener API",
    description="FastAPI URL Shortener with Telegram Bot Integration",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility functions
def get_host(request: Request) -> str:
    """Extract base URL from request"""
    return str(request.base_url).rstrip("/")


async def get_or_create_shortcode(
    custom_alias: Optional[str] = None,
    db: Session = None
) -> str:
    """Generate unique shortcode or use custom alias"""
    if custom_alias:
        if not is_valid_custom_alias(custom_alias):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid custom alias. Use 4-32 alphanumeric characters, hyphens, or underscores."
            )
        
        existing = db.query(URL).filter(
            (URL.shortcode == custom_alias) | (URL.custom_alias == custom_alias)
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom alias already in use."
            )
        return custom_alias
    
    # Generate unique shortcode
    for _ in range(10):
        code = generate_shortcode()
        existing = db.query(URL).filter(URL.shortcode == code).first()
        if not existing:
            return code
    
    raise HTTPException(
        status_code=500,
        detail="Failed to generate unique shortcode."
    )


# Routes

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/shorten", response_model=ShortenResponse, tags=["URL Management"])
async def shorten_url(
    req: ShortenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Shorten a URL with optional custom alias
    
    - **url**: The long URL to shorten
    - **custom_alias**: Optional custom short code (4-32 chars)
    """
    url = sanitize_url(str(req.url))
    
    if not is_valid_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format."
        )
    
    try:
        shortcode = await get_or_create_shortcode(req.custom_alias, db)
    except HTTPException:
        raise
    
    # Create database entry
    try:
        host = get_host(request)
        url_record = URL(
            shortcode=shortcode,
            original_url=url,
            custom_alias=req.custom_alias
        )
        db.add(url_record)
        db.commit()
        db.refresh(url_record)
        
        short_url = f"{host}/{shortcode}"
        qr_bytes = generate_qr_code(short_url)
        qr_url = f"{host}/qr/{shortcode}" if qr_bytes else None
        
        return ShortenResponse(
            shortcode=shortcode,
            custom_alias=req.custom_alias,
            short_url=short_url,
            qr_code_url=qr_url
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shortcode already exists."
        )


@app.get("/{shortcode}", tags=["Redirection"])
async def redirect(shortcode: str, db: Session = Depends(get_db)):
    """
    Redirect to original URL and increment click counter
    """
    url_record = db.query(URL).filter(
        (URL.shortcode == shortcode) | (URL.custom_alias == shortcode)
    ).first()
    
    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortcode not found."
        )
    
    # Update analytics
    url_record.clicks += 1
    url_record.last_accessed = datetime.utcnow()
    db.commit()
    
    return RedirectResponse(url=url_record.original_url, status_code=307)


@app.get("/info/{shortcode}", response_model=UrlInfoResponse, tags=["Analytics"])
async def get_info(shortcode: str, db: Session = Depends(get_db)):
    """
    Get URL information and click statistics
    """
    url_record = db.query(URL).filter(
        (URL.shortcode == shortcode) | (URL.custom_alias == shortcode)
    ).first()
    
    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortcode not found."
        )
    
    return UrlInfoResponse(
        shortcode=url_record.shortcode,
        original_url=url_record.original_url,
        custom_alias=url_record.custom_alias,
        clicks=url_record.clicks,
        last_accessed=url_record.last_accessed.isoformat() if url_record.last_accessed else None,
        created_at=url_record.created_at.isoformat()
    )


@app.get("/stats/{shortcode}", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_stats(shortcode: str, db: Session = Depends(get_db)):
    """
    Get detailed analytics for shortened URL
    """
    url_record = db.query(URL).filter(
        (URL.shortcode == shortcode) | (URL.custom_alias == shortcode)
    ).first()
    
    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortcode not found."
        )
    
    return AnalyticsResponse(**format_analytics(url_record))


@app.get("/qr/{shortcode}", tags=["QR Code"])
async def get_qr_code(shortcode: str, db: Session = Depends(get_db)):
    """
    Get QR code image for shortened URL
    """
    url_record = db.query(URL).filter(
        (URL.shortcode == shortcode) | (URL.custom_alias == shortcode)
    ).first()
    
    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortcode not found."
        )
    
    short_url = f"{os.environ.get('API_BASE_URL', 'http://localhost:8000')}/{shortcode}"
    qr_bytes = generate_qr_code(short_url)
    
    if not qr_bytes:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate QR code."
        )
    
    from io import BytesIO
    return FileResponse(
        BytesIO(qr_bytes),
        media_type="image/png",
        filename=f"qr_{shortcode}.png"
    )


@app.post("/webhook", tags=["Telegram"])
async def telegram_webhook(request: Request):
    """
    Telegram bot webhook endpoint
    Receives updates from Telegram Bot API
    """
    try:
        update_data = await request.json()
        
        # Verify webhook secret
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret != TELEGRAM_WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Handle bot update
        update = types.Update(**update_data)
        
        if update.message:
            message = update.message
            chat_id = message.chat.id
            
            # /start command
            if message.text and message.text.startswith("/start"):
                await notify_user_start(chat_id, message.from_user.first_name)
            
            # /stats command
            elif message.text and message.text.startswith("/stats"):
                parts = message.text.split()
                if len(parts) > 1:
                    shortcode = parts[1]
                    db = next(get_db())
                    url_record = db.query(URL).filter(
                        (URL.shortcode == shortcode) | (URL.custom_alias == shortcode)
                    ).first()
                    db.close()
                    
                    if url_record:
                        await send_analytics(chat_id, format_analytics(url_record))
                    else:
                        await send_error_message(chat_id, "Shortcode not found")
                else:
                    await send_error_message(chat_id, "Usage: /stats <shortcode>")
            
            # URL shortening
            elif message.text and is_valid_url(sanitize_url(message.text)):
                url = sanitize_url(message.text)
                
                try:
                    db = next(get_db())
                    shortcode = await get_or_create_shortcode(None, db)
                    
                    url_record = URL(
                        shortcode=shortcode,
                        original_url=url,
                        user_id=str(chat_id)
                    )
                    db.add(url_record)
                    db.commit()
                    
                    short_url = f"{API_BASE_URL}/{shortcode}"
                    qr_bytes = generate_qr_code(short_url)
                    
                    await send_url_shortened(chat_id, url, shortcode, qr_bytes)
                    db.close()
                except Exception as e:
                    logger.error(f"Error shortening URL: {e}")
                    await send_error_message(chat_id, str(e))
            
            else:
                await send_error_message(chat_id, "Please send a valid URL or use /stats <shortcode>")
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/", tags=["Info"])
async def root():
    """API information"""
    return {
        "name": "URL Shortener API",
        "version": "2.0.0",
        "features": [
            "URL shortening with custom aliases",
            "QR code generation",
            "Advanced analytics",
            "Telegram bot integration",
            "PostgreSQL backend"
        ],
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
