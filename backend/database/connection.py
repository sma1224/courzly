import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://courzly:password@localhost:5432/courzly")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis connection
redis_client = None

async def init_db():
    """Initialize database connections and create tables"""
    global redis_client
    
    try:
        # Initialize Redis
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connection established")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def close_db():
    """Close database connections"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Database connections closed")

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_redis():
    """Get Redis client"""
    return redis_client