import requests

url = "https://data.europarl.europa.eu/api/v2/datasets"

response = requests.get(url)

print("STATUS:", response.status_code)
print("DATA SAMPLE:", response.text[:500])