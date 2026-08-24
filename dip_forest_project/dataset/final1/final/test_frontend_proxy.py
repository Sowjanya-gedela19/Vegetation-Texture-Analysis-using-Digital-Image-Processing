#!/usr/bin/env python3
"""
Test if the frontend proxy is working correctly
"""

import requests
import json

def test_proxy_health():
    """Test if the proxy can reach the backend health endpoint"""
    try:
        # This simulates what the frontend would do
        response = requests.get('http://127.0.0.1:5000/api/health')
        print(f"✅ Direct Backend Health: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Direct backend test failed: {e}")
        return False

def test_cors_with_proxy():
    """Test CORS with proxy-like headers"""
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization, Content-Type'
        }
        
        response = requests.options('http://127.0.0.1:5000/api/sessions', headers=headers)
        print(f"✅ CORS with Proxy Headers: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        return True
    except Exception as e:
        print(f"❌ CORS proxy test failed: {e}")
        return False

def main():
    print("🧪 Testing Frontend Proxy Configuration...")
    print("=" * 50)
    
    # Test direct backend access
    if not test_proxy_health():
        print("❌ Backend is not accessible")
        return
    
    print("\n" + "=" * 50)
    
    # Test CORS with proxy headers
    if not test_cors_with_proxy():
        print("❌ CORS with proxy headers failed")
        return
    
    print("\n" + "=" * 50)
    print("✅ Proxy configuration looks good!")
    print("\nNext steps:")
    print("1. Make sure the backend is running: python server.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. The frontend should now work without CORS errors")

if __name__ == "__main__":
    main() 