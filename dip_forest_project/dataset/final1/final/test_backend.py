#!/usr/bin/env python3
"""
Simple test script to verify StudySphere backend functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running.")
        return False

def test_signup():
    """Test user signup"""
    print("\nTesting user signup...")
    signup_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "academic_goal": "Test academic goal",
        "focus_areas": "Math, Science"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
        if response.status_code == 201:
            print("✅ Signup successful")
            return response.json().get('token')
        else:
            print(f"❌ Signup failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful")
            return response.json().get('token')
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    print("\nTesting protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return False

def test_subjects_endpoint(token):
    """Test subjects endpoint"""
    print("\nTesting subjects endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/subjects/", headers=headers)
        if response.status_code == 200:
            print("✅ Subjects endpoint successful")
            return True
        else:
            print(f"❌ Subjects endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Subjects endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 StudySphere Backend Test Suite")
    print("=" * 40)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Backend is not running or not accessible")
        sys.exit(1)
    
    # Test signup
    token = test_signup()
    if not token:
        # Try login if signup failed (user might already exist)
        token = test_login()
    
    if not token:
        print("\n❌ Authentication failed")
        sys.exit(1)
    
    # Test protected endpoints
    test_protected_endpoint(token)
    test_subjects_endpoint(token)
    
    print("\n✅ All tests completed!")
    print("\nTo run the full application:")
    print("1. Backend: python server.py")
    print("2. Frontend: cd frontend && npm start")

if __name__ == "__main__":
    main() 