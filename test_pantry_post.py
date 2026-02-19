import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_pantry_post():
    # 1. Login to get token (using temporary user from previous tests or creating one)
    user_data = {"email": "test_pantry@example.com", "password": "password123"}
    requests.post(f"{BASE_URL}/register", json=user_data)
    login_res = requests.post(f"{BASE_URL}/login", json=user_data)
    token = login_res.json().get('access_token')
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 2. Test POST /pantry
    # Send a small list of IDs
    payload = {"ingredient_ids": [1, 2, 3]}
    print(f"Sending POST to /pantry with payload: {payload}")
    try:
        res = requests.post(f"{BASE_URL}/pantry", headers=headers, json=payload, timeout=5)
        print(f"Response: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"Error during POST: {e}")

if __name__ == "__main__":
    test_pantry_post()
