"""
Admin activity logging
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User

logger = logging.getLogger(__name__)

def log_admin_activity(
    admin_user: User,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
):
    """
    Log admin activity for audit trail
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "admin_id": admin_user.id,
        "admin_email": admin_user.email,
        "admin_role": admin_user.role,
        "action": action,
        "resource": resource,
        "resource_id": resource_id,
        "details": details,
        "ip_address": ip_address
    }
    
    # Log to application logger
    logger.info(f"ADMIN_ACTIVITY: {log_data}")
    
    # In production, you might want to store this in a database table
    # For now, we'll just use the application logger

def log_login_attempt(ip_address: str, email: str, success: bool, reason: Optional[str] = None):
    """Log login attempts"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": ip_address,
        "email": email,
        "success": success,
        "reason": reason
    }
    
    if success:
        logger.info(f"ADMIN_LOGIN_SUCCESS: {log_data}")
    else:
        logger.warning(f"ADMIN_LOGIN_FAILED: {log_data}")

def log_admin_action(admin_user: User, action: str, **kwargs):
    """Convenience method for logging admin actions"""
    log_admin_activity(
        admin_user=admin_user,
        action=action,
        resource=kwargs.get('resource', 'unknown'),
        resource_id=kwargs.get('resource_id'),
        details=kwargs.get('details'),
        ip_address=kwargs.get('ip_address')
    )
