from flask import Flask, render_template, request
import requests
import urllib.parse

app = Flask(__name__, template_folder='.')

def search_vinted(query, max_price):
    # Enkodowanie frazy (np. "Jordan 1" -> "Jordan%201")
    safe_query = urllib.parse.quote(query)
    
    session = requests.Session()
    
    # Rozbudowane nagłówki udające prawdziwą aplikację/przeglądarkę
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.vinted.pl",
        "Referer": f"https://www.vinted.pl/catalog?search_text={safe_query}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        # Krok 1: Wejście na stronę główną w celu pobrania ciasteczek CSRF/Session
        session.get("https://www.vinted.pl", headers=headers, timeout=10)
        
        # Krok 2: Strzał do API po oferty
        url = f"https://www.vinted.pl/api/v2/catalog/items?search_text={safe_query}&price_to={max_price}&order=newest_first"
        response = session.get(url, headers=headers, timeout=10)
        
        print(f"Status Vinted: {response.status_code}") # Log dla Rendera

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            results = []
            for item in items:
                title = item.get('title', 'Brak tytułu')
                price = item.get('price', '0')
                item_url = item.get('url', '#')
                
                # Zdjęcie
                photo_data = item.get('photo', {})
                photo_url = photo_data.get('url', 'https://via.placeholder.com/300x400?text=Brak+Zdjecia') if photo_data else 'https://via.placeholder.com/300x400?text=Brak+Zdjecia'
                
                # Dodatkowe dane
                status = item.get('status', 'Brak informacji')
                user_data = item.get('user', {})
                user_name = user_data.get('login', 'Nieznany') if user_data else 'Nieznany'
                size = item.get('size_title', '')
                brand = item.get('brand_title', '')
                
                results.append({
                    'title': title,
                    'price': price,
                    'url': item_url,
                    'photo': photo_url,
                    'status': status,
                    'user': user_name,
                    'size': size,
                    'brand': brand
                })
            return results
        else:
            return []
            
    except Exception as e:
        print(f"Błąd połączenia z Vinted: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_tracker():
    query = request.form.get('query')
    
    # Przekształcenie kwoty (np. z przecinkiem "1000,0" na kropkę "1000.0")
    price_raw = request.form.get('price', '0').replace(',', '.')
    max_price = float(price_raw)
    
    offers = search_vinted(query, max_price)
    return render_template('index.html', offers=offers, query=query, max_price=max_price)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
