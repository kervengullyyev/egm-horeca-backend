
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import app.api as api
import app.routers.auth as auth_router
import app.routers.stripe as stripe_router
import app.routers.messages as messages_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Only add HSTS in production
    if os.getenv("NODE_ENV") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

app = FastAPI(
    title="EGM Horeca API",
    description="Backend API for EGM Horeca e-commerce platform",
    version="1.0.0"
)

# Add security middleware
app.middleware("http")(security_headers_middleware)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure this properly in production
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

# Include Auth router
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])

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
