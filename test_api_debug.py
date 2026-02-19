import requests

def test_api():
    try:
        # We need a token. Let's register a temp user.
        base_url = "http://127.0.0.1:5001"
        reg = requests.post(f"{base_url}/register", json={"email": "test@debug.com", "password": "password"})
        login = requests.post(f"{base_url}/login", json={"email": "test@debug.com", "password": "password"})
        token = login.json().get('access_token')
        
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{base_url}/ingredients", headers=headers)
        print(f"Status Code: {res.status_code}")
        data = res.json()
        print(f"Found {len(data)} ingredients via API.")
        if data:
            print(f"First 5: {data[:5]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
