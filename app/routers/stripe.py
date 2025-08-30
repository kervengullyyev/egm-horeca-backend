from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import stripe
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order
from app.schemas import CreateOrderRequest, OrderBase

load_dotenv()

# Initialize Stripe - validate environment variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
if not STRIPE_SECRET_KEY:
    raise ValueError("STRIPE_SECRET_KEY environment variable must be set")

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/stripe", tags=["stripe"])

class CartItem(BaseModel):
    id: str
    name: str
    price: float
    qty: int
    variants: Union[Dict[str, Any], None] = None

class CustomerInfo(BaseModel):
    entityType: str
    firstName: str
    lastName: str
    phone: str
    email: str
    taxId: Union[str, None] = None
    companyName: Union[str, None] = None
    county: str
    city: str
    address: str

class CheckoutRequest(BaseModel):
    cartItems: List[CartItem]
    customerInfo: CustomerInfo
    total: float
    orderId: Optional[str] = None

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest):
    try:
        # Calculate subtotal and tax
        subtotal = sum(item.price * item.qty for item in request.cartItems)
        tax_amount = subtotal * 0.21
        
        # Create single line item with total price only
        line_items = [{
            "price_data": {
                "currency": "ron",
                "product_data": {
                    "name": "Order Total",
                    "description": "21% tax included"
                },
                "unit_amount": int(request.total * 100),  # Convert to cents
            },
            "quantity": 1,
        }]
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{os.getenv('FRONTEND_URL')}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/checkout/cancel",
            customer_email=request.customerInfo.email,
            metadata={
                "customer_name": f"{request.customerInfo.firstName} {request.customerInfo.lastName}",
                "customer_phone": request.customerInfo.phone,
                "customer_email": request.customerInfo.email,
                "entity_type": request.customerInfo.entityType,
                "county": request.customerInfo.county,
                "city": request.customerInfo.city,
                "address": request.customerInfo.address,
                "subtotal": str(subtotal),
                "tax_amount": str(tax_amount),
                "total_amount": str(request.total),
                "order_id": request.orderId,
            }
        )

        return {
            "url": session.url, 
            "session_id": session.id,
            "tax_breakdown": {
                "subtotal": subtotal,
                "tax_rate": 0.21,
                "tax_amount": tax_amount,
                "total": request.total
            }
        }

    except Exception as e:
        print(f"Error creating Stripe session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@router.get("/session/{session_id}")
async def get_session_details(session_id: str):
    try:
        # Retrieve the checkout session
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == "paid":
            # Get the payment intent
            payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
            
            # Get the latest charge to access receipt_url
            if payment_intent.latest_charge:
                charge = stripe.Charge.retrieve(payment_intent.latest_charge)
                return {
                    "session_id": session_id,
                    "status": session.payment_status,
                    "receipt_url": charge.receipt_url,
                    "amount": session.amount_total / 100,  # Convert from cents
                    "currency": session.currency.upper()
                }
        
        return {
            "session_id": session_id,
            "status": session.payment_status,
            "receipt_url": None,
            "amount": None,
            "currency": None
        }
        
    except Exception as e:
        print(f"Error retrieving session: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session details")

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    print(f"Webhook received: {request.headers.get('stripe-signature')}")
    print(f"Payload length: {len(payload)} bytes")
    print(f"Webhook secret configured: {'Yes' if webhook_secret and webhook_secret != 'whsec_your_webhook_secret_here' else 'No'}")
    print(f"Webhook secret starts with: {webhook_secret[:10] if webhook_secret else 'None'}...")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
        print(f"Webhook event type: {event['type']}")
        print(f"Webhook event data: {event['data']['object'].keys()}")
        
    except ValueError as e:
        print(f"Webhook ValueError: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook SignatureVerificationError: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")
    except Exception as e:
        print(f"Webhook unexpected error: {e}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment successful for session: {session.id}")
        
        # Find order by order ID in metadata
        order_id = session.metadata.get("order_id")
        print(f"Looking for order with ID: {order_id}")
        
        if order_id:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                print(f"Found order: {order.order_number}")
                order.payment_status = "paid"
                order.stripe_payment_intent_id = session.payment_intent
                order.stripe_session_id = session.id
                order.order_status = "processing"
                
                # Get receipt URL from payment intent
                if session.payment_intent:
                    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                    if payment_intent.latest_charge:
                        charge = stripe.Charge.retrieve(payment_intent.latest_charge)
                        order.receipt_url = charge.receipt_url
                
                db.commit()
                print(f"Order {order.order_number} updated to paid status")
            else:
                print(f"Order not found with ID: {order_id}")
        else:
            print("No order_id found in session metadata")
        
    elif event["type"] == "payment_intent.payment_failed":
        session = event["data"]["object"]
        print(f"Payment failed for session: {session.id}")
        
        # Find order by order ID in metadata
        order_id = session.metadata.get("order_id")
        if order_id:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.payment_status = "failed"
                order.stripe_session_id = session.id
                order.order_status = "cancelled"
                db.commit()
                print(f"Order {order.order_number} updated to failed status")

    return {"status": "success"}
