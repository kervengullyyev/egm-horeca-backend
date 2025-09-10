from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base schemas
class CategoryBase(BaseModel):
    name_en: str = Field(..., min_length=1, max_length=100)
    name_ro: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description_en: Optional[str] = None
    description_ro: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = Field(0, ge=0)
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name_en: Optional[str] = Field(None, min_length=1, max_length=100)
    name_ro: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description_en: Optional[str] = None
    description_ro: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CategoryReorder(BaseModel):
    category_id: int
    new_position: int = Field(..., ge=0)

class ProductBase(BaseModel):
    name_en: str = Field(..., min_length=1, max_length=200)
    name_ro: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description_en: Optional[str] = None
    description_ro: Optional[str] = None
    short_description_en: Optional[str] = Field(None, max_length=200)
    short_description_ro: Optional[str] = Field(None, max_length=200)
    price: float = Field(..., gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    category_id: int
    brand: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    stock_quantity: int = Field(0, ge=0)
    is_active: bool = True
    images: Optional[List[str]] = []
    has_variants: bool = False
    variant_type_en: Optional[str] = Field(None, max_length=100)  # e.g., "Size", "Color", "Material"
    variant_type_ro: Optional[str] = Field(None, max_length=100)  # Romanian variant type
    is_featured: bool = False
    is_top_product: bool = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name_en: Optional[str] = Field(None, min_length=1, max_length=200)
    name_ro: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description_en: Optional[str] = None
    description_ro: Optional[str] = None
    short_description_en: Optional[str] = Field(None, max_length=200)
    short_description_ro: Optional[str] = Field(None, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    images: Optional[List[str]] = None
    has_variants: Optional[bool] = None
    variant_type_en: Optional[str] = Field(None, max_length=100)
    variant_type_ro: Optional[str] = Field(None, max_length=100)
    is_featured: Optional[bool] = None
    is_top_product: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    category: Optional[CategoryResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field("customer", pattern="^(customer|admin)$")
    is_active: bool = True

class UserCreate(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field("customer", pattern="^(customer|admin)$")
    is_active: bool = True
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = Field(None, pattern="^(customer|admin)$")
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    total_price: float
    product_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int
    status: str = Field("pending", pattern="^(pending|confirmed|shipped|delivered|cancelled)$")
    total_amount: float = Field(..., gt=0)
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    payment_status: str = Field("pending", pattern="^(pending|paid|failed)$")
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|confirmed|shipped|delivered|cancelled)$")
    payment_status: Optional[str] = Field(None, pattern="^(pending|paid|failed)$")
    notes: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    order_number: str
    user: UserResponse
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    user_id: int
    product_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    created_at: datetime
    product: ProductResponse
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    subject: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=1)

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    status: str = Field(..., pattern="^(unread|read|replied)$")

class MessageResponse(MessageBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_revenue: float
    total_products: int
    total_orders: int
    total_customers: int
    pending_orders: int

class RecentActivity(BaseModel):
    action: str
    detail: str
    timestamp: datetime

# Search and filter schemas
class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brand: Optional[str] = None
    in_stock: Optional[bool] = None
    search: Optional[str] = None

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int

# Variant schemas
class ProductVariantBase(BaseModel):
    value_en: str = Field(..., min_length=1, max_length=100)
    value_ro: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)  # Absolute price for this variant
    stock_quantity: int = Field(0, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class ProductVariantCreate(ProductVariantBase):
    product_id: Optional[int] = None

class ProductVariantUpdate(BaseModel):
    value_en: Optional[str] = Field(None, min_length=1, max_length=100)
    value_ro: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class ProductVariantResponse(ProductVariantBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Update ProductResponse to include variants
class ProductResponseWithVariants(ProductResponse):
    variants: List[ProductVariantResponse] = []

# Order schemas
class OrderItemBase(BaseModel):
    product_id: int
    product_name: str
    product_slug: str
    variant_id: Optional[int] = None
    variant_name: Optional[str] = None
    variant_value_en: Optional[str] = None
    variant_value_ro: Optional[str] = None
    unit_price: float
    quantity: int
    total_price: float
    product_image: Optional[str] = None

class OrderBase(BaseModel):
    customer_email: str = Field(..., description="Customer email address")
    customer_name: str = Field(..., description="Customer full name")
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    
    # Company information (optional)
    company_name: Optional[str] = None
    tax_id: Optional[str] = None
    trade_register_no: Optional[str] = None
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    
    # Address information
    shipping_address: Dict[str, Any] = Field(..., description="Shipping address details")
    billing_address: Optional[Dict[str, Any]] = None

# Create order request
class CreateOrderRequest(BaseModel):
    customer_info: OrderBase
    cart_items: List[Dict[str, Any]] = Field(..., description="Cart items from frontend")
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str = "RON"

# Order response
class OrderItemResponse(OrderItemBase):
    id: str
    order_id: str

class OrderResponse(OrderBase):
    id: str
    order_number: str
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str
    
    # Payment information
    payment_status: str
    payment_method: str
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    receipt_url: Optional[str] = None
    
    # Order status
    order_status: str
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Order items
    items: List[OrderItemResponse]

# Update order request
class UpdateOrderRequest(BaseModel):
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None

# Order list response for admin
class OrderListResponse(BaseModel):
    id: str
    order_number: str
    customer_name: str
    customer_email: str
    total_amount: float
    currency: str
    payment_status: str
    order_status: str
    created_at: datetime
    order_items_count: int

# Stripe webhook data
class StripeWebhookData(BaseModel):
    stripe_session_id: str
    payment_status: str
    stripe_payment_intent_id: Optional[str] = None
    receipt_url: Optional[str] = None

# Password reset schemas
class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)

class PasswordResetResponse(BaseModel):
    success: bool
    message: str
