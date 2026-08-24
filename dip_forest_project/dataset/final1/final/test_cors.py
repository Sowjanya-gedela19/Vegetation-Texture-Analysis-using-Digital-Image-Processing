#!/usr/bin/env python3
"""
Test CORS preflight requests for StudySphere
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_cors_preflight():
    """Test CORS preflight request"""
    try:
        # Test OPTIONS request (preflight)
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization, Content-Type'
        }
        
        response = requests.options(f'{BASE_URL}/sessions', headers=headers)
        print(f"✅ CORS Preflight: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
        return True
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def test_actual_request():
    """Test actual request with Authorization header"""
    try:
        # First get a token
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        login_response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print("❌ Could not get token for testing")
            return False
            
        token = login_response.json().get('token')
        
        # Test actual request
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000'
        }
        
        response = requests.get(f'{BASE_URL}/sessions', headers=headers)
        print(f"✅ Actual Request: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Actual request test failed: {e}")
        return False

def main():
    print("🧪 Testing CORS Configuration...")
    print("=" * 50)
    
    # Test preflight
    if not test_cors_preflight():
        print("❌ CORS preflight failed")
        return
    
    print("\n" + "=" * 50)
    
    # Test actual request
    if not test_actual_request():
        print("❌ Actual request failed")
        return
    
    print("\n" + "=" * 50)
    print("✅ CORS testing complete!")

if __name__ == "__main__":
    main() 