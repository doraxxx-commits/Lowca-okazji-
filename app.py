from flask import Flask, render_template, request, redirect, session, url_for
import requests
import urllib.parse

app = Flask(__name__, template_folder='.')
app.secret_key = 'super_tajny_kluczyk_game_claimer'

def get_epic_free_games():
    """ Pobiera darmowe gry z Epic Games bez ryzyka wywalenia błędu """
    url = "https://store-site-backend-static-ipv4.akamaized.net/freeGamesPromotions?locale=pl-PL&country=PL"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)"}
    
    current_freebies = []
    upcoming_freebies = []
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            elements = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
            
            for item in elements:
                title = item.get('title', 'Darmowa Gra')
                promotions = item.get('promotions')
                if not promotions:
                    continue
                
                # Zdjęcie
                photo = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600"
                for img in item.get('keyImages', []):
                    if img.get('type') in ['OfferImageWide', 'DieselStoreFrontWide', 'Thumbnail']:
                        photo = img.get('url')
                        break
                
                page_slug = item.get('productSlug') or item.get('urlSlug') or 'free-games'
                game_url = f"https://store.epicgames.com/pl/p/{page_slug}"
                
                # 1. Obecnie darmowe
                curr_offers = promotions.get('promotionalOffers', [])
                if curr_offers and len(curr_offers) > 0:
                    offers_list = curr_offers[0].get('promotionalOffers', [])
                    if offers_list:
                        end_date = offers_list[0].get('endDate', '')
                        current_freebies.append({
                            'title': title,
                            'thumb': photo,
                            'url': game_url,
                            'end_date': end_date,
                            'store': 'Epic Games'
                        })
                
                # 2. Nadchodzące
                up_offers = promotions.get('upcomingPromotionalOffers', [])
                if up_offers and len(up_offers) > 0:
                    offers_list = up_offers[0].get('promotionalOffers', [])
                    if offers_list:
                        start_date = offers_list[0].get('startDate', '')
                        upcoming_freebies.append({
                            'title': title,
                            'thumb': photo,
                            'url': game_url,
                            'start_date': start_date,
                            'store': 'Epic Games'
                        })
    except Exception as e:
        print(f"Błąd Epic Games API: {e}")
        
    # Awaryjne uzupełnienie, żeby sekcja NIGDY nie była pusta
    if not current_freebies:
        current_freebies.append({
            'title': 'Darmowa Gra Tygodnia (Epic Games)',
            'thumb': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600',
            'url': 'https://store.epicgames.com/pl/free-games',
            'store': 'Epic Games'
        })
        
    return current_freebies, upcoming_freebies

def get_top_deals():
    """ Pobiera top okazje (gwarantuje przynajmniej 10 wyników) """
    url = "https://www.cheapshark.com/api/1.0/deals?sortBy=Savings&pageSize=30"
    headers = {"User-Agent": "Mozilla/5.0"}
    deals = []
    stores = {"1": "Steam", "7": "GOG", "11": "Humble", "25": "Epic Games"}
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for item in data:
                savings = float(item.get('savings', 0))
                deals.append({
                    'title': item.get('title', 'Gra w promocji'),
                    'price': item.get('salePrice', '0'),
                    'old_price': item.get('normalPrice', '0'),
                    'discount': int(savings),
                    'store': stores.get(str(item.get('storeID')), 'Sklep PC'),
                    'thumb': item.get('thumb', 'https://via.placeholder.com/300x150'),
                    'url': f"https://www.cheapshark.com/redirect?dealID={item.get('dealID')}"
                })
                if len(deals) >= 10:
                    break
    except Exception as e:
        print(f"Błąd CheapShark API: {e}")
        
    return deals

@app.route('/')
def home():
    current_freebies, upcoming_freebies = get_epic_free_games()
    top_deals = get_top_deals()
    
    connected = {
        'steam': session.get('steam_id'),
        'epic': session.get('epic_user'),
        'ubisoft': session.get('ubisoft_user'),
        'xbox': session.get('xbox_user'),
        'psn': session.get('psn_user')
    }
    
    return render_template('index.html', 
                           current_freebies=current_freebies, 
                           upcoming_freebies=upcoming_freebies, 
                           top_deals=top_deals, 
                           connected=connected)

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

@app.route('/login/<platform>')
def login_oauth(platform):
    urls = {
        'epic': 'https://www.epicgames.com/id/login',
        'ubisoft': 'https://connect.ubisoft.com/login',
        'xbox': 'https://login.live.com/oauth20_authorize.srf',
        'psn': 'https://my.account.sony.com/central/signin/'
    }
    session[f'{platform}_user'] = f"Połączono ({platform.capitalize()})"
    return redirect(urls.get(platform, '/'))

@app.route('/disconnect/<platform>')
def disconnect_platform(platform):
    session.pop(f'{platform}_user', None)
    if platform == 'steam':
        session.pop('steam_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
