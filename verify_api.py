import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_index():
    print("Testing / ...")
    resp = requests.get(f"{BASE_URL}/")
    if resp.status_code == 200:
        print("Success: Dashboard loaded.")
    else:
        print(f"Failed: {resp.status_code}")

def test_dynamic_endpoints():
    print("Testing /api/dashboard_stats ...")
    resp = requests.get(f"{BASE_URL}/api/dashboard_stats")
    if resp.status_code == 200:
        print(f"Success: Stats: {resp.json()}")
    else:
        print(f"Failed: {resp.status_code}")

    print("Testing /api/weather_trends ...")
    resp = requests.get(f"{BASE_URL}/api/weather_trends")
    if resp.status_code == 200:
        print(f"Success: History length: {len(resp.json())}")
    else:
        print(f"Failed: {resp.status_code}")

def test_fetch_data():
    print("Testing /fetch_satellite_data ...")
    payload = {
        "region": "California",
        "from_date": "2023-01-01",
        "to_date": "2023-01-05"
    }
    resp = requests.post(f"{BASE_URL}/fetch_satellite_data", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success: Found {data.get('firms_count')} hotspots.")
    else:
        print(f"Failed: {resp.status_code} - {resp.text}")

def test_predict():
    print("Testing /predict (High Risk with SMS) ...")
    payload = {
        "temperature": 45,
        "humidity": 10,
        "wind_speed": 40,
        "rainfall": 0,
        "ndvi": 0.9,
        "historical_fire": 1,
        "phone_number": "8591556205"
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success: Risk Level: {data.get('risk_level')}, Confidence: {data.get('confidence')}")
        print(f"SMS Status: {data.get('sms_status')}")
        print(f"Telegram Status: {data.get('telegram_status')}")
    else:
        print(f"Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    try:
        test_index()
        test_dynamic_endpoints()
        test_fetch_data()
        test_predict()
    except Exception as e:
        print(f"Error during testing: {e}")
