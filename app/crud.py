from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from app import models, schemas
import uuid

# Category CRUD operations
def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_slug(db: Session, slug: str):
    return db.query(models.Category).filter(models.Category.slug == slug).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True):
    query = db.query(models.Category)
    if active_only:
        query = query.filter(models.Category.is_active == True)
    return query.order_by(models.Category.sort_order.asc(), models.Category.id.asc()).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate):
    db_category = get_category(db, category_id)
    if db_category:
        update_data = category.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

def reorder_categories(db: Session, reorder_data: List[schemas.CategoryReorder]):
    """Reorder categories based on provided positions"""
    try:
        # Get all categories to update
        category_ids = [item.category_id for item in reorder_data]
        categories = db.query(models.Category).filter(models.Category.id.in_(category_ids)).all()
        
        # Create a mapping of category_id to new position
        position_map = {item.category_id: item.new_position for item in reorder_data}
        
        # Update sort_order for each category
        for category in categories:
            if category.id in position_map:
                category.sort_order = position_map[category.id]
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e

# Product CRUD operations
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_slug(db: Session, slug: str):
    return db.query(models.Product).filter(models.Product.slug == slug).first()

def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    language: Optional[str] = None
):
    query = db.query(models.Product)
    
    if active_only:
        query = query.filter(models.Product.is_active == True)
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if search:
        if language == "ro":
            # For Romanian, search only in Romanian fields and ensure Romanian content exists
            search_filter = and_(
                or_(
                    models.Product.name_ro.ilike(f"%{search}%"),
                    models.Product.description_ro.ilike(f"%{search}%")
                ),
                models.Product.name_ro.isnot(None),
                models.Product.name_ro != ""
            )
        else:
            # For English (default), search only in English fields and ensure English content exists
            search_filter = and_(
                or_(
                    models.Product.name_en.ilike(f"%{search}%"),
                    models.Product.description_en.ilike(f"%{search}%")
                ),
                models.Product.name_en.isnot(None),
                models.Product.name_en != ""
            )
        query = query.filter(search_filter)
    
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    
    if brand:
        query = query.filter(models.Product.brand == brand)
    
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True):
    query = db.query(models.User)
    if active_only:
        query = query.filter(models.User.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # Hash the password before storing
    from app.utils import hash_password
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        phone=user.phone,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# Order CRUD operations
def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_order_by_number(db: Session, order_number: str):
    return db.query(models.Order).filter(models.Order.order_number == order_number).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None):
    query = db.query(models.Order)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    # Generate unique order number
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    db_order = models.Order(
        order_number=order_number,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        billing_address=order.billing_address,
        payment_status=order.payment_status,
        payment_method=order.payment_method,
        notes=order.notes
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for item in order.items:
        product = get_product(db, item.product_id)
        if product:
            order_item = models.OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price,
                product_data={
                    "name": product.name_en,
                    "price": product.price,
                    "image": product.images[0] if product.images else None
                }
            )
            db.add(order_item)
    
    db.commit()
    return db_order

def update_order(db: Session, order_id: int, order: schemas.OrderUpdate):
    db_order = get_order(db, order_id)
    if db_order:
        update_data = order.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        db.commit()
        db.refresh(db_order)
    return db_order

# Favorite CRUD operations
def get_user_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).offset(skip).limit(limit).all()

def add_favorite(db: Session, favorite: schemas.FavoriteCreate):
    # Check if already exists
    existing = db.query(models.Favorite).filter(
        and_(
            models.Favorite.user_id == favorite.user_id,
            models.Favorite.product_id == favorite.product_id
        )
    ).first()
    
    if existing:
        return existing
    
    db_favorite = models.Favorite(**favorite.model_dump())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def remove_favorite(db: Session, user_id: int, product_id: int):
    db_favorite = db.query(models.Favorite).filter(
        and_(
            models.Favorite.user_id == user_id,
            models.Favorite.product_id == product_id
        )
    ).first()
    
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
    return db_favorite

def is_favorite(db: Session, user_id: int, product_id: int):
    return db.query(models.Favorite).filter(
        and_(
            models.Favorite.user_id == user_id,
            models.Favorite.product_id == product_id
        )
    ).first() is not None

# Message CRUD operations
def get_message(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()

def get_messages(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    query = db.query(models.Message)
    if status:
        query = query.filter(models.Message.status == status)
    return query.offset(skip).limit(limit).all()

def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message(db: Session, message_id: int, message: schemas.MessageUpdate):
    db_message = get_message(db, message_id)
    if db_message:
        update_data = message.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_message, field, value)
        db.commit()
        db.refresh(db_message)
    return db_message

# Dashboard statistics
def get_dashboard_stats(db: Session):
    total_revenue = db.query(func.coalesce(func.sum(models.Order.total_amount), 0)).filter(
        models.Order.payment_status == "paid"
    ).scalar()
    
    total_products = db.query(func.count(models.Product.id)).scalar()
    total_orders = db.query(func.count(models.Order.id)).scalar()
    total_customers = db.query(func.count(models.User.id)).filter(models.User.role == "customer").scalar()
    pending_orders = db.query(func.count(models.Order.id)).filter(models.Order.status == "pending").scalar()
    
    return {
        "total_revenue": float(total_revenue),
        "total_products": total_products,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "pending_orders": pending_orders
    }

# Product Variant CRUD operations
def get_product_variants(db: Session, product_id: int):
    return db.query(models.ProductVariant).filter(
        models.ProductVariant.product_id == product_id,
        models.ProductVariant.is_active == True
    ).all()

def get_product_variant(db: Session, variant_id: int):
    return db.query(models.ProductVariant).filter(models.ProductVariant.id == variant_id).first()

def create_product_variant(db: Session, product_id: int, variant: schemas.ProductVariantCreate):
    # Set the product_id from the URL parameter
    variant_data = variant.model_dump()
    variant_data["product_id"] = product_id
    
    db_variant = models.ProductVariant(**variant_data)
    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)
    
    # Update the product to mark it as having variants
    product = get_product(db, product_id)
    if product:
        product.has_variants = True
        # Note: variant_type should be set when creating the product or first variant
        db.commit()
    
    return db_variant

def update_product_variant(db: Session, variant_id: int, variant: schemas.ProductVariantUpdate):
    db_variant = get_product_variant(db, variant_id)
    if db_variant:
        update_data = variant.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_variant, field, value)
        db.commit()
        db.refresh(db_variant)
    return db_variant

def delete_product_variant(db: Session, variant_id: int):
    db_variant = get_product_variant(db, variant_id)
    if db_variant:
        # Check if this was the last variant for the product BEFORE deleting
        product_id = db_variant.product_id
        remaining_variants = db.query(models.ProductVariant).filter(
            models.ProductVariant.product_id == product_id,
            models.ProductVariant.is_active == True
        ).count()
        
        # Delete the variant first
        db.delete(db_variant)
        db.commit()
        
        # If this was the last variant, mark product as not having variants
        if remaining_variants <= 1:  # <= 1 because we're counting before deletion
            product = get_product(db, product_id)
            if product:
                product.has_variants = False
                db.commit()
    
    return db_variant
