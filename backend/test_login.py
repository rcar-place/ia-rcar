import urllib.request
import urllib.error
import json

url = "http://localhost:8000/api/v1/auth/login"
data = json.dumps({"username": "joao", "password": "2468"}).encode("utf-8")
headers = {"Content-Type": "application/json"}

req = urllib.request.Request(url, data=data, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTPError Status:", e.code)
    print("Body:", e.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
