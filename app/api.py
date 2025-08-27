from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from PIL import Image
import io
from app import crud, schemas, database
from app.routers import auth, stripe, orders

router = APIRouter()

# Include routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(stripe.router, prefix="/stripe", tags=["Stripe"])
router.include_router(orders.router, prefix="/orders", tags=["Orders"])



# Dependency
def get_db():
    SessionLocal = database.get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check
@router.get("/health")
def health_check():
    return {"status": "ok", "message": "EGM Horeca API is running"}

# Image upload endpoint
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/images/{filename}"
        
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Save image
        image.save(file_path, quality=85, optimize=True)
        
        # Return the image URL
        image_url = f"http://localhost:8000/api/v1/images/{filename}"
        
        return {
            "success": True,
            "filename": filename,
            "url": image_url,
            "size": len(contents),
            "content_type": file.content_type
        }
        
    except Exception as e:
        print(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

# Mock data for when database is not available
MOCK_CATEGORIES = [
    {
        "id": 1,
        "name_en": "Kitchen Equipment",
        "name_ro": "Echipamente Bucătărie",
        "slug": "kitchen-equipment",
        "description_en": "Professional kitchen equipment and appliances",
        "description_ro": "Echipamente și aparate profesionale pentru bucătărie",
                        "image_url": "",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": None
    },
    {
        "id": 2,
        "name_en": "Bar & Beverage",
        "name_ro": "Bar și Băuturi",
        "slug": "bar-beverage",
        "description_en": "Bar equipment and beverage dispensers",
        "description_ro": "Echipamente pentru bar și distribuitoare de băuturi",
                        "image_url": "",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": None
    }
]

MOCK_PRODUCTS = [
    {
        "id": 1,
        "name_en": "Professional Coffee Machine",
        "name_ro": "Mașină de Cafea Profesională",
        "slug": "professional-coffee-machine",
        "description_en": "High-quality professional coffee machine for restaurants and cafes",
        "description_ro": "Mașină de cafea profesională de înaltă calitate pentru restaurante și cafenele",
        "price": 1299.99,
        "category_id": 2,
        "brand": "EGM",
        "sku": "COF-001",
        "stock_quantity": 15,
        "is_active": True,
                        "images": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": None
    },
    {
        "id": 2,
        "name_en": "Commercial Refrigerator",
        "name_ro": "Frigider Comercial",
        "slug": "commercial-refrigerator",
        "description_en": "Large capacity commercial refrigerator for food storage",
        "description_ro": "Frigider comercial cu capacitate mare pentru depozitarea alimentelor",
        "price": 2499.99,
        "category_id": 1,
        "brand": "EGM",
        "sku": "REF-001",
        "stock_quantity": 8,
        "is_active": True,
                        "images": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": None
    }
]

MOCK_DASHBOARD_STATS = {
    "total_revenue": 45231.89,
    "total_products": 6,
    "total_orders": 156,
    "total_customers": 156,
    "pending_orders": 24
}

# Category endpoints
@router.get("/categories", response_model=List[schemas.CategoryResponse])
def read_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all categories"""
    try:
        categories = crud.get_categories(db, skip=skip, limit=limit, active_only=active_only)
        return categories
    except Exception as e:
        print(f"⚠️  Error fetching categories: {e}")
        # Return mock data as fallback
        return MOCK_CATEGORIES[skip:skip+limit]

@router.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID"""
    try:
        if db is None:
            # Return mock data if database is not available
            if category_id <= len(MOCK_CATEGORIES):
                return MOCK_CATEGORIES[category_id - 1]
            raise HTTPException(status_code=404, detail="Category not found")
        
        category = crud.get_category(db, category_id=category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️  Error fetching category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories/slug/{slug}", response_model=schemas.CategoryResponse)
def read_category_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a specific category by slug"""
    try:
        if db is None:
            # Return mock data if database is not available
            for category in MOCK_CATEGORIES:
                if category["slug"] == slug:
                    return category
            raise HTTPException(status_code=404, detail="Category not found")
        
        category = crud.get_category_by_slug(db, slug=slug)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️  Error fetching category by slug: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/categories", response_model=schemas.CategoryResponse)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    return crud.create_category(db=db, category=category)

@router.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category"""
    db_category = crud.update_category(db=db, category_id=category_id, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    db_category = crud.delete_category(db=db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# Product endpoints
@router.get("/products", response_model=List[schemas.ProductResponse])
def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    brand: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all products with optional filtering"""
    try:
        if db is None:
            # Return mock data if database is not available
            products = MOCK_PRODUCTS[skip:skip+limit]
            if category_id:
                products = [p for p in products if p["category_id"] == category_id]
            return products
        
        products = crud.get_products(
            db=db,
            skip=skip,
            limit=limit,
            active_only=active_only,
            category_id=category_id,
            search=search,
            min_price=min_price,
            max_price=max_price,
            brand=brand
        )
        return products
    except Exception as e:
        print(f"⚠️  Error fetching products: {e}")
        # Return mock data as fallback
        products = MOCK_PRODUCTS[skip:skip+limit]
        if category_id:
            products = [p for p in products if p["category_id"] == category_id]
        return products

@router.get("/products/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/products/slug/{slug}", response_model=schemas.ProductResponse)
def read_product_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a specific product by slug"""
    product = crud.get_product_by_slug(db, slug=slug)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    return crud.create_product(db=db, product=product)

@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """Update a product"""
    db_product = crud.update_product(db=db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = crud.delete_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Product Variant endpoints
@router.get("/products/{product_id}/variants", response_model=List[schemas.ProductVariantResponse])
def read_product_variants(product_id: int, db: Session = Depends(get_db)):
    """Get all variants for a specific product"""
    variants = crud.get_product_variants(db, product_id=product_id)
    return variants

@router.post("/products/{product_id}/variants", response_model=schemas.ProductVariantResponse)
def create_product_variant(
    product_id: int, 
    variant: schemas.ProductVariantCreate, 
    db: Session = Depends(get_db)
):
    """Create a new variant for a product"""
    return crud.create_product_variant(db=db, product_id=product_id, variant=variant)

@router.put("/variants/{variant_id}", response_model=schemas.ProductVariantResponse)
def update_product_variant(
    variant_id: int, 
    variant: schemas.ProductVariantUpdate, 
    db: Session = Depends(get_db)
):
    """Update a product variant"""
    db_variant = crud.update_product_variant(db=db, variant_id=variant_id, variant=variant)
    if db_variant is None:
        raise HTTPException(status_code=404, detail="Variant not found")
    return db_variant

@router.delete("/variants/{variant_id}")
def delete_product_variant(variant_id: int, db: Session = Depends(get_db)):
    """Delete a product variant"""
    db_variant = crud.delete_product_variant(db=db, variant_id=variant_id)
    if db_variant is None:
        raise HTTPException(status_code=404, detail="Variant not found")
    return {"message": "Variant deleted successfully"}

# User endpoints
@router.get("/users", response_model=List[schemas.UserResponse])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all users"""
    users = crud.get_users(db, skip=skip, limit=limit, active_only=active_only)
    return users

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.create_user(db=db, user=user)

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    db_user = crud.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Order endpoints
@router.get("/orders", response_model=List[schemas.OrderResponse])
def read_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all orders with optional user filtering"""
    orders = crud.get_orders(db, skip=skip, limit=limit, user_id=user_id)
    return orders

@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/orders", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    return crud.create_order(db=db, order=order)

@router.put("/orders/{order_id}", response_model=schemas.OrderResponse)
def update_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)):
    """Update an order"""
    db_order = crud.update_order(db=db, order_id=order_id, order=order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Favorite endpoints
@router.get("/users/{user_id}/favorites", response_model=List[schemas.FavoriteResponse])
def read_user_favorites(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get user favorites"""
    favorites = crud.get_user_favorites(db, user_id=user_id, skip=skip, limit=limit)
    return favorites

@router.post("/favorites", response_model=schemas.FavoriteResponse)
def add_favorite(favorite: schemas.FavoriteCreate, db: Session = Depends(get_db)):
    """Add a product to favorites"""
    return crud.add_favorite(db=db, favorite=favorite)

@router.delete("/users/{user_id}/favorites/{product_id}")
def remove_favorite(user_id: int, product_id: int, db: Session = Depends(get_db)):
    """Remove a product from favorites"""
    crud.remove_favorite(db=db, user_id=user_id, product_id=product_id)
    return {"message": "Favorite removed successfully"}

@router.get("/users/{user_id}/favorites/{product_id}/check")
def check_favorite(user_id: int, product_id: int, db: Session = Depends(get_db)):
    """Check if a product is in user favorites"""
    is_fav = crud.is_favorite(db=db, user_id=user_id, product_id=product_id)
    return {"is_favorite": is_fav}

# Message endpoints
@router.get("/messages", response_model=List[schemas.MessageResponse])
def read_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all messages with optional status filtering"""
    messages = crud.get_messages(db, skip=skip, limit=limit, status=status)
    return messages

@router.get("/messages/{message_id}", response_model=schemas.MessageResponse)
def read_message(message_id: int, db: Session = Depends(get_db)):
    """Get a specific message by ID"""
    message = crud.get_message(db, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.post("/messages", response_model=schemas.MessageResponse)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    """Create a new message"""
    return crud.create_message(db=db, message=message)

@router.put("/messages/{message_id}", response_model=schemas.MessageResponse)
def update_message(message_id: int, message: schemas.MessageUpdate, db: Session = Depends(get_db)):
    """Update a message status"""
    db_message = crud.update_message(db=db, message_id=message_id, message=message)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

# Dashboard endpoints
@router.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        if db is None:
            # Return mock data if database is not available
            return MOCK_DASHBOARD_STATS
        
        return crud.get_dashboard_stats(db)
    except Exception as e:
        print(f"⚠️  Error fetching dashboard stats: {e}")
        # Return mock data as fallback
        return MOCK_DASHBOARD_STATS
