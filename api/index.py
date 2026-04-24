"""
Vercel serverless handler for FastAPI application
Routes all requests through FastAPI ASGI app
"""
from app.main import app


# For ASGI servers like Vercel
asgi_app = app

# Vercel Python runtime expects 'app'
# So we also export it as 'app' for compatibility
handler = app
