# URL Shortener API - Deployment Guide

## 🚀 Project Features

✅ **FastAPI** with async/await support
✅ **PostgreSQL** database (SQLAlchemy ORM)
✅ **Telegram Bot** webhook integration
✅ **QR Code** generation
✅ **Advanced Analytics** (clicks, last accessed, created date)
✅ **Custom Aliases** with validation
✅ **Vercel Serverless** ready
✅ **Environment-based configuration**

---

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL database (Supabase or Vercel Postgres)
- Telegram Bot Token (from @BotFather)
- Vercel account (for deployment)
- Git

---

## 🛠️ Local Development Setup

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd url-shortener-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
DATABASE_URL=postgresql://user:password@localhost/url_shortener
BOT_TOKEN=123456789:ABCdef_GHIjklmnoPQRstuvWXYZ
TELEGRAM_WEBHOOK_SECRET=your-secret-key
API_BASE_URL=http://localhost:8000
```

### 3. Create Database

```bash
python -c "from app.database import init_db; init_db()"
```

### 4. Run Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

---

## 🌐 Deployment to Vercel

### 1. Set Environment Variables

In Vercel dashboard, add these environment variables:

```
DATABASE_URL=postgresql://...
BOT_TOKEN=123456789:ABCdef...
TELEGRAM_WEBHOOK_SECRET=your-secret
API_BASE_URL=https://your-project.vercel.app
```

### 2. Configure Telegram Webhook

Once deployed, set the webhook in Telegram:

```bash
curl -X POST https://api.telegram.org/bot<BOT_TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-project.vercel.app/webhook",
    "secret_token": "your-secret-key"
  }'
```

### 3. Verify Webhook

```bash
curl -X GET https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo
```

### 4. Deploy

```bash
vercel deploy
```

---

## 📡 API Endpoints

### Create Shortened URL
```bash
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com/very/long/url",
  "custom_alias": "mylink"  # optional
}

Response:
{
  "shortcode": "abc123",
  "custom_alias": "mylink",
  "short_url": "https://your-api.com/abc123",
  "qr_code_url": "https://your-api.com/qr/abc123"
}
```

### Redirect to Original
```bash
GET /{shortcode}
# Redirects to original URL and increments click counter
```

### Get URL Info
```bash
GET /info/{shortcode}

Response:
{
  "shortcode": "abc123",
  "original_url": "https://example.com/very/long/url",
  "custom_alias": "mylink",
  "clicks": 42,
  "last_accessed": "2024-01-15T10:30:00",
  "created_at": "2024-01-10T15:45:00"
}
```

### Get Analytics (Detailed)
```bash
GET /stats/{shortcode}

Response:
{
  "shortcode": "abc123",
  "custom_alias": "mylink",
  "original_url": "https://...",
  "total_clicks": 42,
  "last_accessed": "2024-01-15T10:30:00",
  "created_at": "2024-01-10T15:45:00",
  "days_active": 5
}
```

### Get QR Code
```bash
GET /qr/{shortcode}
# Returns PNG image
```

---

## 🤖 Telegram Bot Commands

Send these commands to your bot:

- **/start** - Show welcome message
- **Send a URL** - Automatically shortens it with QR code
- **/stats {shortcode}** - View analytics

---

## 🗄️ Database Schema

### urls table

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY,
    shortcode VARCHAR(50) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    custom_alias VARCHAR(50) UNIQUE,
    clicks INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100)
);
```

---

## 🔧 Configuration

### Database: PostgreSQL

- **Supabase**: https://supabase.com (Free tier: 500MB)
- **Vercel Postgres**: https://vercel.com/storage/postgres
- **Neon**: https://neon.tech (Free tier available)

Connection string format:
```
postgresql://user:password@host:5432/database_name
```

### Telegram Bot

1. Create bot: https://t.me/BotFather
2. Get BOT_TOKEN from BotFather
3. Generate TELEGRAM_WEBHOOK_SECRET (any random string)

---

## 📦 Project Structure

```
url-shortener-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + webhook handler
│   ├── bot.py               # Telegram bot utilities
│   ├── database.py          # SQLAlchemy models
│   └── utils.py             # QR code, validation, helpers
├── api/
│   └── index.py             # Vercel serverless entry point
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

---

## 🐛 Troubleshooting

### 1. Webhook not receiving messages

```bash
# Check webhook status
curl -X GET https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo
```

Expected response:
```json
{
  "ok": true,
  "result": {
    "url": "https://your-domain.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "ip_address": "..."
  }
}
```

### 2. Database connection error

- Verify DATABASE_URL format
- Check PostgreSQL is running
- Test connection: `psql <DATABASE_URL>`

### 3. QR Code not generating

- Ensure `segno` is installed: `pip install segno`
- Check file permissions in /tmp

---

## 📊 Performance Tips

1. **Connection Pooling**: SQLAlchemy handles this automatically
2. **Caching**: Use Redis for frequently accessed URLs (future enhancement)
3. **Cleanup**: Implement a scheduled task to delete old URLs

---

## 🔒 Security Considerations

1. ✅ Environment variables for secrets (no hardcoding)
2. ✅ URL validation to prevent malicious links
3. ✅ Webhook secret token verification
4. ✅ CORS properly configured
5. 🔄 TODO: Rate limiting per IP/user
6. 🔄 TODO: Input sanitization for custom aliases

---

## 📝 License

MIT

---

## 🤝 Support

For issues or questions, please create a GitHub issue.

---

**Last Updated**: 2024-01-20
