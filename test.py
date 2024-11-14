import requests

# Replace with your actual API key and organization ID
API_KEY = "ed_o2j5dhd367l4je2k0sczkw9ixlfjxfqowznkz0437rjk6a8gd3gmlpia1mqt30u7"
ORGANIZATION_ID = "f73cdf90-8224-11ef-9338-8dff4b34f2dc"
BASE_URL = f"https://api.edenic.io/api/v1/device/{ORGANIZATION_ID}"

# Test different header formats
headers_with_bearer = {"Authorization": "Bearer " + API_KEY}
headers_without_bearer = {"Authorization": API_KEY}

def fetch_devices(headers):
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code == 200:
        print("Devices fetched successfully:", response.json())
    else:
        print("Failed to fetch devices:", response.status_code, response.text)

# Try fetching with both header formats
print("Testing with 'Bearer' prefix:")
fetch_devices(headers_with_bearer)

print("\nTesting without 'Bearer' prefix:")
fetch_devices(headers_without_bearer)
    