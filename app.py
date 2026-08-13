from flask import Flask, render_template, request, jsonify
import requests
import urllib.parse

app = Flask(__name__, template_folder='.')

# Słownik kategorii OLX z ich ID
CATEGORIES = {
    "all": "Wszystkie kategorie",
    "99": "Elektronika",
    "5": "Motoryzacja",
    "87": "Moda / Odzież",
    "89": "Dom i Ogród",
    "751": "Sport i Hobby",
    "3": "Dla Dzieci",
    "88": "Muzyka i Edukacja"
}

@app.route('/api/cities')
def suggest_cities():
    """ Endpoint do autouzupełniania miast przy wpisywaniu """
    text = request.args.get('q', '').strip()
    if not text or len(text) < 2:
        return jsonify([])
    
    url = f"https://www.olx.pl/api/v1/geo-encoder/cities/?q={urllib.parse.quote(text)}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json().get('data', [])
            suggestions = []
            for city in data[:7]: # max 7 podpowiedzi
                city_id = city.get('id')
                name = city.get('name')
                region = city.get('region', {}).get('name', '')
                label = f"{name}, {region}" if region else name
                suggestions.append({'id': city_id, 'name': name, 'label': label})
            return jsonify(suggestions)
    except Exception as e:
        print(f"Błąd miasta: {e}")
    return jsonify([])

def search_olx(query, price_from, price_to, category_id, city_id, distance, sort_by):
    params = {
        "offset": 0,
        "limit": 40,
        "query": query,
    }
    
    if price_from:
        params["filter_float_price:from"] = price_from
    if price_to:
        params["filter_float_price:to"] = price_to
    if category_id and category_id != "all":
        params["category_id"] = category_id
    if city_id:
        params["city_id"] = city_id
    if distance and int(distance) > 0:
        params["distance"] = distance
    if sort_by:
        params["sort_by"] = sort_by  # created_at:desc, price:asc, price:desc

    url = "https://www.olx.pl/api/v1/offers/?" + urllib.parse.urlencode(params)
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
                
                # Wyciąganie ceny
                price = "Za darmo / Zamiana"
                for p in item.get('params', []):
                    if p.get('key') == 'price':
                        val = p.get('value', {}).get('value')
                        if val is not None:
                            price = f"{val} zł"
                        break
                
                # Zdjęcie
                photos = item.get('photos', [])
                photo_url = 'https://via.placeholder.com/300x400?text=Brak+Zdjecia'
                if photos:
                    photo_url = photos[0].get('link', '').replace('{width}', '600').replace('{height}', '400')
                
                # Lokalizacja i data
                location_data = item.get('location', {})
                city_name = location_data.get('city', {}).get('name', 'Polska')
                created_time = item.get('created_time', '')[:10]
                
                results.append({
                    'title': title,
                    'price': price,
                    'url': item_url,
                    'photo': photo_url,
                    'location': city_name,
                    'date': created_time
                })
            return results
        return []
    except Exception as e:
        print(f"Błąd OLX Search: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query', '')
    price_from = request.form.get('price_from', '')
    price_to = request.form.get('price_to', '')
    category_id = request.form.get('category_id', 'all')
    city_name = request.form.get('city_name', '')
    city_id = request.form.get('city_id', '')
    distance = request.form.get('distance', '0')
    sort_by = request.form.get('sort_by', 'created_at:desc')
    
    offers = search_olx(query, price_from, price_to, category_id, city_id, distance, sort_by)
    
    return render_template('index.html', 
                           offers=offers, 
                           categories=CATEGORIES,
                           query=query,
                           price_from=price_from,
                           price_to=price_to,
                           category_id=category_id,
                           city_name=city_name,
                           city_id=city_id,
                           distance=distance,
                           sort_by=sort_by)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
