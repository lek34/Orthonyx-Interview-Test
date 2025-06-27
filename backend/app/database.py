from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, text
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create async database URL without database name for initial connection
BASE_DATABASE_URL = f"mysql+asyncmy://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}"

# Create async database URL with database name
DATABASE_URL = f"{BASE_DATABASE_URL}/{settings.DB_NAME}"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Create engine without database name
        temp_engine = create_async_engine(
            BASE_DATABASE_URL,
            echo=False
        )
        
        async with temp_engine.begin() as conn:
            # Create database if it doesn't exist
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}"))
            logger.info(f"Database '{settings.DB_NAME}' is ready")
        
        await temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise

async def init_db():
    """Initialize database - create database and tables if they don't exist"""
    try:
        # First, ensure database exists
        await create_database_if_not_exists()
        
        # Then create all tables
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed") 