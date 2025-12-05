import requests
from bs4 import BeautifulSoup

def test_rokomari(query):
    url = f"https://www.rokomari.com/search?term={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # I need to find the book items. 
    # Usually they are in a div with a specific class.
    # Let's look for divs that contain "TK."
    
    books = []
    # Try to find book wrappers. 
    # Based on common practices, it might be 'book-item', 'product-item', etc.
    # Let's print all div classes to see what's available.
    
    # print("Classes found:")
    # classes = set()
    # for div in soup.find_all('div', class_=True):
    #     classes.update(div['class'])
    # print(classes)

    # Let's try to find a container that looks like a book list.
    # The markdown showed "Showing 1 to 60 of 526 items".
    # This text is likely in a pagination or info bar.
    
    # Look for links containing '/book/' and followed by a number
    import re
    book_links = soup.find_all('a', href=re.compile(r'/book/\d+/'))
    
    print(f"Found {len(book_links)} book links.")
    
    if book_links:
        # Take the first one and traverse up to find the container
        link = book_links[0]
        print(f"Link: {link['href']}")
        parent = link.parent
        while parent and parent.name != 'body':
            if parent.name == 'div' and parent.get('class'):
                print(f"Parent div class: {parent.get('class')}")
                # If we find a class that looks like a wrapper, print it
                if 'book-list-wrapper' in parent.get('class') or 'product-item' in str(parent.get('class')):
                     print("Found potential wrapper!")
                     print(parent.prettify()[:500])
                     break
            parent = parent.parent
            
    # Find price elements and traverse up
    prices = soup.find_all('strike', class_='original-price')
    if prices:
        print(f"Found {len(prices)} original prices.")
        price_el = prices[0]
        parent = price_el.parent
        while parent and parent.name != 'body':
            if parent.name == 'div' and parent.get('class'):
                print(f"Price Parent div class: {parent.get('class')}")
                if 'book-text-area' in parent.get('class') or 'book-list-wrapper' in str(parent.get('class')):
                     print("Found book text area!")
                     print(parent.prettify()[:500])
                     # Go up one more to find the full card
                     card = parent.parent
                     print(f"Card tag: {card.name}")
                     print(f"Card class: {card.get('class')}")
                     # Check if there is an image
                     img = card.find('img')
                     if img:
                         print(f"Image src: {img.get('src')}")
                     
                     # Check for link
                     link = card.find('a')
                     if link:
                         print(f"Book Link: {link.get('href')}")
                     break
            parent = parent.parent

def test_wafilife(query):
    url = f"https://www.wafilife.com/?s={query}&post_type=product"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("Testing Wafilife...")
    import re
    # Look for grid container
    grids = soup.find_all('div', class_=lambda c: c and 'grid' in c)
    print(f"Found {len(grids)} grid divs.")
    
    for i, grid in enumerate(grids):
        # Check if it contains product links
        links = grid.find_all('a', href=re.compile(r'/pd/\d+'))
        if len(links) > 0:
            print(f"Grid {i} contains {len(links)} product links.")
            # Print the first item in this grid
            first_item = links[0].parent
            while first_item and first_item.parent != grid:
                first_item = first_item.parent
            
            if first_item:
                print(f"First item in Grid {i}:")
                print(first_item.prettify()[:500])
            break
            
    # Also look for price
    prices = soup.find_all(string=re.compile(r'৳'))
    print(f"Found {len(prices)} price elements.")
    if prices:
        print(f"Sample price: {prices[0]}")
        print(f"Parent of price: {prices[0].parent}")

if __name__ == "__main__":
    # test_rokomari("humayun ahmed")
    test_wafilife("humayun ahmed")
