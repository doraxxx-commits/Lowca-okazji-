from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import random, uuid, math

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
HTML_FILE = ROOT / 'game_transfery_poprawione.html'

LEAGUES = {
 'Ekstraklasa':[('Legia Warszawa',72),('Lech Poznań',71),('Raków Częstochowa',70),('Jagiellonia Białystok',69),('Pogoń Szczecin',68),('Górnik Zabrze',64),('Widzew Łódź',63),('Cracovia',62),('Wisła Kraków',61),('Śląsk Wrocław',60),('Piast Gliwice',61),('Lechia Gdańsk',59),('Zagłębie Lubin',58),('Radomiak Radom',57),('Motor Lublin',56),('Korona Kielce',55),('Stal Mielec',54),('GKS Katowice',53)],
 'Premier League':[('Manchester City',88),('Liverpool',86),('Arsenal',85),('Chelsea',81),('Manchester United',80),('Newcastle',78),('Tottenham',79),('Aston Villa',78),('Brighton',75),('West Ham',73),('Crystal Palace',72),('Everton',70),('Fulham',70),('Wolves',69),('Brentford',72),('Bournemouth',68),('Nottingham Forest',67),('Leicester',66)],
 'La Liga':[('Real Madrid',90),('Barcelona',88),('Atletico Madrid',84),('Athletic Bilbao',78),('Real Sociedad',77),('Villarreal',76),('Sevilla',74),('Valencia',73),('Real Betis',76),('Girona',75),('Celta Vigo',69),('Getafe',68),('Osasuna',69),('Mallorca',68),('Rayo Vallecano',67),('Alaves',65),('Espanyol',64),('Leganes',62)],
 'Bundesliga':[('Bayern Monachium',89),('Bayer Leverkusen',86),('Borussia Dortmund',83),('RB Leipzig',81),('Eintracht Frankfurt',77),('Stuttgart',76),('Freiburg',72),('Union Berlin',71),('Mainz',69),('Werder Bremen',70),("Borussia M'gladbach",69),('Hoffenheim',68),('Wolfsburg',70),('Augsburg',66),('Heidenheim',63),('St. Pauli',61),('Bochum',60),('Holstein Kiel',59)]}

RIVALS={'Legia Warszawa':['Lech Poznań'],'Lech Poznań':['Legia Warszawa'],'Real Madrid':['Barcelona','Atletico Madrid'],'Barcelona':['Real Madrid'],'Liverpool':['Manchester United'],'Manchester United':['Liverpool','Manchester City'],'Manchester City':['Manchester United'],'Bayern Monachium':['Borussia Dortmund'],'Borussia Dortmund':['Bayern Monachium']}
FIRST=['Jan','Kacper','Michał','Mateusz','Jakub','Szymon','Antoni','Filip','Bartosz','Oskar','Nikodem','Igor','Leon','Tomasz','Piotr','Adam','Marcel','Mikołaj','Wiktor','Patryk']
LAST=['Kowalski','Nowak','Wiśniewski','Wójcik','Kamiński','Lewandowski','Zieliński','Szymański','Woźniak','Dąbrowski','Kozłowski','Jankowski','Mazur','Krawczyk','Piotrowski','Grabowski','Pawłowski','Michalski','Król','Wieczorek']
POSITIONS=['Bramkarz','Obrońca','Pomocnik','Napastnik']
SESSIONS={}

def clamp(x,a,b): return max(a,min(b,x))
def rn(): return f'{random.choice(FIRST)} {random.choice(LAST)}'
def poisson(l):
    p=1.0;k=0;limit=math.exp(-max(.05,l))
    while p>limit and k<8:k+=1;p*=random.random()
    return max(0,k-1)
def squad(ovr):
    out=[]
    for _ in range(22):
        r=clamp(ovr+random.randint(-10,5),35,92); age=random.randint(17,34)
        out.append({'name':rn(),'position':random.choice(POSITIONS),'ovr':r,'age':age,'value':max(25000,r*r*random.randint(25,70)),'wage':r*random.randint(80,220)})
    return out

def world(selected=None,league=None):
    clubs={}; leagues={}
    for lg,rows in LEAGUES.items():
        leagues[lg]=[]
        for n,o in rows:
            clubs[n]={'name':n,'league':lg,'ovr':o,'budget':random.randint(10,45)*1_000_000,'squad':squad(o),'momentum':50}
            leagues[lg].append(n)
    if selected and selected not in clubs:
        lg=league or 'Ekstraklasa';clubs[selected]={'name':selected,'league':lg,'ovr':60,'budget':20_000_000,'squad':squad(60),'momentum':50};leagues.setdefault(lg,[]).append(selected)
    return {'clubs':clubs,'leagues':leagues}

def table(w):
    return {lg:{n:{'name':n,'played':0,'wins':0,'draws':0,'losses':0,'gf':0,'ga':0,'gd':0,'pts':0} for n in ns} for lg,ns in w['leagues'].items()}
def match(a,b):
    rival=b['name'] in RIVALS.get(a['name'],[]) or a['name'] in RIVALS.get(b['name'],[])
    hs=(a['ovr']+2+(a['momentum']-50)*.06)/10; aw=(b['ovr']+(b['momentum']-50)*.06)/10; bonus=.18 if rival else 0
    return min(6,poisson(clamp(1.2+(hs-aw)*.2+bonus,.25,3.4))),min(6,poisson(clamp(1+(aw-hs)*.2+bonus,.2,3.2))),rival
def result(t,a,b,ag,bg):
    A=t[a['league']][a['name']];B=t[b['league']][b['name']];A['played']+=1;B['played']+=1;A['gf']+=ag;A['ga']+=bg;B['gf']+=bg;B['ga']+=ag
    if ag>bg:A['wins']+=1;B['losses']+=1;A['pts']+=3
    elif bg>ag:B['wins']+=1;A['losses']+=1;B['pts']+=3
    else:A['draws']+=1;B['draws']+=1;A['pts']+=1;B['pts']+=1
    A['gd']=A['gf']-A['ga'];B['gd']=B['gf']-B['ga']

def fee(p): return max(100000,int(p['value']*random.uniform(.75,1.35)))
def transfers(w,news,phase):
    cs=list(w['clubs'].values());out=[]
    for _ in range(random.randint(22,34)):
        s,b=random.sample(cs,2)
        if len(s['squad'])<=18 or len(b['squad'])>=27: continue
        cand=[p for p in s['squad'] if abs(p['ovr']-b['ovr'])<=10 and fee(p)<=b['budget']]
        if not cand or random.random()>(.68 if phase=='summer' else .50):continue
        p=random.choice(cand);f=fee(p);s['squad'].remove(p);b['squad'].append(p);b['budget']-=f;s['budget']+=int(f*.94)
        out.append({'player':p['name'],'ovr':p['ovr'],'age':p['age'],'from':s['name'],'to':b['name'],'fee':f})
    for x in out[:10]:news.append(f"🔄 Transfer AI: {x['player']} ({x['ovr']} OVR) {x['from']} → {x['to']} za {x['fee']} PLN.")
    return out

def offers(w,p):
    out=[]
    for c in w['clubs'].values():
        if c['name']==p['club']:continue
        gap=abs(c['ovr']-p['ovr'])
        if gap<=10 and random.random()<.8:
            out.append({'club':c['name'],'league':c['league'],'ovr':c['ovr'],'wage':max(900,c['ovr']*random.randint(90,220)),'contractYears':random.choice([2,3,4]),'signingBonus':random.randint(5000,40000)})
    return sorted(out,key=lambda x:abs(x['ovr']-p['ovr']))[:5]

def develop(w):
    for c in w['clubs'].values():
        avg=sum(x['ovr'] for x in c['squad'])/len(c['squad']);c['ovr']=clamp(round(c['ovr']*.72+avg*.28+random.uniform(-1.2,1.2)),45,92);c['budget']+=random.randint(2,10)*1_000_000

def season(s):
    w=s['world'];p=s['player'];news=[];games=[];ts=transfers(w,news,'summer');t=table(w)
    for lg,names in w['leagues'].items():
        for h in names:
            for a in names:
                if h==a:continue
                ag,bg,riv=match(w['clubs'][h],w['clubs'][a]);result(t,w['clubs'][h],w['clubs'][a],ag,bg)
                if len(games)<700:games.append({'league':lg,'home':h,'away':a,'homeScore':ag,'awayScore':bg,'rivalry':riv})
                if riv and (h==p['club'] or a==p['club']):news.append(f'🔥 RYWALIZACJA: {h} {ag}:{bg} {a}.')
    standings={lg:sorted(rows.values(),key=lambda x:(x['pts'],x['gd'],x['gf']),reverse=True) for lg,rows in t.items()};row=next((x for x in standings[p['league']] if x['name']==p['club']),None)
    old=p['ovr'];mp=max(10,round(random.randint(22,34)*clamp(p['ovr']/88,.35,.96)));pos=p['position'];goals=random.randint(4,18) if pos=='Napastnik' else random.randint(2,10) if pos=='Pomocnik' else random.randint(0,5) if pos=='Obrońca' else random.randint(0,2);ass=random.randint(1,8) if pos=='Napastnik' else random.randint(3,12) if pos=='Pomocnik' else random.randint(0,5);p['ovr']=clamp(old+(2 if goals+ass>=10 else 1 if goals+ass>=5 else random.choice([-1,0])),40,92);p['year']+=1;p['stats']={'matches':mp,'minutes':mp*random.randint(55,88),'goals':goals,'assists':ass,'yellow':random.randint(0,6),'red':int(random.random()<.1)};p['value']=max(25000,p['ovr']*p['ovr']*random.randint(35,75))
    ts+=transfers(w,news,'winter');develop(w)
    summary={'season':f"{p['year']-1}/{p['year']}",'club':p['club'],'league':p['league'],'position':standings[p['league']].index(row)+1 if row else None,'matches':mp,'goals':goals,'assists':ass,'oldOVR':old,'newOVR':p['ovr'],'transfers':ts[:40],'playerOffers':offers(w,p),'standings':{k:v[:18] for k,v in standings.items()},'news':news[:40],'matches':games[:300],'rivalries':RIVALS.get(p['club'],[])}
    s['history'].append(summary);s['last_summary']=summary;return summary

@app.get('/')
def home(): return send_from_directory(ROOT,HTML_FILE.name)
@app.get('/api/health')
def health(): return jsonify(ok=True,engine='Python Football Simulation Engine',version='2.0')
@app.post('/api/session')
def session():
    b=request.get_json(silent=True) or {};pl=b.get('player',{});cl=b.get('club',{});w=world(cl.get('name'),cl.get('league'));c=w['clubs'][cl.get('name') or next(iter(w['clubs']))];p={'name':pl.get('name','Zawodnik'),'position':pl.get('position','Napastnik'),'ovr':int(pl.get('ovr',48)),'year':int(pl.get('year',2026)),'club':c['name'],'league':c['league'],'stats':pl.get('stats',{}),'value':int(pl.get('value',100000)),'gameMode':pl.get('gameMode','simulation')};sid=uuid.uuid4().hex;SESSIONS[sid]={'world':w,'player':p,'history':[],'last_summary':None};return jsonify(sessionId=sid,engine='python',club={'name':c['name'],'league':c['league'],'ovr':c['ovr']})
@app.post('/api/season')
def run_season():
    s=SESSIONS.get((request.get_json(silent=True) or {}).get('sessionId'));return (jsonify(error='Brak sesji'),404) if not s else jsonify(ok=True,summary=season(s),player=s['player'])
@app.post('/api/offers')
def get_offers():
    s=SESSIONS.get((request.get_json(silent=True) or {}).get('sessionId'));return (jsonify(error='Brak sesji'),404) if not s else jsonify(offers=offers(s['world'],s['player']))
@app.post('/api/transfer')
def do_transfer():
    b=request.get_json(silent=True) or {};s=SESSIONS.get(b.get('sessionId'));club=s and s['world']['clubs'].get(b.get('club'))
    if not s or not club:return jsonify(error='Brak sesji lub klubu'),404
    old=s['player']['club'];s['player']['club']=club['name'];s['player']['league']=club['league'];s['player']['contractYears']=int(b.get('contractYears',3));return jsonify(ok=True,player=s['player'],news=[f"🔄 Transfer: {old} → {club['name']}."])
@app.post('/api/state')
def state():
    s=SESSIONS.get((request.get_json(silent=True) or {}).get('sessionId'));return (jsonify(error='Brak sesji'),404) if not s else jsonify(player=s['player'],summary=s['last_summary'],history=s['history'])

if __name__=='__main__': app.run(host='0.0.0.0',port=8000)
