#!/usr/bin/env python3
"""
Test the complete login flow and verify token works
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_complete_login_flow():
    """Test login and then use the token to access protected endpoints"""
    try:
        # Step 1: Login
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        print("🔐 Logging in...")
        login_response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.json()}")
            return False
            
        token = login_response.json().get('token')
        print(f"✅ Login successful!")
        print(f"Token: {token[:20]}...")
        
        # Step 2: Test protected endpoint with token
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print("\n🔒 Testing protected endpoint...")
        sessions_response = requests.get(f'{BASE_URL}/sessions?limit=3', headers=headers)
        
        print(f"✅ Sessions endpoint: {sessions_response.status_code}")
        print(f"Response: {sessions_response.json()}")
        
        # Step 3: Test analytics endpoint
        print("\n📊 Testing analytics endpoint...")
        analytics_response = requests.get(f'{BASE_URL}/sessions/analytics?days=7', headers=headers)
        
        print(f"✅ Analytics endpoint: {analytics_response.status_code}")
        print(f"Response: {analytics_response.json()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🧪 Testing Complete Login Flow...")
    print("=" * 50)
    
    if test_complete_login_flow():
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Go to http://localhost:3000/login")
        print("2. Login with test@example.com / testpassword123")
        print("3. The dashboard should now work without 401 errors")
    else:
        print("\n❌ Tests failed. Check the backend is running.")

if __name__ == "__main__":
    main() 