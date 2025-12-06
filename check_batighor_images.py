import requests
from bs4 import BeautifulSoup

def check_batighor_images():
    url = "https://baatighar.com/shop?search=humayun"
    print(f"Fetching {url}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    items = soup.find_all('div', class_='card h-100')
    print(f"Found {len(items)} items.")
    
    for i, item in enumerate(items[:3]):
        print(f"--- Item {i} ---")
        img_container = item.find('div', class_='image-container')
        if img_container:
            img = img_container.find('img')
            if img:
                print("Attributes:", img.attrs.keys())
                print("data-src:", img.get('data-src'))
                print("src starts with:", img.get('src')[:30] if img.get('src') else "None")
                print("src length:", len(img.get('src')) if img.get('src') else 0)

if __name__ == "__main__":
    check_batighor_images()
