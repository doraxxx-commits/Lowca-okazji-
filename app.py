from flask import Flask, render_template, request
import requests

app = Flask(__name__, template_folder='.')

def search_vinted(query, max_price):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }

    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Pobranie ciasteczek z Vinted
        session.get("https://www.vinted.pl")
        
        # Zapytanie do API Vinted z sortowaniem od najnowszych
        url = f"https://www.vinted.pl/api/v2/catalog/items?search_text={query}&price_to={max_price}&order=newest_first"
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            results = []
            for item in items:
                # Wyciągamy szczegółowe dane z przedmiotu
                title = item.get('title', 'Brak tytułu')
                price = item.get('price', '0')
                item_url = item.get('url', '#')
                
                # Zdjęcie główne
                photo_data = item.get('photo', {})
                photo_url = photo_data.get('url', 'https://via.placeholder.com/300x400?text=Brak+Zdjecia') if photo_data else 'https://via.placeholder.com/300x400?text=Brak+Zdjecia'
                
                # Stan przedmiotu (np. Nowy z metką, Bardzo dobry)
                status = item.get('status', 'Brak informacji')
                
                # Użytkownik
                user_data = item.get('user', {})
                user_name = user_data.get('login', 'Nieznany') if user_data else 'Nieznany'
                
                # Krótki opis/opis lub rozmiar
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
        print(f"Błąd: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_tracker():
    query = request.form.get('query')
    max_price = float(request.form.get('price', 0))
    
    offers = search_vinted(query, max_price)
    return render_template('index.html', offers=offers, query=query, max_price=max_price)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
