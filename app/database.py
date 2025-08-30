from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - must be set in environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

# Create engine function - only create when needed
def get_engine():
    return create_engine(DATABASE_URL, echo=False)  # echo=False for production

# Create SessionLocal class
def get_session_local():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Note: Database tables are now managed by Alembic migrations
# Use 'python manage_db.py init' to initialize the database
# Use 'python manage_db.py migrate' to run pending migrations
