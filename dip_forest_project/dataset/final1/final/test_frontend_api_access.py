#!/usr/bin/env python3
"""
Test if the frontend can access the APIs through the proxy
"""

import requests
import json

def test_frontend_proxy_access():
    """Test API access as if coming from frontend"""
    try:
        # Simulate frontend making requests through proxy
        headers = {
            'Origin': 'http://localhost:3000',
            'Content-Type': 'application/json'
        }
        
        # Test without auth first
        print("🔍 Testing health endpoint...")
        health_response = requests.get('http://127.0.0.1:5000/api/health', headers=headers)
        print(f"Health Status: {health_response.status_code}")
        
        # Test with auth
        print("\n🔐 Testing with authentication...")
        
        # Login first
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        login_response = requests.post('http://127.0.0.1:5000/api/auth/login', 
                                    json=login_data, headers=headers)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        token = login_response.json().get('token')
        print(f"✅ Login successful!")
        
        # Test dashboard endpoints with auth
        auth_headers = {
            **headers,
            'Authorization': f'Bearer {token}'
        }
        
        print("\n📊 Testing dashboard endpoints...")
        
        # Test each endpoint
        endpoints = [
            ('/sessions/analytics?days=7', 'Analytics'),
            ('/ai/suggestions', 'AI Suggestions'),
            ('/sessions?limit=3', 'Recent Sessions')
        ]
        
        for endpoint, name in endpoints:
            print(f"\nTesting {name}...")
            response = requests.get(f'http://127.0.0.1:5000/api{endpoint}', 
                                 headers=auth_headers)
            print(f"{name} Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"{name} Error: {response.text}")
                return False
            else:
                print(f"{name} Success!")
        
        print("\n✅ All endpoints accessible!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🧪 Testing Frontend API Access...")
    print("=" * 50)
    
    if test_frontend_proxy_access():
        print("\n" + "=" * 50)
        print("✅ All APIs accessible from frontend!")
        print("\nThe issue might be:")
        print("1. Frontend not properly logged in")
        print("2. Token not being sent correctly")
        print("3. JavaScript error in the frontend")
        print("\nTry:")
        print("1. Open browser DevTools (F12)")
        print("2. Go to Console tab")
        print("3. Look for any error messages")
        print("4. Go to Network tab and check if requests are being made")
    else:
        print("\n❌ API access test failed.")

if __name__ == "__main__":
    main() 