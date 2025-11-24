from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi import BackgroundTasks
from pydantic import BaseModel, AnyHttpUrl
from typing import Optional
import string
import random
import sqlite3
from contextlib import asynccontextmanager

DATABASE = "url_shortener.db"
SHORTCODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits

# Database utilities
def get_db_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    # Enable WAL mode for concurrency
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shortcode TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def generate_shortcode(length=SHORTCODE_LENGTH):
    return ''.join(random.choices(ALPHABET, k=length))

def shortcode_exists(code):
    conn = get_db_connection()
    cur = conn.execute("SELECT 1 FROM urls WHERE shortcode = ?", (code,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def create_unique_shortcode():
    for _ in range(10):
        code = generate_shortcode()
        if not shortcode_exists(code):
            return code
    raise HTTPException(status_code=500, detail="Failed to generate unique shortcode.")

# Pydantic Models
class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    custom_code: Optional[str] = None

class ShortenResponse(BaseModel):
    shortcode: str
    short_url: str

class UrlInfoResponse(BaseModel):
    shortcode: str
    url: AnyHttpUrl
    clicks: int
    created_at: str

# App lifespan and FastAPI Instance
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB at startup
    init_db()
    yield
    # Clean up resources here if needed

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, limit allowed origins!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get host for composing short URLs
def get_host(request: Request):
    return str(request.base_url)

# Routes

@app.post('/shorten', response_model=ShortenResponse)
async def shorten_url(
    req: ShortenRequest,
    host: str = Depends(get_host),
):
    code = req.custom_code
    if code:
        # Validate code: only allow alphanumeric, 4-16 characters, no reserved words
        if not (4 <= len(code) <= 16 and all(c in ALPHABET for c in code)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Custom code must be 4-16 alphanumeric characters."
            )
        if shortcode_exists(code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Shortcode already exists."
            )
    else:
        code = await run_in_threadpool(create_unique_shortcode)
    # Insert into DB
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO urls (shortcode, url) VALUES (?, ?)",
            (code, str(req.url))
        )
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shortcode already exists."
        )
    return ShortenResponse(shortcode=code, short_url=f"{host}{code}")

@app.get("/{shortcode}", status_code=307)
async def redirect(shortcode: str, request: Request, background_tasks: BackgroundTasks):
    conn = get_db_connection()
    cur = conn.execute("SELECT url FROM urls WHERE shortcode = ?", (shortcode,))
    result = cur.fetchone()
    conn.close()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortcode not found.")
    url = result[0]
    # Increment click count in the background
    def increment_click(code):
        conn = get_db_connection()
        conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE shortcode = ?", (code,))
        conn.commit()
        conn.close()
    background_tasks.add_task(increment_click, shortcode)
    return RedirectResponse(url, status_code=307)

@app.get("/info/{shortcode}", response_model=UrlInfoResponse)
async def info(shortcode: str):
    conn = get_db_connection()
    cur = conn.execute(
        "SELECT shortcode, url, clicks, created_at FROM urls WHERE shortcode = ?",
        (shortcode,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortcode not found.")
    return UrlInfoResponse(
        shortcode=row[0],
        url=row[1],
        clicks=row[2],
        created_at=row[3]
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)