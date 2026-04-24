"""
Database configuration and models for URL Shortener
Using SQLAlchemy with PostgreSQL
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database URL from environment variable
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://user:password@localhost/url_shortener"
)

# Fix for Vercel PostgreSQL URLs (psycopg2 format)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add SSL support for Supabase and cloud PostgreSQL
# Supabase requires SSL connections
if DATABASE_URL and "sslmode" not in DATABASE_URL:
    # Check if it's a remote database (not localhost)
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        # Add SSL mode for cloud databases
        if "?" in DATABASE_URL:
            DATABASE_URL += "&sslmode=require"
        else:
            DATABASE_URL += "?sslmode=require"

# Create engine with pool configuration for serverless
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        connect_args={"connect_timeout": 10} if "postgresql" in DATABASE_URL else {}
    )
except Exception as e:
    print(f"Warning: Database connection issue: {e}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()


class URL(Base):
    """URL Model with analytics"""
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    shortcode = Column(String(50), unique=True, index=True, nullable=False)
    original_url = Column(Text, nullable=False)
    custom_alias = Column(String(50), unique=True, nullable=True)
    clicks = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), nullable=True)  # Telegram user ID


def get_db():
    """Dependency for database session"""
    if not SessionLocal or not engine:
        raise RuntimeError("Database not properly configured. Check DATABASE_URL environment variable.")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        if not engine:
            raise RuntimeError("Database engine not initialized")
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False


async def init_db_async():
    """Async wrapper for database initialization"""
    return init_db()
