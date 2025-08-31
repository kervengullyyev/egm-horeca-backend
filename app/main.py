
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import app.api as api
import app.routers.stripe as stripe_router
import app.routers.messages as messages_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="EGM Horeca API",
    description="Backend API for EGM Horeca e-commerce platform",
    version="1.0.0"
)

# CORS middleware configuration - use environment variables
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://egmhoreca.ro")
ADMIN_URL = os.getenv("ADMIN_URL", "https://admin.egmhoreca.ro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,  # Frontend
        ADMIN_URL,      # Admin
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Local admin development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories if they don't exist
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/files", exist_ok=True)

# Mount static files for serving uploaded images
app.mount("/api/v1/images", StaticFiles(directory="uploads/images"), name="images")

# Mount static files for serving uploaded files
app.mount("/api/v1/files", StaticFiles(directory="uploads/files"), name="files")

# Include API router
app.include_router(api.router, prefix="/api/v1")

# Include Stripe router
app.include_router(stripe_router.router, prefix="/api/v1")

# Include Messages router
app.include_router(messages_router.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        # Check if database is accessible
        from app.database import get_engine
        from sqlalchemy import text
        
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        print("✅ Database connection successful")
        print("💡 Note: Database tables are managed by Alembic migrations")
        print("   Use 'python manage_db.py init' to initialize the database")
        print("   Use 'python manage_db.py migrate' to run pending migrations")
    except Exception as e:
        print(f"⚠️  Database connection warning: {e}")
        print("   The API will still work, but database operations may fail")
        print("   Make sure PostgreSQL is running and accessible")
        print("   Use 'python manage_db.py init' to initialize the database")

@app.get("/")
def root():
    return {
        "message": "EGM Horeca API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "categories": "/api/v1/categories",
            "products": "/api/v1/products",
            "users": "/api/v1/users",
            "orders": "/api/v1/orders",
            "favorites": "/api/v1/favorites",
            "messages": "/api/v1/messages",
            "dashboard": "/api/v1/dashboard/stats",
            "upload_file": "/api/v1/upload-file",
            "upload_image": "/api/v1/upload-image"
        },
        "status": "running",
        "note": "Check /docs for full API documentation"
    }

@app.get("/health")
def health():
    return {"status": "ok", "message": "EGM Horeca API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
