#!/usr/bin/env python3
"""
Test authentication and API endpoints for StudySphere
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_signup():
    """Test signup endpoint"""
    try:
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'academic_goal': 'Get good grades',
            'focus_areas': 'Math, Science'
        }
        response = requests.post(f'{BASE_URL}/auth/signup', json=data)
        print(f"✅ Signup: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"Token: {result.get('token', 'No token')[:20]}...")
            return result.get('token')
        else:
            print(f"Response: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Signup failed: {e}")
        return None

def test_login():
    """Test login endpoint"""
    try:
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Token: {result.get('token', 'No token')[:20]}...")
            return result.get('token')
        else:
            print(f"Response: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    if not token:
        print("❌ No token provided")
        return False
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/subjects/', headers=headers)
        print(f"✅ Protected endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Protected endpoint failed: {e}")
        return False

def main():
    print("🧪 Testing StudySphere Backend...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Backend is not running or not accessible")
        return
    
    print("\n" + "=" * 50)
    
    # Test signup
    token = test_signup()
    
    print("\n" + "=" * 50)
    
    # Test login
    if not token:
        token = test_login()
    
    print("\n" + "=" * 50)
    
    # Test protected endpoint
    if token:
        test_protected_endpoint(token)
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    main() 