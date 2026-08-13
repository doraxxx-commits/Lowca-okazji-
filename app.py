from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

app = Flask(__name__, template_folder='.')

CATEGORIES = {
    "all": "Wszystkie kategorie",
    "elektronika": "Elektronika",
    "motoryzacja": "Motoryzacja",
    "moda": "Moda / Odzież",
    "dom-ogrod": "Dom i Ogród",
    "sport-hobby": "Sport i Hobby"
}

def search_olx_html(query, price_from, price_to, category_slug, city_slug):
    # Budowanie adresu URL dokładnie tak, jak w przeglądarce OLX
    formatted_query = query.lower().strip().replace(' ', '-')
    
    # Baza URL zależna od kategorii i miasta
    base_path = "oferty"
    if category_slug and category_slug != "all":
        base_path = category_slug
        
    if city_slug:
        formatted_city = city_slug.lower().strip().replace(' ', '-')
        url = f"https://www.olx.pl/{base_path}/{formatted_city}/q-{formatted_query}/"
    else:
        url = f"https://www.olx.pl/{base_path}/q-{formatted_query}/"
    
    # Parametry filtrowania ceny
    params = {}
    if price_from:
        params['search[filter_float_price:from]'] = price_from
    if price_to:
        params['search[filter_float_price:to]'] = price_to
        
    if params:
        url += "?" + urllib.parse.urlencode(params)
        
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
        "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8"
    }
    
    print(f"Pobieranie URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # OLX ukrywa dane w obiekcie JSON script window.__PRERENDERED_STATE__ lub w kartach
            cards = soup.select('div[data-testid="l-card"]')
            results = []
            
            for card in cards:
                title_elem = card.select_one('h6, h4')
                price_elem = card.select_one('p[data-testid="ad-price"], font')
                link_elem = card.select_one('a')
                img_elem = card.select_one('img')
                loc_date_elem = card.select_one('p[data-testid="location-date"]')
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    price = price_elem.text.strip() if price_elem else "Zamiana / Darmo"
                    
                    link = link_elem.get('href', '')
                    if link.startswith('/'):
                        link = f"https://www.olx.pl{link}"
                        
                    photo = ''
                    if img_elem:
                        photo = img_elem.get('src', '') or img_elem.get('data-src', '')
                    if not photo or 'data:image' in photo:
                        photo = 'https://via.placeholder.com/300x400?text=OLX'
                        
                    loc_date = loc_date_elem.text.strip() if loc_date_elem else 'Polska'
                    
                    results.append({
                        'title': title,
                        'price': price,
                        'url': link,
                        'photo': photo,
                        'location': loc_date
                    })
            return results
        else:
            print(f"Błąd HTTP OLX: {response.status_code}")
            return []
    except Exception as e:
        print(f"Błąd podczas połączenia: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query', '').strip()
    price_from = request.form.get('price_from', '').strip()
    price_to = request.form.get('price_to', '').strip()
    category_slug = request.form.get('category_slug', 'all')
    city_name = request.form.get('city_name', '').strip()
    
    # Jeśli użytkownik wpisał cenę tylko w pierwsze pole, traktujemy ją jako 'do' (maksymalna)
    if price_from and not price_to:
        price_to = price_from
        price_from = ""
    
    offers = search_olx_html(query, price_from, price_to, category_slug, city_name)
    
    return render_template('index.html', 
                           offers=offers, 
                           categories=CATEGORIES,
                           query=query,
                           price_from=price_from,
                           price_to=price_to,
                           category_slug=category_slug,
                           city_name=city_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
