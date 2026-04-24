#!/bin/bash
# Set Telegram Webhook
# Usage: bash set-webhook.sh <BOT_TOKEN> <WEBHOOK_URL> <SECRET>

BOT_TOKEN=${1:-$BOT_TOKEN}
WEBHOOK_URL=${2:-https://your-domain.com/webhook}
SECRET=${3:-your-secret-key}

if [ -z "$BOT_TOKEN" ]; then
    echo "Usage: $0 <BOT_TOKEN> <WEBHOOK_URL> [SECRET]"
    echo "Example: $0 123456789:ABCdef https://your-api.vercel.app/webhook mysecret"
    exit 1
fi

echo "Setting Telegram webhook..."
echo "URL: $WEBHOOK_URL"
echo "Secret: $SECRET"

curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/setWebhook \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"$WEBHOOK_URL\",
    \"secret_token\": \"$SECRET\"
  }"

echo ""
echo ""
echo "Verifying webhook..."
curl -X GET https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo | jq .
