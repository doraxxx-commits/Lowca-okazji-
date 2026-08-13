from flask import Flask, render_template, request, redirect, session, url_for
import requests
import urllib.parse

app = Flask(__name__, template_folder='.')
app.secret_key = 'super_tajny_kluczyk_game_claimer'

def get_freebies():
    """ Pobiera 100% darmowe gry """
    url = "https://www.cheapshark.com/api/1.0/deals?upperPrice=0"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            freebies = []
            for item in data[:6]:
                deal_id = item.get('dealID')
                freebies.append({
                    'title': item.get('title', 'Darmowa Gra'),
                    'thumb': item.get('thumb', 'https://via.placeholder.com/300x150?text=Darmowa+Gra'),
                    'url': f"https://www.cheapshark.com/redirect?dealID={deal_id}"
                })
            return freebies
    except Exception as e:
        print(f"Błąd freebies: {e}")
    
    # Awaryjne powiadomienie, jeśli brak darmowych gier 100% w tym momencie
    return [{
        'title': 'Gry z serii Epic Freebies / Steam Free Week',
        'thumb': 'https://via.placeholder.com/300x150?text=Sprawdzaj+Co+Czwartek',
        'url': 'https://store.epicgames.com/pl/free-games'
    }]

def get_top_deals():
    """ Pobiera top 10 promocji o największych rabatach """
    url = "https://www.cheapshark.com/api/1.0/deals?sortBy=Savings&pageSize=10"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            deals = []
            stores = {"1": "Steam", "7": "GOG", "11": "Humble", "25": "Epic Games"}
            for item in data:
                deal_id = item.get('dealID')
                deals.append({
                    'title': item.get('title', 'Gra w promocji'),
                    'price': item.get('salePrice', '0'),
                    'old_price': item.get('normalPrice', '0'),
                    'store': stores.get(str(item.get('storeID')), 'Sklep PC'),
                    'thumb': item.get('thumb', 'https://via.placeholder.com/300x150?text=Promocja'),
                    'url': f"https://www.cheapshark.com/redirect?dealID={deal_id}"
                })
            return deals
    except Exception as e:
        print(f"Błąd top deals: {e}")
    return []

@app.route('/')
def home():
    freebies = get_freebies()
    top_deals = get_top_deals()
    
    # Stan połączenia kont zapisany w sesji
    connected = {
        'steam': session.get('steam_id'),
        'epic': session.get('epic_user'),
        'xbox': session.get('xbox_user'),
        'psn': session.get('psn_user')
    }
    
    return render_template('index.html', freebies=freebies, top_deals=top_deals, connected=connected)

# --- OFICJALNE LOGOWANIE STEAM OPENID ---
@app.route('/login/steam')
def login_steam():
    # Pobieramy domenę, na której działa aplikacja (np. lowca-okazji.onrender.com)
    domain = request.host_url.rstrip('/')
    
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': f"{domain}/login/steam/callback",
        'openid.realm': domain,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
    }
    steam_url = "https://steamcommunity.com/openid/login?" + urllib.parse.urlencode(params)
    return redirect(steam_url)

@app.route('/login/steam/callback')
def steam_callback():
    # Odbieramy odpowiedź ze Steam i wyciągamy SteamID
    claimed_id = request.args.get('openid.claimed_id', '')
    if claimed_id:
        steam_id = claimed_id.split('/')[-1]
        session['steam_id'] = steam_id
    return redirect(url_for('home'))

# --- PODŁĄCZANIE POZOSTAŁYCH KONT (EPIC, XBOX, PSN) ---
@app.route('/connect/<platform>', methods=['POST'])
def connect_platform(platform):
    username = request.form.get('username', '').strip()
    if username:
        session[f'{platform}_user'] = username
    return redirect(url_for('home'))

@app.route('/disconnect/<platform>')
def disconnect_platform(platform):
    session.pop(f'{platform}_user', None)
    if platform == 'steam':
        session.pop('steam_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
