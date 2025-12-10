import requests
from bs4 import BeautifulSoup

def debug_rokomari_images(query):
    print(f"Scraping Rokomari for: {query}")
    url = f"https://www.rokomari.com/search?term={query}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            items = soup.find_all('div', class_='book-text-area')
            
            print(f"Found {len(items)} items.")
            
            for i, item in enumerate(items[:3]):
                print(f"--- Item {i} ---")
                card = item.parent
                print(f"Card tag: {card.name}")
                print(f"Card classes: {card.get('class')}")
                
                href = ""
                if card.name == 'a':
                    href = card.get('href', '')
                else:
                    a_tag = card.find('a')
                    if a_tag:
                        href = a_tag.get('href', '')
                
                print(f"Href: {href}")
                
                img_tag = card.find('img')
                if img_tag:
                    print("Img tag found:")
                    print(img_tag)
                    print("src:", img_tag.get('src'))
                    print("data-src:", img_tag.get('data-src'))
                    print("class:", img_tag.get('class'))
                else:
                    print("No img tag found in parent.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_rokomari_images("Sajid")
