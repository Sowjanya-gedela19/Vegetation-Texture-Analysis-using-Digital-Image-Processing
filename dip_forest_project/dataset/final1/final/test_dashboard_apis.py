#!/usr/bin/env python3
"""
Test all dashboard API endpoints exactly as the frontend does
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_dashboard_apis():
    """Test all dashboard API endpoints with proper authentication"""
    try:
        # Step 1: Login to get token
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        print("🔐 Logging in...")
        login_response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        token = login_response.json().get('token')
        print(f"✅ Login successful!")
        
        # Step 2: Set up headers like the frontend
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Step 3: Test each endpoint individually (like Promise.all)
        print("\n📊 Testing Analytics endpoint...")
        analytics_response = requests.get(f'{BASE_URL}/sessions/analytics?days=7', headers=headers)
        print(f"Analytics Status: {analytics_response.status_code}")
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print(f"Analytics Data: {json.dumps(analytics_data, indent=2)}")
        else:
            print(f"Analytics Error: {analytics_response.text}")
            return False
        
        print("\n🤖 Testing AI Suggestions endpoint...")
        ai_response = requests.get(f'{BASE_URL}/ai/suggestions', headers=headers)
        print(f"AI Status: {ai_response.status_code}")
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            print(f"AI Data: {json.dumps(ai_data, indent=2)}")
        else:
            print(f"AI Error: {ai_response.text}")
            return False
        
        print("\n📝 Testing Recent Sessions endpoint...")
        sessions_response = requests.get(f'{BASE_URL}/sessions?limit=3', headers=headers)
        print(f"Sessions Status: {sessions_response.status_code}")
        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()
            print(f"Sessions Data: {json.dumps(sessions_data, indent=2)}")
        else:
            print(f"Sessions Error: {sessions_response.text}")
            return False
        
        # Step 4: Test data processing (like the frontend does)
        print("\n🔧 Testing data processing...")
        try:
            # Process analytics data
            stats = {
                'totalStudyTime': analytics_data.get('summary', {}).get('total_time', 0),
                'sessionsThisWeek': analytics_data.get('summary', {}).get('total_sessions', 0),
                'averageFocusLevel': analytics_data.get('summary', {}).get('average_focus_level', 0),
                'subjectsCount': len(analytics_data.get('subject_breakdown', {}))
            }
            print(f"Processed Stats: {stats}")
            
            # Process AI insights
            insights = []
            if ai_data.get('suggestions'):
                insights.append({
                    'type': 'suggestion',
                    'title': 'Actionable Suggestions',
                    'content': ai_data['suggestions']
                })
            if ai_data.get('attention_areas'):
                insights.append({
                    'type': 'attention',
                    'title': 'Areas for Attention',
                    'content': ai_data['attention_areas']
                })
            if ai_data.get('motivation'):
                insights.append({
                    'type': 'motivation',
                    'title': 'Your Daily Motivation',
                    'content': [ai_data['motivation']]
                })
            print(f"Processed Insights: {insights}")
            
            print("✅ All data processing successful!")
            
        except Exception as e:
            print(f"❌ Data processing failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🧪 Testing Dashboard API Endpoints...")
    print("=" * 50)
    
    if test_dashboard_apis():
        print("\n" + "=" * 50)
        print("✅ All dashboard APIs working correctly!")
        print("\nThe issue might be in the frontend. Check:")
        print("1. Browser console for JavaScript errors")
        print("2. Network tab for failed requests")
        print("3. Make sure you're logged in with a valid token")
    else:
        print("\n❌ Dashboard API test failed.")

if __name__ == "__main__":
    main() 