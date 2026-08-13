from flask import Flask, render_template, request
import requests

app = Flask(__name__, template_folder='.')

def search_vinted(query, max_price):
    """
    Funkcja łącząca się z API Vinted w celu wyciągnięcia ofert
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }

    # Sesja HTTP wymagana przez Vinted do pobrania ciasteczka sesyjnego
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        # Krok 1: Wywołanie strony głównej po token/session cookie
        session.get("https://www.vinted.pl")
        
        # Krok 2: Zapytanie do wyszukiwarki Vinted
        url = f"https://www.vinted.pl/api/v2/catalog/items?search_text={query}&price_to={max_price}&order=newest_first"
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            results = []
            for item in items:
                title = item.get('title')
                price = float(item.get('price', 0))
                item_url = item.get('url')
                
                results.append({
                    'title': title,
                    'price': price,
                    'url': item_url
                })
            return results
        else:
            print(f"Błąd API Vinted: Status {response.status_code}")
            return []
    except Exception as e:
        print(f"Błąd podczas połączenia z Vinted: {e}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_tracker():
    query = request.form.get('query')
    max_price = float(request.form.get('price'))
    
    offers = search_vinted(query, max_price)
    
    if not offers:
        return f"""
        <body style="background:#0f172a; color:white; font-family:sans-serif; padding:20px;">
            <h2>Brak nowych ofert lub Vinted tymczasowo zablokowało zapytanie.</h2>
            <p>Szukano: <b>{query}</b> do <b>{max_price} PLN</b></p>
            <a href="/" style="color:#00d2ff;">← Wróć do formularza</a>
        </body>
        """
    
    # Tworzenie czytelnej listy wyników
    html_results = f"""
    <body style="background:#0f172a; color:white; font-family:sans-serif; padding:20px;">
        <h2 style="color:#00d2ff;">Znaleziono {len(offers)} ofert na Vinted!</h2>
        <ul style="line-height: 1.8;">
    """
    for item in offers[:10]: # Pokazujemy pierwsze 10
        html_results += f"<li><b>{item['title']}</b> - {item['price']} PLN | <a href='{item['url']}' target='_blank' style='color:#00d2ff;'>Zobacz ogłoszenie</a></li>"
    
    html_results += "</ul><br><a href='/' style='color:#00d2ff;'>← Wróć do formularza</a></body>"
    
    return html_results

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
