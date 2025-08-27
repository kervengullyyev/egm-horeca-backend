
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import app.api as api
import app.database as database
import app.routers.stripe as stripe_router
import app.routers.messages as messages_router

app = FastAPI(
    title="EGM Horeca API",
    description="Backend API for EGM Horeca e-commerce platform",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Admin
        "http://127.0.0.1:3001",
        "https://admin.egmhoreca.ro",
        "https://egmhoreca.ro",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving uploaded images
app.mount("/api/v1/images", StaticFiles(directory="uploads/images"), name="images")

# Include API router
app.include_router(api.router, prefix="/api/v1")

# Include Stripe router
app.include_router(stripe_router.router, prefix="/api/v1")

# Include Messages router
app.include_router(messages_router.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        database.create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        print("   The API will still work, but database operations may fail")
        print("   Make sure PostgreSQL is running and accessible")

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
            "dashboard": "/api/v1/dashboard/stats"
        },
        "status": "running",
        "note": "Check /docs for full API documentation"
    }

@app.get("/health")
def health():
    return {"status": "ok", "message": "EGM Horeca API is running"}
