from flask import Flask, render_template, redirect, url_for, session
import requests

app = Flask(__name__, template_folder='.')
app.secret_key = 'super_tajny_kluczyk_sesji'

def get_freebies():
    """ Pobiera gry, które są w tym momencie w 100% darmowe """
    url = "https://www.cheapshark.com/api/1.0/deals?upperPrice=0"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            freebies = []
            for item in data[:6]:
                freebies.append({
                    'title': item.get('title'),
                    'thumb': item.get('thumb'),
                    'url': f"https://www.cheapshark.com/redirect?dealID={item.get('dealID')}"
                })
            return freebies
    except Exception as e:
        print(f"Błąd freebies: {e}")
    return []

def get_top_deals():
    """ Pobiera 10 najgorętszych promocji z największym rabatem """
    url = "https://www.cheapshark.com/api/1.0/deals?sortBy=Savings&pageSize=10"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            deals = []
            stores = {"1": "Steam", "7": "GOG", "11": "Humble", "25": "Epic Games"}
            for item in data:
                deals.append({
                    'title': item.get('title'),
                    'price': item.get('salePrice'),
                    'old_price': item.get('normalPrice'),
                    'store': stores.get(item.get('storeID'), 'Sklep'),
                    'thumb': item.get('thumb'),
                    'url': f"https://www.cheapshark.com/redirect?dealID={item.get('dealID')}"
                })
            return deals
    except Exception as e:
        print(f"Błąd top deals: {e}")
    return []

@app.route('/')
def home():
    freebies = get_freebies()
    top_deals = get_top_deals()
    return render_template('index.html', freebies=freebies, top_deals=top_deals)

# Przykład integracji logowania Steam OpenID
@app.route('/login/steam')
def login_steam():
    # Przekierowanie do oficjalnego logowania Steam OpenID
    steam_openid_url = "https://steamcommunity.com/openid/login"
    # Tutaj przesyła się parametry autoryzacji
    return redirect(steam_openid_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
