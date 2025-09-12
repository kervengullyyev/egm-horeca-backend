#!/usr/bin/env python3
"""
Script to create an admin user for the EGM Horeca admin panel.
Run this script to create the first admin user.
"""

import sys
import os
from sqlalchemy.orm import Session
from app.database import get_session_local
from app import crud
from app.utils import hash_password

def create_admin_user():
    """Create an admin user"""
    print("🔐 EGM Horeca Admin User Creation")
    print("=" * 40)
    
    # Get database session
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        # Get admin details
        email = input("Enter admin email: ").strip()
        if not email:
            print("❌ Email is required")
            return False
            
        password = input("Enter admin password (min 6 characters): ").strip()
        if len(password) < 6:
            print("❌ Password must be at least 6 characters")
            return False
            
        full_name = input("Enter admin full name: ").strip()
        if not full_name:
            print("❌ Full name is required")
            return False
            
        role = input("Enter role (admin/super_admin) [admin]: ").strip() or "admin"
        if role not in ["admin", "super_admin"]:
            print("❌ Role must be 'admin' or 'super_admin'")
            return False
        
        # Check if user already exists
        existing_user = crud.get_user_by_email(db, email=email)
        if existing_user:
            print(f"❌ User with email {email} already exists")
            return False
        
        # Create admin user
        from app.schemas import UserCreate
        
        admin_data = UserCreate(
            email=email,
            username=email.split("@")[0],  # Use email prefix as username
            full_name=full_name,
            password=password,  # Pass plain password, crud will hash it
            role=role,
            is_active=True,
            phone=None
        )
        
        admin_user = crud.create_user(db, admin_data)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Name: {admin_user.full_name}")
        print(f"   Role: {admin_user.role}")
        print(f"   ID: {admin_user.id}")
        print("\n🚀 You can now log in to the admin panel!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_admin_user()
    sys.exit(0 if success else 1)
