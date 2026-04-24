#!/bin/bash
# Setup script for URL Shortener API
# Use: bash setup.sh

set -e

echo "🚀 Setting up URL Shortener API..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your configuration!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env with your credentials:"
echo "   DATABASE_URL=postgresql://..."
echo "   BOT_TOKEN=..."
echo ""
echo "2. Initialize database:"
echo "   python init_db.py"
echo ""
echo "3. Run development server:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Visit API documentation:"
echo "   http://localhost:8000/docs"
