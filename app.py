from flask import Flask, render_template, request, redirect, session, url_for
import requests
import urllib.parse

app = Flask(__name__, template_folder='.')
app.secret_key = 'super_tajny_kluczyk_game_claimer'

def get_epic_free_games():
    """ Pobiera aktualne darmowe gry prosto z API Epic Games Store """
    url = "https://store-site-backend-static-ipv4.akamaized.net/freeGamesPromotions?locale=pl-PL&country=PL"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            elements = data['data']['Catalog']['searchStore']['elements']
            
            freebies = []
            for item in elements:
                promotions = item.get('promotions')
                if not promotions:
                    continue
                
                # Sprawdzamy czy gra jest aktualnie darmowa (100% discount)
                offers = promotions.get('promotionalOffers', [])
                if offers:
                    title = item.get('title', 'Darmowa Gra')
                    
                    # Szukamy miniaturki gry
                    photo = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600"
                    for img in item.get('keyImages', []):
                        if img.get('type') in ['OfferImageWide', 'DieselStoreFrontWide', 'Thumbnail']:
                            photo = img.get('url')
                            break
                    
                    page_slug = item.get('productSlug') or item.get('urlSlug') or 'free-games'
                    game_url = f"https://store.epicgames.com/pl/p/{page_slug}"
                    
                    freebies.append({
                        'title': title,
                        'thumb': photo,
                        'url': game_url,
                        'store': 'Epic Games'
                    })
            return freebies if freebies else get_fallback_freebies()
    except Exception as e:
        print(f"Błąd Epic API: {e}")
    return get_fallback_freebies()

def get_fallback_freebies():
    """ Alternatywne powiadomienie z ładnym tłem gdy brak promocji """
    return [{
        'title': 'Darmowe Gry Tygodnia Epic Games Store',
        'thumb': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600',
        'url': 'https://store.epicgames.com/pl/free-games',
        'store': 'Epic Games'
    }]

def get_top_deals():
    """ Pobiera TOP 10 najlepszych gier z największą przeceną """
    url = "https://www.cheapshark.com/api/1.0/deals?sortBy=Savings&pageSize=10"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            deals = []
            stores = {"1": "Steam", "7": "GOG", "11": "Humble", "25": "Epic Games"}
            for item in data:
                deals.append({
                    'title': item.get('title'),
                    'price': item.get('salePrice'),
                    'old_price': item.get('normalPrice'),
                    'store': stores.get(str(item.get('storeID')), 'Sklep PC'),
                    'thumb': item.get('thumb'),
                    'url': f"https://www.cheapshark.com/redirect?dealID={item.get('dealID')}"
                })
            return deals
    except Exception as e:
        print(f"Błąd top deals: {e}")
    return []

@app.route('/')
def home():
    freebies = get_epic_free_games()
    top_deals = get_top_deals()
    
    connected = {
        'steam': session.get('steam_id'),
        'epic': session.get('epic_user'),
        'ubisoft': session.get('ubisoft_user'),
        'xbox': session.get('xbox_user'),
        'psn': session.get('psn_user')
    }
    
    return render_template('index.html', freebies=freebies, top_deals=top_deals, connected=connected)

# --- LOGOWANIE STEAM ---
@app.route('/login/steam')
def login_steam():
    domain = request.host_url.rstrip('/')
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': f"{domain}/login/steam/callback",
        'openid.realm': domain,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
    }
    return redirect("https://steamcommunity.com/openid/login?" + urllib.parse.urlencode(params))

@app.route('/login/steam/callback')
def steam_callback():
    claimed_id = request.args.get('openid.claimed_id', '')
    if claimed_id:
        session['steam_id'] = claimed_id.split('/')[-1]
    return redirect(url_for('home'))

# --- LOGOWANIE DLA POZOSTAŁYCH PLATFORM (EPIC, UBISOFT, XBOX, PSN) ---
@app.route('/login/<platform>')
def login_oauth(platform):
    # Przekierowanie do logowania poszczególnych platform
    urls = {
        'epic': 'https://www.epicgames.com/id/login',
        'ubisoft': 'https://connect.ubisoft.com/login',
        'xbox': 'https://login.live.com/oauth20_authorize.srf',
        'psn': 'https://my.account.sony.com/central/signin/'
    }
    target_url = urls.get(platform, '/')
    # Zapisujemy symulację zalogowania dla demonstracji
    session[f'{platform}_user'] = f"Połączono ({platform.capitalize()})"
    return redirect(target_url)

@app.route('/disconnect/<platform>')
def disconnect_platform(platform):
    session.pop(f'{platform}_user', None)
    if platform == 'steam':
        session.pop('steam_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
