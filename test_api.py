#!/usr/bin/env python3
"""
Simple test script to verify the backend API is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

def test_root():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            data = response.json()
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            if 'endpoints' in data:
                print("   Available endpoints:")
                for name, path in data['endpoints'].items():
                    print(f"     {name}: {path}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def test_api_endpoints():
    """Test the main API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    # Test categories
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories endpoint working - {len(categories)} categories found")
        else:
            print(f"❌ Categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories endpoint error: {e}")
    
    # Test products
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Products endpoint working - {len(products)} products found")
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Products endpoint error: {e}")
    
    # Test dashboard stats
    try:
        response = requests.get(f"{BASE_URL}/api/v1/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Dashboard stats endpoint working")
            print(f"   Total products: {stats.get('total_products')}")
            print(f"   Total orders: {stats.get('total_orders')}")
        else:
            print(f"❌ Dashboard stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard stats endpoint error: {e}")

def test_docs():
    """Test if API docs are accessible"""
    print("\n🔍 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API documentation error: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing EGM Horeca Backend API")
    print("=" * 50)
    
    test_health()
    test_root()
    test_api_endpoints()
    test_docs()
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    main()
