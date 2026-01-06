import requests
import json

BASE_URL = "http://localhost:5000"

print("Testing Backend API...")
print("=" * 60)

# Test 1: Health check
print("\n[1/4] Testing /api/health")
try:
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Create user
print("\n[2/4] Testing POST /api/users")
try:
    data = {"name": "Test User", "age": 30, "condition": "healthy"}
    resp = requests.post(f"{BASE_URL}/api/users", json=data)
    print(f"Status: {resp.status_code}")
    user_data = resp.json()
    print(f"Response: {user_data}")
    user_id = user_data.get('user_id')
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Start session
print("\n[3/4] Testing POST /api/sessions/start")
try:
    data = {"user_id": user_id}
    resp = requests.post(f"{BASE_URL}/api/sessions/start", json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Get users
print("\n[4/4] Testing GET /api/users")
try:
    resp = requests.get(f"{BASE_URL}/api/users")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ API tests complete!")
