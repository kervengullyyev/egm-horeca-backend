"""
Security utilities for admin authentication
"""
import time
from typing import Dict, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Store login attempts per IP
login_attempts: Dict[str, list] = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds

def check_login_attempts(ip_address: str) -> Tuple[bool, str]:
    """
    Check if IP is allowed to attempt login
    Returns (is_allowed, message)
    """
    current_time = time.time()
    
    # Clean old attempts
    login_attempts[ip_address] = [
        attempt_time for attempt_time in login_attempts[ip_address]
        if current_time - attempt_time < LOCKOUT_DURATION
    ]
    
    # Check if too many attempts
    if len(login_attempts[ip_address]) >= MAX_ATTEMPTS:
        oldest_attempt = min(login_attempts[ip_address])
        remaining_time = LOCKOUT_DURATION - (current_time - oldest_attempt)
        return False, f"Too many login attempts. Try again in {int(remaining_time/60)} minutes."
    
    return True, ""

def record_failed_attempt(ip_address: str) -> None:
    """Record a failed login attempt"""
    current_time = time.time()
    login_attempts[ip_address].append(current_time)
    logger.warning(f"Failed login attempt from IP: {ip_address}")

def record_successful_login(ip_address: str) -> None:
    """Clear failed attempts after successful login"""
    if ip_address in login_attempts:
        del login_attempts[ip_address]
    logger.info(f"Successful admin login from IP: {ip_address}")

def get_attempts_count(ip_address: str) -> int:
    """Get current number of failed attempts for IP"""
    current_time = time.time()
    login_attempts[ip_address] = [
        attempt_time for attempt_time in login_attempts[ip_address]
        if current_time - attempt_time < LOCKOUT_DURATION
    ]
    return len(login_attempts[ip_address])

# IP whitelist for admin access (in production, load from environment or database)
ADMIN_IP_WHITELIST = [
    "127.0.0.1",  # localhost
    "::1",        # localhost IPv6
    # Add your trusted IPs here
]

def is_ip_whitelisted(ip_address: str) -> bool:
    """Check if IP is whitelisted for admin access"""
    import os
    whitelist = os.getenv("ADMIN_IP_WHITELIST", "").split(",")
    if whitelist and whitelist[0]:  # If whitelist is configured
        return ip_address in whitelist
    return True  # If no whitelist configured, allow all IPs

def check_admin_ip_access(ip_address: str) -> Tuple[bool, str]:
    """
    Check if IP is allowed for admin access
    Returns (is_allowed, message)
    """
    if not is_ip_whitelisted(ip_address):
        return False, "Access denied from this IP address"
    return True, ""
