#!/usr/bin/env python3
"""
Test script for the 404 page functionality
"""
import requests

BASE_URL = "http://localhost:8000"

def test_admin_access_with_regular_user():
    """Test admin access with a regular user"""
    print("Testing admin access with regular user...")
    
    session = requests.Session()
    
    # First, login as a regular user (newuser@example.com)
    login_data = {
        "email": "newuser@example.com",
        "password": "newpassword"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Login response status: {response.status_code}")
    
    # Now try to access admin panel
    response = session.get(f"{BASE_URL}/admin")
    print(f"Admin access response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin access correctly returns custom 404 page for regular user")
        
        # Check if it's our custom 404 page
        if "Access Denied" in response.text:
            print("✅ Custom 404 page with 'Access Denied' message")
        else:
            print("❌ Not showing custom 404 page")
            
        if "Login as Admin" in response.text:
            print("✅ Custom 404 page includes 'Login as Admin' button")
        else:
            print("❌ Missing 'Login as Admin' button")
    else:
        print(f"❌ Expected 200, got {response.status_code}")

def test_admin_access_with_admin_user():
    """Test admin access with an admin user"""
    print("\nTesting admin access with admin user...")
    
    session = requests.Session()
    
    # Login as admin user
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Admin login response status: {response.status_code}")
    
    # Now try to access admin panel
    response = session.get(f"{BASE_URL}/admin")
    print(f"Admin access response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin access works for admin user")
        if "Admin Panel" in response.text:
            print("✅ Admin panel page loads correctly")
        else:
            print("❌ Admin panel page not loading correctly")
    else:
        print(f"❌ Expected 200, got {response.status_code}")

def test_general_404():
    """Test general 404 page"""
    print("\nTesting general 404 page...")
    
    response = requests.get(f"{BASE_URL}/nonexistent-page")
    print(f"404 response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ General 404 page works")
        if "Page Not Found" in response.text:
            print("✅ Custom 404 page with 'Page Not Found' message")
        else:
            print("❌ Not showing custom 404 page")
    else:
        print(f"❌ Expected 200, got {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing 404 Page Functionality...")
    print("=" * 50)
    
    try:
        test_admin_access_with_regular_user()
        test_admin_access_with_admin_user()
        test_general_404()
        
        print("=" * 50)
        print("🎉 404 page tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)
