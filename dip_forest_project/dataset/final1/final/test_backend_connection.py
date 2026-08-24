#!/usr/bin/env python3
"""
Simple script to test if the StudySphere backend is running
"""

import requests
import sys

def test_backend():
    """Test if the backend is running and accessible"""
    try:
        # Test health endpoint
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend at http://127.0.0.1:5000")
        print("Make sure the backend is running with: python server.py")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

if __name__ == "__main__":
    print("Testing StudySphere Backend Connection...")
    success = test_backend()
    sys.exit(0 if success else 1) 