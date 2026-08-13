from flask import Flask, render_template, request
import requests

app = Flask(__name__, template_folder='.')

def search_olx(query, max_price):
    # Wykorzystujemy wewnętrzne API OLX zamiast wyciągania kodu HTML
    url = f"https://www.olx.pl/api/v1/offers/?offset=0&limit=40&query={query}&filter_float_price:to={max_price}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            
            results = []
            for item in items:
                title = item.get('title', 'Brak tytułu')
                item_url = item.get('url', '#')
                
                # Wyciąganie ceny z parametrów
                params = item.get('params', [])
                price = 0
                for p in params:
                    if p.get('key') == 'price':
                        value_data = p.get('value', {})
                        price = value_data.get('value', 0)
                        break
                
                # Wyciąganie zdjęcia
                photos = item.get('photos', [])
                photo_url = 'https://via.placeholder.com/300x400?text=OLX+Okazja'
                if photos:
                    photo_url = photos[0].get('link', '').replace('{width}', '600').replace('{height}', '400')
                
                # Lokalizacja
                location_data = item.get('location', {})
                city_data = location_data.get('city', {})
                location = city_data.get('name', 'Polska')
                
                results.append({
                    'title': title,
                    'price': price,
                    'url': item_url,
                    'photo': photo_url,
                    'location': location
                })
            return results
        else:
            print(f"Błąd API OLX: Status {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Błąd podczas połączenia z API OLX: {e}")
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
