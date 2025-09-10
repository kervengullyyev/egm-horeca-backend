import httpx
import hashlib
import hmac
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class WebhookClient:
    def __init__(self):
        self.frontend_url = os.getenv("FRONTEND_WEBHOOK_URL", "http://localhost:3000/api/revalidate")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "your-webhook-secret-here")
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload"""
        return hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def send_webhook(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Send webhook to frontend"""
        try:
            payload = {
                "type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload_str = json.dumps(payload)
            signature = self._generate_signature(payload_str)
            
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.frontend_url,
                    content=payload_str,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"Webhook sent successfully: {event_type}")
                    return True
                else:
                    print(f"Webhook failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error sending webhook: {e}")
            return False
    
    async def product_created(self, product_id: int, slug: str, category_id: int):
        """Send product created webhook"""
        return await self.send_webhook("product.created", {
            "id": product_id,
            "slug": slug,
            "category_id": category_id
        })
    
    async def product_updated(self, product_id: int, slug: str, category_id: int):
        """Send product updated webhook"""
        return await self.send_webhook("product.updated", {
            "id": product_id,
            "slug": slug,
            "category_id": category_id
        })
    
    async def product_deleted(self, product_id: int, category_id: int):
        """Send product deleted webhook"""
        return await self.send_webhook("product.deleted", {
            "id": product_id,
            "category_id": category_id
        })
    
    async def category_created(self, category_id: int, slug: str):
        """Send category created webhook"""
        return await self.send_webhook("category.created", {
            "id": category_id,
            "slug": slug
        })
    
    async def category_updated(self, category_id: int, slug: str):
        """Send category updated webhook"""
        return await self.send_webhook("category.updated", {
            "id": category_id,
            "slug": slug
        })
    
    async def category_deleted(self, category_id: int):
        """Send category deleted webhook"""
        return await self.send_webhook("category.deleted", {
            "id": category_id
        })
    
    async def order_created(self, order_id: int):
        """Send order created webhook"""
        return await self.send_webhook("order.created", {
            "id": order_id
        })
    
    async def order_updated(self, order_id: int):
        """Send order updated webhook"""
        return await self.send_webhook("order.updated", {
            "id": order_id
        })

# Global webhook client instance
webhook_client = WebhookClient()
