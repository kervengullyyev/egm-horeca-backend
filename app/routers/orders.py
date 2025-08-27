from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Order, OrderItem, Product, ProductVariant
from app.schemas import (
    CreateOrderRequest, 
    OrderResponse, 
    OrderListResponse,
    UpdateOrderRequest,
    StripeWebhookData
)

router = APIRouter()

def generate_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"

@router.post("/", response_model=OrderResponse)
async def create_order(order_data: CreateOrderRequest, db: Session = Depends(get_db)):
    """Create a new order"""
    try:
        # Generate unique order number
        order_number = generate_order_number()
        
        # Create order
        order = Order(
            id=str(uuid.uuid4()),  # Generate UUID for order ID
            order_number=order_number,
            customer_email=order_data.customer_info.customer_email,
            customer_name=order_data.customer_info.customer_name,
            customer_phone=order_data.customer_info.customer_phone,
            company_name=order_data.customer_info.company_name,
            tax_id=order_data.customer_info.tax_id,
            trade_register_no=order_data.customer_info.trade_register_no,
            bank_name=order_data.customer_info.bank_name,
            iban=order_data.customer_info.iban,
            shipping_address=order_data.customer_info.shipping_address,
            billing_address=order_data.customer_info.billing_address or order_data.customer_info.shipping_address,
            subtotal=order_data.subtotal,
            tax_amount=order_data.tax_amount,
            total_amount=order_data.total_amount,
            currency=order_data.currency,
            payment_status="pending",
            order_status="pending"
        )
        
        db.add(order)
        db.flush()  # Get the order ID
        
        # Create order items
        order_items = []
        print(f"DEBUG: Processing {len(order_data.cart_items)} cart items")
        for item in order_data.cart_items:
            print(f"DEBUG: Processing cart item: {item}")
            # Get product details
            product = db.query(Product).filter(Product.id == item["id"]).first()
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {item['id']} not found")
            
            # Get variant details if applicable
            variant = None
            variant_type = None
            if item.get("variants"):
                # The variants object contains variant type info, not variant IDs
                # We need to find the variant by product_id and variant value
                variant_type = list(item["variants"].keys())[0]  # e.g., "Size"
                variant_value = item["variants"][variant_type]["value_en"]  # e.g., "Large"
                
                print(f"DEBUG: Looking for variant - product_id: {product.id}, variant_type: {variant_type}, variant_value: {variant_value}")
                
                # Find variant by product_id and value_en
                variant = db.query(ProductVariant).filter(
                    ProductVariant.product_id == product.id,
                    ProductVariant.value_en == variant_value
                ).first()
                
                if variant:
                    print(f"DEBUG: Found variant with ID: {variant.id}")
                else:
                    print(f"DEBUG: No variant found for product {product.id} with value {variant_value}")
            
            # Calculate prices
            if item.get("variants"):
                # Use the price from the frontend variant data
                variant_type = list(item["variants"].keys())[0]
                unit_price = item["variants"][variant_type]["price"]
            else:
                unit_price = product.price
            total_price = unit_price * item["quantity"]
            
            order_item = OrderItem(
                id=str(uuid.uuid4()),  # Generate UUID for order item ID
                order_id=order.id,
                product_id=product.id,
                product_name=product.name_en,
                product_slug=product.slug,
                variant_id=variant.id if variant else None,
                variant_name=variant_type if variant else None,
                variant_value_en=variant.value_en if variant else None,
                variant_value_ro=variant.value_ro if variant else None,
                unit_price=unit_price,
                quantity=item["quantity"],
                total_price=total_price,
                product_image=product.images[0] if product.images else None
            )
            
            order_items.append(order_item)
        
        db.add_all(order_items)
        db.commit()
        
        # Refresh to get the complete order with items
        db.refresh(order)
        
        return order
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.get("/", response_model=List[OrderListResponse])
async def get_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all orders (for admin)"""
    try:
        # Get orders with item count
        orders = db.query(
            Order,
            func.count(OrderItem.id).label('order_items_count')
        ).outerjoin(OrderItem).group_by(Order.id).offset(skip).limit(limit).all()
        
        result = []
        for order, item_count in orders:
            result.append(OrderListResponse(
                id=order.id,
                order_number=order.order_number,
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                total_amount=order.total_amount,
                currency=order.currency,
                payment_status=order.payment_status,
                order_status=order.order_status,
                created_at=order.created_at,
                order_items_count=item_count
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return order
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str, 
    order_update: UpdateOrderRequest, 
    db: Session = Depends(get_db)
):
    """Update an order (for admin)"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update fields
        if order_update.order_status is not None:
            order.order_status = order_update.order_status
        if order_update.payment_status is not None:
            order.payment_status = order_update.payment_status
        if order_update.shipping_address is not None:
            order.shipping_address = order_update.shipping_address
        if order_update.billing_address is not None:
            order.billing_address = order_update.billing_address
        
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
        
        return order
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")

@router.post("/webhook/stripe")
async def stripe_webhook(webhook_data: StripeWebhookData, db: Session = Depends(get_db)):
    """Handle Stripe webhook to update payment status"""
    try:
        # Find order by Stripe session ID
        order = db.query(Order).filter(Order.stripe_session_id == webhook_data.stripe_session_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update payment information
        order.payment_status = webhook_data.payment_status
        order.stripe_payment_intent_id = webhook_data.stripe_payment_intent_id
        order.receipt_url = webhook_data.receipt_url
        
        # Update order status based on payment
        if webhook_data.payment_status == "paid":
            order.order_status = "processing"
        elif webhook_data.payment_status == "failed":
            order.order_status = "cancelled"
        
        order.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Order updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")

@router.get("/by-session/{session_id}")
async def get_order_by_session(session_id: str, db: Session = Depends(get_db)):
    """Get order by Stripe session ID"""
    try:
        order = db.query(Order).filter(Order.stripe_session_id == session_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return order
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")
