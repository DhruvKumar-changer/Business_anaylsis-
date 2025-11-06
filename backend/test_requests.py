import requests
import json

BASE_URL = "http://localhost:5000"

# Test 1: Home
print("Testing Home...")
response = requests.get(f"{BASE_URL}/")
print(response.json())

# Test 2: Upload (manual - file chahiye)
print("\nUpload endpoint ready")

# Test 3: Analyze (after upload)
print("\nTesting Analyze...")
analyze_data = {
    'filename': 'sample_business_data.csv',
    'business_name': 'Test Store',
    'industry': 'Retail',
    'business_type': 'Startup'
}
response = requests.post(f"{BASE_URL}/analyze", json=analyze_data)
print(response.json())

# Test 4: Recommendations
print("\nTesting Recommendations...")
rec_data = {
    'kpis': {
        'total_revenue': 500000,
        'net_profit': 100000,
        'profit_margin': 20
    }
}
response = requests.post(f"{BASE_URL}/recommendations", json=rec_data)
print(response.json())

# # Test 5: History
# print("\nTesting History...")
# response = requests.get(f"{BASE_URL}/history/1")
# print(response.json())