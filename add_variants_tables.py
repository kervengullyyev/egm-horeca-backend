#!/usr/bin/env python3
"""
Script to add product variants functionality to the database
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/egm_horeca")

def add_variants_tables():
    """Add product variants tables and columns"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Add has_variants column to products table
            print("Adding has_variants column to products table...")
            connection.execute(text("""
                ALTER TABLE products 
                ADD COLUMN IF NOT EXISTS has_variants BOOLEAN DEFAULT FALSE
            """))
            
            # Create product_variants table
            print("Creating product_variants table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS product_variants (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                    name_en VARCHAR(100) NOT NULL,
                    name_ro VARCHAR(100) NOT NULL,
                    value_en VARCHAR(100) NOT NULL,
                    value_ro VARCHAR(100) NOT NULL,
                    price_adjustment DECIMAL(10,2) DEFAULT 0.0,
                    stock_quantity INTEGER DEFAULT 0,
                    sku VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Add indexes for better performance
            print("Adding indexes...")
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_product_variants_product_id 
                ON product_variants(product_id)
            """))
            
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_product_variants_active 
                ON product_variants(is_active)
            """))
            
            # Commit changes
            connection.commit()
            print("✅ Successfully added product variants functionality!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            connection.rollback()
            sys.exit(1)

if __name__ == "__main__":
    print("🚀 Adding product variants functionality to database...")
    add_variants_tables()
    print("✨ Done!")
