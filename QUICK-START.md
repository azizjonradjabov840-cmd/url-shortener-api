# URL Shortener API - Quick Reference

## 🚀 Quick Start (5 minutes)

### 1. Setup
```bash
bash setup.sh
python init_db.py
```

### 2. Environment
```bash
# Edit .env with your PostgreSQL credentials
export DATABASE_URL="postgresql://user:pass@host/db"
export BOT_TOKEN="your_telegram_token"
```

### 3. Run
```bash
uvicorn app.main:app --reload
```

### 4. Test
Open http://localhost:8000/docs

---

## 📡 API Endpoints Quick Reference

### Create Short URL
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/very/long/url",
    "custom_alias": "mylink"
  }'
```

**Response:**
```json
{
  "shortcode": "abc123",
  "custom_alias": "mylink",
  "short_url": "http://localhost:8000/abc123",
  "qr_code_url": "http://localhost:8000/qr/abc123"
}
```

### Redirect
```bash
curl -L http://localhost:8000/abc123
# Redirects to original URL
```

### Get Info
```bash
curl http://localhost:8000/info/abc123
```

### Get Analytics
```bash
curl http://localhost:8000/stats/abc123
```

### Get QR Code
```bash
curl http://localhost:8000/qr/abc123 > qr.png
```

---

## 🤖 Telegram Bot Commands

- Send a URL → Bot shortens it
- `/stats <shortcode>` → View analytics
- `/start` → Welcome message

---

## 🗄️ Database

### PostgreSQL Connection
```bash
psql postgresql://user:pass@host/database
```

### Tables
```sql
SELECT * FROM urls;
```

---

## 🌐 Deployment

### Local Docker
```bash
docker-compose up
```

### Vercel
```bash
npm install -g vercel
vercel deploy --prod
bash set-webhook.sh TOKEN URL SECRET
```

### Render/Heroku
```bash
git push heroku main
```

---

## 🔧 Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `DATABASE_URL` | ✅ | `postgresql://...` |
| `BOT_TOKEN` | ✅ | `123456789:ABC...` |
| `TELEGRAM_WEBHOOK_SECRET` | ✅ | `secret-key` |
| `API_BASE_URL` | ✅ | `https://api.example.com` |

---

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### API Docs
```
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

## 🐛 Troubleshooting

### Database connection fails
- Check `DATABASE_URL` format
- Verify PostgreSQL is running
- Test: `psql $DATABASE_URL`

### Webhook not working
```bash
# Check webhook status
curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo
```

### QR code not generating
```bash
python -c "import segno; print(segno.__file__)"
```

---

## 📈 Analytics Example

```json
{
  "shortcode": "abc123",
  "custom_alias": "mylink",
  "original_url": "https://example.com/very/long/url",
  "total_clicks": 42,
  "last_accessed": "2024-01-15T10:30:00",
  "created_at": "2024-01-10T15:45:00",
  "days_active": 5
}
```

---

**Need help?** Check README.md for full documentation.
