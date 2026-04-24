"""
Vercel serverless handler for FastAPI application
Routes all requests through FastAPI ASGI app
"""
from app.main import app


# Vercel serverless function
async def handler(request):
    """Handle HTTP requests via Vercel serverless"""
    return app(request)
