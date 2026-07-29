#!/usr/bin/env python3
"""
Test registration endpoint locally
"""

import requests
import json

# Test the registration endpoint
API_URL = "http://localhost:8000"  # Change to your Railway URL for remote test

def test_registration():
    """Test user registration"""
    
    print("Testing registration endpoint...")
    print(f"API URL: {API_URL}")
    print()
    
    # Test data
    test_user = {
        "email": "test_admin@oddsifylabs.com",
        "membership": "TERMINAL"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        # Try to parse as JSON
        try:
            data = response.json()
            print("✅ Response is valid JSON:")
            print(json.dumps(data, indent=2))
            
            if response.status_code == 200:
                print("\n✅ REGISTRATION SUCCESSFUL!")
                print(f"Username: {data.get('username', 'N/A')}")
                print(f"Email: {data.get('email', 'N/A')}")
            else:
                print(f"\n⚠️  Registration returned status {response.status_code}")
                print(f"Detail: {data.get('detail', 'N/A')}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Response is NOT valid JSON: {e}")
            print(f"Response text: {response.text[:200]}")
            print("\nThis is likely an HTML error page (Internal Server Error)")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("\nIs the server running?")
        print("For Railway: Use your Railway URL instead of localhost:8000")
        
    except requests.exceptions.Timeout as e:
        print(f"❌ Request timed out: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_registration()
