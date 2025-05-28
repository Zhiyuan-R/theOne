"""
Test authentication endpoints
"""
import requests
import json

API_BASE_URL = "http://localhost:8000/api"

def test_registration():
    """Test user registration"""
    print("🔐 Testing Registration...")
    
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json=user_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Registration successful!")
        return True
    elif response.status_code == 400:
        print("⚠️  User already exists (this is expected if running multiple times)")
        return True
    else:
        print("❌ Registration failed!")
        return False

def test_login():
    """Test user login"""
    print("\n🔑 Testing Login...")
    
    # Use form data for OAuth2
    login_data = {
        "username": "test@example.com",  # OAuth2 uses 'username' field
        "password": "testpassword123"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data=login_data  # Use data, not json for form data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful!")
        print(f"Access Token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print("❌ Login failed!")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\n🛡️  Testing Protected Endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{API_BASE_URL}/profiles/me",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 404:
        print("✅ Authentication working! (Profile not found is expected)")
        return True
    elif response.status_code == 200:
        print("✅ Authentication working! Profile found.")
        return True
    else:
        print("❌ Authentication failed!")
        return False

def main():
    """Run authentication tests"""
    print("🧪 Testing Authentication Flow")
    print("=" * 40)
    
    # Test registration
    if not test_registration():
        return
    
    # Test login
    token = test_login()
    if not token:
        return
    
    # Test protected endpoint
    test_protected_endpoint(token)
    
    print("\n" + "=" * 40)
    print("🎉 Authentication tests completed!")
    print("You should now be able to login through the web interface.")

if __name__ == "__main__":
    main()
