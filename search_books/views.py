from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import re

# Affiliate configuration
ROKOMARI_AFFILIATE_ID = "MY_AFFILIATE_ID" # Replace with actual ID

def get_rokomari_books(query):
    books = []
    try:
        url = f"https://www.rokomari.com/search?term={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.rokomari.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        print(f"Fetching Rokomari URL: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            items = soup.find_all('div', class_='book-text-area')
            print(f"Rokomari found {len(items)} items")
            for item in items:
                try:
                    # Title
                    title_el = item.find('h4', class_='book-title')
                    title = title_el.get_text(strip=True) if title_el else "Unknown Title"
                    
                    # Author
                    author_el = item.find('p', class_='book-author')
                    author = author_el.get_text(strip=True) if author_el else "Unknown Author"
                    
                    # Price
                    price_el = item.find('p', class_='book-price')
                    price_text = "0"
                    if price_el:
                        original_price_el = price_el.find('strike')
                        if original_price_el:
                            original_price_el.extract()
                        price_text = price_el.get_text(strip=True).replace('TK.', '').replace('TK', '').strip()
                    
                    # Parse price
                    try:
                        price = float(re.sub(r'[^\d.]', '', price_text))
                    except:
                        price = 0.0
                        
                    # Link and Image
                    card = item.parent
                    link = ""
                    image_url = ""
                    
                    if card.name == 'a':
                        href = card.get('href', '')
                        link = "https://www.rokomari.com" + href
                    else:
                        a_tag = card.find('a')
                        if a_tag:
                            href = a_tag.get('href', '')
                            link = "https://www.rokomari.com" + href
                        else:
                            href = ""
                    
                    # print(f"Rokomari Item: {title}, Href: {href}")

                    # Filter out non-book items (e.g. stationery, electronics)
                    # Books usually have /book/ in the URL, others have /product/ or /electronics/
                    if '/book/' not in href:
                        # print(f"Skipping non-book: {href}")
                        continue
                            
                    # Image
                    img_tag = card.find('img')
                    if img_tag:
                        # Prefer data-src as it usually contains the real image
                        image_url = img_tag.get('data-src', '')
                        if not image_url:
                            image_url = img_tag.get('src', '')
                            
                    # Add affiliate link
                    if link:
                        if '?' in link:
                            link += f"&ref={ROKOMARI_AFFILIATE_ID}"
                        else:
                            link += f"?ref={ROKOMARI_AFFILIATE_ID}"

                    books.append({
                        'title': title,
                        'author': author,
                        'price': price,
                        'price_text': f"Tk. {price}",
                        'product_url': link,
                        'image_url': image_url,
                        'source': 'Rokomari'
                    })
                except Exception as e:
                    print(f"Error parsing rokomari item: {e}")
                    continue
    except Exception as e:
        print(f"Error scraping Rokomari: {e}")
        
    return books

def get_wafilife_books(query):
    books = []
    try:
        # Use the internal API
        url = f"https://www.wafilife.com/api/search?keyword={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.wafilife.com/'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # The API returns a list of products directly
            if isinstance(data, list):
                for item in data:
                    try:
                        title = item.get('name', 'Unknown Title')
                        
                        # Authors
                        authors = item.get('authors', [])
                        author = authors[0] if authors else "Unknown Author"
                        
                        # Price
                        price_val = item.get('price')
                        price = float(price_val) if price_val is not None else 0.0
                        
                        # Check sale price
                        sale_prices = item.get('sale_price', [])
                        if sale_prices:
                            # Use the lowest sale price if available
                            try:
                                sale_price_val = sale_prices[0]
                                if sale_price_val is not None:
                                    sale_price = float(sale_price_val)
                                    if sale_price < price and sale_price > 0:
                                        price = sale_price
                            except:
                                pass
                                
                        # Image
                        image_info = item.get('image', {})
                        image_url = image_info.get('thumbnail', '') or image_info.get('original', '')
                        
                        # URL
                        slug = item.get('slug', '')
                        product_id = item.get('id', '')
                        link = f"https://www.wafilife.com/{slug}/pd/{product_id}"
                        
                        # Filter out invalid items
                        if price <= 0 or not slug or not product_id:
                            continue
                        
                        # Filter out non-books (must have authors)
                        if not authors:
                            continue

                        books.append({
                            'title': title,
                            'author': author,
                            'price': price,
                            'price_text': f"Tk. {price}",
                            'product_url': link,
                            'image_url': image_url,
                            'source': 'Wafilife'
                        })
                    except Exception as e:
                        print(f"Error parsing wafilife API item: {e}")
                        continue
    except Exception as e:
        print(f"Error scraping Wafilife: {e}")
        
    return books

def get_batighor_books(query):
    books = []
    try:
        url = f"https://baatighar.com/shop?search={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://baatighar.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all product cards
            items = soup.find_all('div', class_='card h-100')
            
            for item in items:
                try:
                    # Title
                    title_el = item.find('p', class_='card_title')
                    title = title_el.get_text(strip=True) if title_el else "Unknown Title"
                    
                    # Author
                    author_el = item.find('a', class_='card_contributer_title')
                    if not author_el:
                        # Skip items without author (likely non-books like notebooks, stationery)
                        continue
                    author = author_el.get_text(strip=True)
                    
                    # Price
                    price_container = item.find('span', class_='text-primary')
                    price_text = "0"
                    if price_container:
                        price_val = price_container.find('span', class_='oe_currency_value')
                        if price_val:
                            price_text = price_val.get_text(strip=True)
                    
                    try:
                        price = float(re.sub(r'[^\d.]', '', price_text))
                    except:
                        price = 0.0
                        
                    # Link
                    link = ""
                    product_id = ""
                    if title_el:
                        a_tag = title_el.find('a')
                        if a_tag:
                            href = a_tag.get('href', '')
                            link = "https://baatighar.com" + href
                            
                            # Extract ID from href (e.g. /shop/title-12345)
                            match = re.search(r'-(\d+)$', href)
                            if match:
                                product_id = match.group(1)
                            
                    # Image
                    image_url = ""
                    # Try to construct image URL from ID first (much lighter than base64)
                    if product_id:
                        image_url = f"https://baatighar.com/web/image/product.template/{product_id}/image_256"
                    else:
                        # Fallback to scraping
                        img_container = item.find('div', class_='image-container')
                        if img_container:
                            img_tag = img_container.find('img')
                            if img_tag:
                                src = img_tag.get('src', '')
                                # Avoid large base64 strings if possible
                                if src.startswith('data:image') and len(src) > 1000:
                                    # If we couldn't get ID, and image is huge base64, 
                                    # we might skip it or use a placeholder to avoid 5MB payloads
                                    # But for now, let's try to find data-src
                                    ds = img_tag.get('data-src')
                                    if ds:
                                        image_url = ds
                                else:
                                    image_url = src

                    books.append({
                        'title': title,
                        'author': author,
                        'price': price,
                        'price_text': f"Tk. {price}",
                        'product_url': link,
                        'image_url': image_url,
                        'source': 'Batighor'
                    })
                except Exception as e:
                    print(f"Error parsing batighor item: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error scraping Batighor: {e}")
        
    return books

@api_view(['GET'])
def search_books(request):
    query = request.GET.get('q', '')
    author = request.GET.get('author', '')
    store = request.GET.get('store', 'all') # 'all', 'rokomari', 'wafilife', 'batighor'
    
    if not query and not author:
        return Response([])
        
    # Combine query and author for better search results
    search_term = f"{query} {author}".strip()
    
    results = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        
        if store in ['all', 'rokomari']:
            futures.append(executor.submit(get_rokomari_books, search_term))
            
        if store in ['all', 'wafilife']:
            futures.append(executor.submit(get_wafilife_books, search_term))

        if store in ['all', 'batighor']:
            futures.append(executor.submit(get_batighor_books, search_term))
            
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Error in thread: {e}")
        
    # Sorting Logic
    # 1. Title match (High priority)
    # 2. Author match (Medium priority)
    # 3. Price (Low priority tie-breaker)
    
    query_lower = query.lower()
    author_lower = author.lower()
    
    for book in results:
        score = 0
        title_lower = book['title'].lower()
        book_author_lower = book['author'].lower()
        
        # Title Match
        if query_lower and query_lower in title_lower:
            score += 100
            # Exact match bonus
            if query_lower == title_lower:
                score += 50
                
        # Author Match
        if author_lower and author_lower in book_author_lower:
            score += 50
        elif query_lower and query_lower in book_author_lower:
             # If user searched for author name in main query
            score += 20
            
        book['score'] = score

    # Sort by score (descending), then price (ascending)
    results.sort(key=lambda x: (-x['score'], x['price']))
    
    return Response(results)
