from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(100), nullable=False)
    name_ro = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description_en = Column(Text)
    description_ro = Column(Text)
    image_url = Column(String(255))
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(200), nullable=False)
    name_ro = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description_en = Column(Text)
    description_ro = Column(Text)
    short_description_en = Column(String(200))
    short_description_ro = Column(String(200))
    price = Column(Float, nullable=False)
    sale_price = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"))
    brand = Column(String(100))
    sku = Column(String(100), unique=True)
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    images = Column(JSON)  # Array of image URLs
    has_variants = Column(Boolean, default=False)  # Whether product has variants
    variant_type_en = Column(String(100))  # e.g., "Size", "Color", "Material" - only one type allowed
    variant_type_ro = Column(String(100))  # Romanian variant type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    value_en = Column(String(100), nullable=False)  # e.g., "Large", "Red", "Cotton"
    value_ro = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)  # Absolute price for this variant
    stock_quantity = Column(Integer, default=0)
    sku = Column(String(100))  # Unique SKU for this variant
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", back_populates="variants")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(20), default="customer")  # customer, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    favorites = relationship("Favorite", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_email = Column(String(255), nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_phone = Column(String(20))
    
    # Order details
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="RON")
    
    # Payment information
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, cancelled
    payment_method = Column(String(50), default="stripe")
    stripe_session_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    receipt_url = Column(String(500))
    
    # Order status
    order_status = Column(String(50), default="pending")  # pending, processing, shipped, delivered, cancelled
    
    # Shipping information
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    
    # Company information (if applicable)
    company_name = Column(String(200))
    tax_id = Column(String(100))
    trade_register_no = Column(String(100))
    bank_name = Column(String(200))
    iban = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_slug = Column(String(200), nullable=False)
    
    # Variant information
    variant_id = Column(Integer, ForeignKey("product_variants.id"))
    variant_name = Column(String(100))
    variant_value_en = Column(String(100))
    variant_value_ro = Column(String(100))
    
    # Pricing
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Product images
    product_image = Column(String(500))
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="favorites")
    product = relationship("Product")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(200))
    message = Column(Text, nullable=False)
    status = Column(String(50), default="unread")  # unread, read, replied
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
