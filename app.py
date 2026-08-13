from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__, template_folder='.')

def search_olx(query, max_price):
    formatted_query = query.lower().strip().replace(' ', '-')
    url = f"https://www.olx.pl/oferty/q-{formatted_query}/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.select('div[data-testid="l-card"]')
            
            results = []
            for card in cards:
                title_elem = card.select_one('h6')
                price_elem = card.select_one('p[data-testid="ad-price"]')
                link_elem = card.select_one('a')
                img_elem = card.select_one('img')
                location_elem = card.select_one('p[data-testid="location-date"]')
                
                if title_elem and price_elem and link_elem:
                    title = title_elem.text.strip()
                    price_text = price_elem.text.strip()
                    
                    # Czyszczenie ceny do samej liczby
                    price_digit = re.sub(r'[^\d]', '', price_text)
                    if not price_digit:
                        continue
                    price = float(price_digit)
                    
                    # Filtrowanie tylko okazji poniżej maksymalnej ceny
                    if price <= max_price:
                        link = link_elem.get('href', '')
                        if link.startswith('/'):
                            link = f"https://www.olx.pl{link}"
                            
                        photo = img_elem.get('src', '') if img_elem else ''
                        if not photo or 'data:image' in photo:
                            photo = 'https://via.placeholder.com/300x400?text=OLX+Okazja'
                            
                        location = location_elem.text.strip() if location_elem else 'OLX Polska'
                        
                        results.append({
                            'title': title,
                            'price': price,
                            'url': link,
                            'photo': photo,
                            'location': location
                        })
            return results
        return []
    except Exception as e:
        print(f"Błąd podczas pobierania OLX: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_tracker():
    query = request.form.get('query')
    price_raw = request.form.get('price', '0').replace(',', '.')
    max_price = float(price_raw)
    
    offers = search_olx(query, max_price)
    return render_template('index.html', offers=offers, query=query, max_price=max_price)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
