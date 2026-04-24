#!/usr/bin/env python
"""
Database initialization script
Use this to set up tables for the first time
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, SessionLocal, URL

def main():
    print("🔄 Initializing database...")
    
    try:
        init_db()
        print("✅ Database tables created successfully!")
        
        # Test connection
        db = SessionLocal()
        result = db.query(URL).first()
        db.close()
        
        print("✅ Database connection verified!")
        print("\n📝 Next steps:")
        print("1. Set up environment variables in .env")
        print("2. Configure Telegram bot webhook")
        print("3. Run: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
