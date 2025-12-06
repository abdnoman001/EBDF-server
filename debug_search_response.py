import requests
import json

def debug_search():
    url = "http://127.0.0.1:8000/api/search/"
    params = {
        "q": "anti gravity",
        "author": "",
        "store": "all"
    }
    print(f"Requesting {url} with params {params}...")
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        
        try:
            data = response.json()
            print(f"Type of data: {type(data)}")
            if isinstance(data, list):
                print(f"Number of items: {len(data)}")
                if len(data) > 0:
                    print("First item keys:", data[0].keys())
                    print("First item sample:", json.dumps(data[0], indent=2))
            else:
                print("Data is not a list!")
                print(data)
        except json.JSONDecodeError:
            print("Response is not JSON!")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_search()
