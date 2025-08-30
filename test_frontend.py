#!/usr/bin/env python3
"""
Test script for the FastAPI frontend
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_home_page():
    """Test the home page"""
    print("Testing home page...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "FastAPI Admin" in response.text
    print("✅ Home page works")

def test_login_page():
    """Test the login page"""
    print("Testing login page...")
    response = requests.get(f"{BASE_URL}/login")
    assert response.status_code == 200
    assert "Sign in to your account" in response.text
    print("✅ Login page works")

def test_register_page():
    """Test the register page"""
    print("Testing register page...")
    response = requests.get(f"{BASE_URL}/register")
    assert response.status_code == 200
    assert "Create your account" in response.text
    print("✅ Register page works")

def test_admin_redirect():
    """Test admin panel redirects to login when not authenticated"""
    print("Testing admin panel redirect...")
    response = requests.get(f"{BASE_URL}/admin", allow_redirects=False)
    assert response.status_code in [302, 303]  # Redirect
    print("✅ Admin panel correctly redirects to login")

def test_login_functionality():
    """Test login functionality"""
    print("Testing login functionality...")
    session = requests.Session()
    
    # Try to login with test user
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    assert response.status_code in [200, 303]  # Success or redirect
    print("✅ Login functionality works")

if __name__ == "__main__":
    print("🚀 Testing FastAPI Frontend...")
    print("=" * 50)
    
    try:
        test_home_page()
        test_login_page()
        test_register_page()
        test_admin_redirect()
        test_login_functionality()
        
        print("=" * 50)
        print("🎉 All frontend tests passed!")
        print("\n📋 Frontend Features Available:")
        print("  • Home page: http://localhost:8000/")
        print("  • Login page: http://localhost:8000/login")
        print("  • Register page: http://localhost:8000/register")
        print("  • Admin panel: http://localhost:8000/admin (requires login)")
        print("\n👤 Test Users:")
        print("  • Admin: test@example.com / testpassword")
        print("  • Regular: newuser@example.com / newpassword")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)
