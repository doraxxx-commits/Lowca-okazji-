from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__, template_folder='.')

# Główna strona ze skryptem HTML
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint odbierający dane z formularza strony
@app.route('/add', methods=['POST'])
def add_tracker():
    query = request.form.get('query')
    max_price = int(request.form.get('price'))
    
    print(f"Rozpoczynam szukanie: {query} do {max_price} zł...")
    
    # Przykładowy test wyszukiwania na OLX
    search_url = f"https://www.olx.pl/oferty/q-{query.replace(' ', '-')}/"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}
    
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        offers = soup.select('div[data-testid="l-card"]')
        
        found_count = 0
        for offer in offers:
            title_elem = offer.select_one('h6')
            price_elem = offer.select_one('p[data-testid="ad-price"]')
            
            if title_elem and price_elem:
                title = title_elem.text.strip()
                price_digit = re.sub(r'[^\d]', '', price_elem.text)
                
                if price_digit:
                    price = int(price_digit)
                    if price <= max_price:
                        print(f" [OKAZJA] {title} - {price} PLN")
                        found_count += 1
                        
        return f"Zaakceptowano! Znaleziono wstępnie {found_count} ofert w budżecie."
    
    return "Nie udało się pobrać danych ze strony."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
