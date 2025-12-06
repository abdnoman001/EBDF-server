import requests

def test_image_url_construction():
    # ID from previous investigation: 111644
    product_id = "111644"
    
    urls_to_test = [
        f"https://baatighar.com/web/image/product.template/{product_id}/image_128",
        f"https://baatighar.com/web/image/product.template/{product_id}/image_256",
        f"https://baatighar.com/web/image/product.template/{product_id}/image_1024",
        f"https://baatighar.com/web/image/product.product/{product_id}/image_128",
    ]
    
    for url in urls_to_test:
        print(f"Testing {url}...")
        try:
            response = requests.head(url)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Content-Type:", response.headers.get('Content-Type'))
                print("Content-Length:", response.headers.get('Content-Length'))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_image_url_construction()
