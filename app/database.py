from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - use the new egm_user
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://egm_user:egm123@localhost:5432/egm_horeca")

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

# Create all tables
def create_tables():
    try:
        # Import models to ensure they are registered
        from app.models import Base
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print("   This is normal if PostgreSQL is not running yet")
        # Don't raise the error, just log it
