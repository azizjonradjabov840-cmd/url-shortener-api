# Vercel Deployment Guide

## Prerequisites

- [Vercel Account](https://vercel.com) (free)
- [GitHub Account](https://github.com)
- PostgreSQL Database (free options: [Supabase](https://supabase.com), [Render.com](https://render.com), [Neon](https://neon.tech))
- Telegram Bot Token (from @BotFather)

---

## Step 1: Set Up PostgreSQL Database

### Option A: Supabase (Recommended)

1. Go to https://supabase.com
2. Create a new project
3. Note your connection string: `postgresql://user:password@host/database`
4. Keep it safe - you'll need it soon

### Option B: Vercel Postgres

1. In Vercel dashboard → Storage → Create Database → Postgres
2. Copy the connection string
3. Note: Limited free tier, but integrated with Vercel

### Option C: Neon

1. Go to https://neon.tech
2. Create project
3. Copy the connection string from Project Settings

---

## Step 2: Create Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow prompts to create bot
4. **Save your BOT_TOKEN** (looks like: `123456789:ABCdef_GHIjklmnoPQRstuvWXYZ`)
5. Generate webhook secret: `openssl rand -hex 32`

---

## Step 3: Prepare Code for Vercel

The project already includes `vercel.json` and `api/index.py`. Just verify:

✅ `vercel.json` exists
✅ `api/index.py` imports FastAPI app
✅ `requirements.txt` has all dependencies
✅ `app/` folder structure is correct

---

## Step 4: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: URL shortener refactored for Vercel"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/url-shortener-api.git
git push -u origin main
```

---

## Step 5: Deploy to Vercel

### Method A: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com/dashboard)
2. Click "New Project"
3. Select "Import Git Repository"
4. Choose your GitHub repo
5. Click "Import"
6. In "Environment Variables" section, add:

```
DATABASE_URL = postgresql://user:password@host/database
BOT_TOKEN = your_telegram_bot_token_here
TELEGRAM_WEBHOOK_SECRET = your_webhook_secret_here
API_BASE_URL = https://your-project-name.vercel.app
```

7. Click "Deploy"
8. Wait for deployment to complete
9. Note your URL (e.g., `https://url-shortener-abc.vercel.app`)

### Method B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel deploy --prod

# Set environment variables
vercel env add DATABASE_URL
vercel env add BOT_TOKEN
vercel env add TELEGRAM_WEBHOOK_SECRET
vercel env add API_BASE_URL
```

---

## Step 6: Configure Telegram Webhook

Once deployment is successful, register webhook with Telegram:

```bash
#!/bin/bash
BOT_TOKEN="your_bot_token"
WEBHOOK_URL="https://your-project.vercel.app/webhook"
SECRET="your_webhook_secret"

curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/setWebhook \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"$WEBHOOK_URL\",
    \"secret_token\": \"$SECRET\"
  }"
```

### Verify Webhook

```bash
curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo | jq
```

Expected response:
```json
{
  "ok": true,
  "result": {
    "url": "https://your-project.vercel.app/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## Step 7: Initialize Database

The database is initialized automatically on first request. However, if you want to pre-create tables:

Option 1: Via API endpoint (automatic)
```bash
curl https://your-project.vercel.app/health
```

Option 2: Manually connect to PostgreSQL
```bash
psql $DATABASE_URL -c "
CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    shortcode VARCHAR(50) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    custom_alias VARCHAR(50) UNIQUE,
    clicks INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100)
);"
```

---

## Step 8: Test Your Deployment

### Test API
```bash
curl https://your-project.vercel.app/health

# Should return:
# {"status":"ok","timestamp":"2024-01-15T..."}
```

### Test URL Shortening
```bash
curl -X POST https://your-project.vercel.app/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com"
  }'
```

### Test Telegram Bot
- Send your bot any URL
- Bot should respond with shortened URL + QR code

### Test Analytics
```bash
curl https://your-project.vercel.app/stats/abc123
```

---

## Troubleshooting

### "No module named 'app'"

Solution: Ensure `api/index.py` imports from `app`:
```python
from app.main import app
```

### Database connection timeout

- Verify `DATABASE_URL` environment variable
- Check database is accessible from Vercel IPs
- For Supabase: allow all IPs (0.0.0.0/0)

### Webhook not receiving messages

```bash
# Check webhook info
curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo

# Check logs
vercel logs <project-name>
```

### QR Code not generating

- Ensure `segno` library is installed
- Check file permissions in Vercel's `/tmp`

### SSL Certificate error

Usually resolves automatically. If not:
```bash
# Restart bot
vercel redeploy
```

---

## Monitoring & Logs

### View Logs
```bash
vercel logs <project-name> --follow
```

### Monitor Performance
- Vercel Dashboard → Project → Analytics
- Check cold start times
- Monitor function duration

### Health Monitoring
```bash
# Set up monitoring (optional)
curl -X POST https://uptime-monitoring-service.com/monitors \
  -d "url=https://your-project.vercel.app/health"
```

---

## Cost & Limits

| Resource | Vercel Free | Note |
|----------|------------|------|
| Functions | Unlimited | 65 second timeout |
| Bandwidth | 100GB/month | Per month |
| Executions | Unlimited | Within bandwidth limit |
| Database | Not included | Use Supabase/Neon |

**Total Estimated Cost**: $0-10/month (depends on database choice)

---

## Production Checklist

- [ ] Database URL set correctly
- [ ] Bot token stored securely
- [ ] Webhook secret configured
- [ ] API_BASE_URL points to Vercel domain
- [ ] Webhook endpoint verified with Telegram
- [ ] Database tables created
- [ ] Test API health check works
- [ ] Test URL shortening works
- [ ] Test Telegram bot responds
- [ ] Monitor logs for errors
- [ ] Set up error alerts (optional)

---

## Next Steps

1. **Custom Domain** (optional)
   - Vercel → Project Settings → Domains
   - Add your domain (e.g., short.example.com)
   - Update API_BASE_URL

2. **SSL/TLS** (automatic)
   - Vercel provides free SSL certificate

3. **Analytics** (optional)
   - Set up Vercel Analytics
   - Monitor function performance

4. **Backups** (recommended)
   - Enable automatic backups in PostgreSQL provider
   - Export data regularly

---

## Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Aiogram Documentation](https://docs.aiogram.dev/)
- [Supabase Documentation](https://supabase.com/docs)

---

**Deployed successfully?** Star the repo and share! 🌟
