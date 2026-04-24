# 📊 Project Architecture & File Guide

## Project Structure Overview

```
url-shortener-api/                    # Root project directory
│
├── 🎯 ENTRY POINTS
│   ├── api/index.py                  ← Vercel serverless entry point
│   └── app/main.py                   ← FastAPI application (for local/Docker)
│
├── 💼 APPLICATION CODE (app/ package)
│   ├── app/__init__.py               
│   ├── app/main.py                   # FastAPI + Webhook handler (390 lines)
│   ├── app/database.py               # SQLAlchemy models + PostgreSQL (65 lines)
│   ├── app/bot.py                    # Telegram bot utilities (130 lines)
│   └── app/utils.py                  # Helpers: QR code, validation (135 lines)
│
├── ⚙️ CONFIGURATION
│   ├── vercel.json                   # Vercel deployment config
│   ├── Dockerfile                    # Production Docker image
│   ├── docker-compose.yml            # Local dev environment with PostgreSQL
│   ├── pyproject.toml                # Python project metadata
│   ├── requirements.txt              # Python dependencies (11 packages)
│   ├── Procfile                      # Render/Heroku deployment
│   └── .env.example                  # Environment variables template
│
├── 📚 DOCUMENTATION
│   ├── START-HERE.md                 ⭐ Executive summary (READ FIRST)
│   ├── README.md                     📖 Complete documentation
│   ├── QUICK-START.md                ⚡ Quick reference (5-minute setup)
│   ├── VERCEL-DEPLOYMENT.md          🚀 Deployment guide (step-by-step)
│   ├── MIGRATION.md                  🔄 Old vs new comparison
│   └── COMPLETION-CHECKLIST.md       ✅ Feature checklist
│
├── 🛠️ UTILITY SCRIPTS
│   ├── setup.sh                      # Development environment setup
│   ├── deploy.sh                     # Vercel deployment
│   ├── set-webhook.sh                # Telegram webhook configuration
│   ├── init_db.py                    # Database initialization
│   └── test_api.py                   # Comprehensive API test suite
│
├── ❌ LEGACY (Deprecated - kept for reference)
│   ├── main.py                       # Old FastAPI with SQLite
│   └── bot.py                        # Old polling bot
│
└── 📝 GIT FILES
    └── .gitignore                    # Git ignore rules
```

---

## 🔄 Data Flow Architecture

```
Telegram User
    ↓ (sends URL via Telegram)
    ↓
Telegram API
    ↓ (webhook POST)
    ↓
Vercel Edge
    ↓ (routes to API)
    ↓
FastAPI (/webhook endpoint)
    ↓ (processes message)
    ↓
PostgreSQL Database
    ↓ (stores shortened URL)
    ↓
Segno (QR generation)
    ↓ (generates QR code)
    ↓
Aiogram Bot
    ↓ (sends response)
    ↓
Telegram User ← (receives short URL + QR code)
```

---

## 📡 API Request Flow

```
Client Request (POST /shorten)
    ↓
FastAPI Middleware (CORS, logging)
    ↓
Request Validation (Pydantic)
    ↓
Database Session (Dependency Injection)
    ↓
Shortcode Generation/Validation
    ↓
URL Record Creation
    ↓
QR Code Generation
    ↓
Response (JSON with short_url + qr_code_url)
    ↓
Client ← Response
```

---

## 🗄️ Database Entity Relationship

```
┌─────────────────────────────────────┐
│          urls (Table)                │
├─────────────────────────────────────┤
│ id (PK)                  INTEGER    │
│ shortcode (UNIQUE)       VARCHAR    │
│ original_url             TEXT       │
│ custom_alias (UNIQUE)    VARCHAR    │
│ clicks                   INTEGER    │
│ last_accessed            TIMESTAMP  │
│ created_at               TIMESTAMP  │
│ user_id                  VARCHAR    │
└─────────────────────────────────────┘

Indexes:
- Primary Key: id
- Unique: shortcode, custom_alias
- Future: user_id (for user tracking)
```

---

## 📦 Dependency Graph

```
FastAPI (web framework)
├── Starlette (ASGI framework)
├── Pydantic (data validation)
└── Uvicorn (ASGI server)

SQLAlchemy (ORM)
├── psycopg2-binary (PostgreSQL driver)
└── [PostgreSQL database]

Aiogram (Telegram bot)
├── aiohttp (async HTTP client)
└── [Telegram Bot API]

Segno (QR code generation)
└── [QR image output]

Other:
├── python-dotenv (environment variables)
├── requests (HTTP library)
├── pydantic-settings (configuration management)
└── uvicorn (ASGI server)
```

---

## 🚀 Deployment Paths

### Path 1: Local Development
```
1. clone repo
2. bash setup.sh              ← Creates venv, installs deps
3. Copy .env.example → .env   ← Configure credentials
4. python init_db.py          ← Initialize database
5. uvicorn app.main:app       ← Run locally
6. http://localhost:8000/docs ← API documentation
```

### Path 2: Docker (Local)
```
1. docker-compose up
2. API available at http://localhost:8000
3. PostgreSQL at localhost:5432
4. Includes health checks
```

### Path 3: Vercel (Production)
```
1. Push to GitHub
2. vercel deploy --prod
3. Set environment variables in Vercel dashboard
4. bash set-webhook.sh        ← Configure Telegram webhook
5. API available at https://your-project.vercel.app
```

### Path 4: Render.com (Alternative)
```
1. Push to GitHub
2. Connect repo to Render.com
3. Set environment variables
4. Deploy via Procfile
5. Configure PostgreSQL connection
```

---

## 📊 API Endpoint Map

### Core Operations
```
POST /shorten
├── Input: { url: string, custom_alias?: string }
├── Process: Generate shortcode or use custom alias
├── Store: Create URL record in PostgreSQL
├── Generate: Create QR code image
└── Output: { shortcode, short_url, qr_code_url }

GET /{shortcode}
├── Lookup: Find URL in database
├── Redirect: Send HTTP 307 redirect
└── Track: Increment clicks, update last_accessed
```

### Information Endpoints
```
GET /info/{shortcode}
├── Lookup: Fetch URL record
└── Output: { shortcode, url, clicks, created_at }

GET /stats/{shortcode}
├── Lookup: Fetch URL record
├── Calculate: Days active, analytics
└── Output: { clicks, last_accessed, days_active, ... }

GET /qr/{shortcode}
├── Lookup: Find URL record
├── Generate: Create QR code from short_url
└── Output: PNG image file
```

### Bot Integration
```
POST /webhook
├── Verify: Check webhook secret token
├── Parse: Extract Telegram update
├── Handle: Route to appropriate handler
│   ├── /start command
│   ├── URL shortening request
│   └── /stats command
└── Response: Send Telegram message/photo
```

---

## 🔐 Security Layers

```
Incoming Request
    ↓
CORS Middleware (Check origin)
    ↓
Webhook Endpoint (for /webhook)
    ├── Verify X-Telegram-Bot-Api-Secret-Token header
    └── Reject if invalid
    ↓
Request Validation (Pydantic)
    ├── URL format validation
    ├── Custom alias validation
    └── Reject if invalid
    ↓
Database Access
    ├── SQLAlchemy prepared statements (SQL injection prevention)
    └── Connection pooling with SSL/TLS
    ↓
Response
    └── No sensitive data in error messages
```

---

## ⚡ Performance Optimization

```
FastAPI
├── Async/await for concurrent requests
├── Dependency injection
└── Automatic OpenAPI docs

Database
├── Connection pooling (reuse connections)
├── Indexes on shortcode, custom_alias
└── Prepared statements

Caching (Future)
├── Redis for hot URLs
├── ETag support
└── HTTP cache headers

Serverless (Vercel)
├── Minimal cold start (~2-3s)
├── Auto-scaling
└── Edge functions for geography
```

---

## 📈 Metrics & Monitoring

```
Performance Metrics
├── API Response Time: <100ms target
├── Database Query: <50ms target
├── QR Generation: <100ms target
├── Health Check: <10ms target
└── Cold Start: 2-3s acceptable

Error Metrics
├── 4xx Errors: Client errors
├── 5xx Errors: Server errors
├── Database Connection: Pool health
└── Webhook Delivery: Bot message success

Usage Metrics
├── Total URLs: COUNT(*)
├── Total Clicks: SUM(clicks)
├── Active URLs: WHERE created_at > NOW() - 30 days
└── Unique Users: COUNT(DISTINCT user_id)
```

---

## 🔄 State Management

```
URL State Lifecycle
    ↓
Created (created_at set)
    ↓
Accessed (clicks increment, last_accessed update)
    ↓
Inactive (no access for X days)
    ↓
[Optional] Expired (delete via scheduled task)

Session State
    ├── Database Session (per request)
    ├── Telegram Session (stateless, webhook-based)
    └── User Session (via user_id)
```

---

## 🎛️ Configuration Management

```
Environment Variables (.env)
├── DATABASE_URL (PostgreSQL connection)
├── BOT_TOKEN (Telegram Bot API token)
├── TELEGRAM_WEBHOOK_SECRET (webhook security)
└── API_BASE_URL (for QR code generation)

Fallback Values
├── DATABASE_URL → localhost (for local dev)
├── Debug logging → INFO level
└── CORS → allow all origins
```

---

## 📋 File Sizes & Stats

```
Application Code:
├── app/main.py: ~15 KB (390 lines)
├── app/database.py: ~3 KB (65 lines)
├── app/bot.py: ~5 KB (130 lines)
└── app/utils.py: ~5 KB (135 lines)
Total App: ~28 KB

Documentation:
├── README.md: ~20 KB
├── VERCEL-DEPLOYMENT.md: ~30 KB
├── QUICK-START.md: ~10 KB
├── MIGRATION.md: ~15 KB
├── COMPLETION-CHECKLIST.md: ~25 KB
└── START-HERE.md: ~20 KB
Total Docs: ~120 KB

Total Project: ~180 KB (excluding node_modules/venv)
```

---

## ✅ Testing Coverage

```
test_api.py
├── Health check endpoint ✅
├── API info endpoint ✅
├── URL shortening (auto) ✅
├── URL shortening (custom) ✅
├── URL info retrieval ✅
├── Analytics retrieval ✅
└── QR code generation ✅

Manual Testing
├── Docker compose up ✅
├── Environment loading ✅
├── Database connection ✅
└── Telegram webhook simulation ✅
```

---

## 🎯 Success Criteria (All Met ✅)

- ✅ SQLite removed, PostgreSQL implemented
- ✅ Polling removed, Webhook implemented
- ✅ Monolithic → Modular structure
- ✅ QR code generation added
- ✅ Advanced analytics added
- ✅ Custom aliases added
- ✅ Vercel deployment ready
- ✅ Comprehensive documentation
- ✅ All tests passing
- ✅ All syntax verified

---

## 🚀 Ready for Production!

Your URL Shortener is now:
- ✅ Production-grade code
- ✅ Vercel-deployable
- ✅ Feature-complete
- ✅ Well-documented
- ✅ Thoroughly tested
- ✅ Security-hardened

**Next step: Deploy! 🎉**

---

**Architecture Diagram Created**: January 2024
**Project Version**: 2.0.0
**Status**: ✅ Production Ready
