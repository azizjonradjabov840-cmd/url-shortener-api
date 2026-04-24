#!/bin/bash
# Deploy to Vercel
# Prerequisites: Vercel CLI installed (npm install -g vercel)

set -e

echo "🚀 Deploying to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install with: npm install -g vercel"
    exit 1
fi

# Verify .env has required variables
if ! grep -q "DATABASE_URL" .env; then
    echo "❌ DATABASE_URL not set in .env"
    exit 1
fi

if ! grep -q "BOT_TOKEN" .env; then
    echo "❌ BOT_TOKEN not set in .env"
    exit 1
fi

echo "✅ Environment variables verified"

# Deploy to Vercel
echo "📤 Deploying to Vercel..."
vercel deploy --prod

# Get deployment URL
VERCEL_URL=$(vercel list --json | jq -r '.[0].url')
echo "✅ Deployment successful!"
echo "🌐 URL: https://$VERCEL_URL"
echo ""
echo "📋 Next: Configure Telegram webhook"
echo "Run: bash scripts/set-webhook.sh"
