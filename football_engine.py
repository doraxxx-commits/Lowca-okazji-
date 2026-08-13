from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import json
import random
import uuid

# ============================================================
# KONFIGURACJA APLIKACJI
# ============================================================

app = Flask(__name__)

ROOT = Path(__file__).resolve().parent
HTML_FILE = ROOT / "game_transfery_poprawione.html"

# ============================================================
# DANE GRY
# ============================================================

POSITIONS = [
    "Bramkarz",
    "Obrońca",
    "Pomocnik",
    "Napastnik"
]

FIRST = [
    "Jan",
    "Kacper",
    "Michał",
    "Mateusz",
    "Jakub",
    "Szymon",
    "Antoni",
    "Filip",
    "Bartosz",
    "Oskar",
    "Nikodem",
    "Igor",
    "Leon",
    "Tomasz",
    "Piotr",
    "Adam",
    "Marcel",
    "Mikołaj",
    "Wiktor",
    "Patryk"
]

LAST = [
    "Kowalski",
    "Nowak",
    "Wiśniewski",
    "Wójcik",
    "Kamiński",
    "Lewandowski",
    "Zieliński",
    "Szymański",
    "Woźniak",
    "Dąbrowski",
    "Kozłowski",
    "Jankowski",
    "Mazur",
    "Krawczyk",
    "Piotrowski",
    "Grabowski",
    "Pawłowski",
    "Michalski",
    "Król",
    "Wieczorek"
]

# ============================================================
# LIGI I KLUBY
# ============================================================

LEAGUES = {
    "Ekstraklasa": [
        ("Legia Warszawa", 72),
        ("Lech Poznań", 71),
        ("Raków Częstochowa", 70),
        ("Jagiellonia Białystok", 69),
        ("Pogoń Szczecin", 68),
        ("Górnik Zabrze", 64),
        ("Widzew Łódź", 63),
        ("Cracovia", 62),
        ("Wisła Kraków", 61),
        ("Śląsk Wrocław", 60),
        ("Piast Gliwice", 61),
        ("Lechia Gdańsk", 59),
        ("Zagłębie Lubin", 58),
        ("Radomiak Radom", 57),
        ("Motor Lublin", 56),
        ("Korona Kielce", 55),
        ("Stal Mielec", 54),
        ("GKS Katowice", 53)
    ],

    "Premier League": [
        ("Manchester City", 88),
        ("Liverpool", 86),
        ("Arsenal", 85),
        ("Chelsea", 81),
        ("Manchester United", 80),
        ("Newcastle", 78),
        ("Tottenham", 79),
        ("Aston Villa", 78),
        ("Brighton", 75),
        ("West Ham", 73),
        ("Crystal Palace", 72),
        ("Everton", 70),
        ("Fulham", 70),
        ("Wolves", 69),
        ("Brentford", 72),
        ("Bournemouth", 68),
        ("Nottingham Forest", 67),
        ("Leicester", 66)
    ],

    "La Liga": [
        ("Real Madrid", 90),
        ("Barcelona", 88),
        ("Atletico Madrid", 84),
        ("Athletic Bilbao", 78),
        ("Real Sociedad", 77),
        ("Villarreal", 76),
        ("Sevilla", 74),
        ("Valencia", 73),
        ("Real Betis", 76),
        ("Girona", 75),
        ("Celta Vigo", 69),
        ("Getafe", 68),
        ("Osasuna", 69),
        ("Mallorca", 68),
        ("Rayo Vallecano", 67),
        ("Alaves", 65),
        ("Espanyol", 64),
        ("Leganes", 62)
    ],

    "Bundesliga": [
        ("Bayern Monachium", 89),
        ("Bayer Leverkusen", 86),
        ("Borussia Dortmund", 83),
        ("RB Leipzig", 81),
        ("Eintracht Frankfurt", 77),
        ("Stuttgart", 76),
        ("Freiburg", 72),
        ("Union Berlin", 71),
        ("Mainz", 69),
        ("Werder Bremen", 70),
        ("Borussia M'gladbach", 69),
        ("Hoffenheim", 68),
        ("Wolfsburg", 70),
        ("Augsburg", 66),
        ("Heidenheim", 63),
        ("St. Pauli", 61),
        ("Bochum", 60),
        ("Holstein Kiel", 59)
    ]
}

# ============================================================
# SESJE
# ============================================================

SESSIONS = {}


# ============================================================
# FUNKCJE POMOCNICZE
# ============================================================

def money(n):
    return int(round(n))


def rn():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"


def clamp(v, a, b):
    return max(a, min(b, v))


def poisson_like(lam):
    """
    Lekki model Poissona bez zewnętrznych bibliotek.
    """
    l = max(0.05, lam)
    k = 0
    p = 1.0
    limit = pow(2.718281828, -l)

    while p > limit and k < 8:
        k += 1
        p *= random.random()

    return max(0, k - 1)


# ============================================================
# TWORZENIE SKŁADU
# ============================================================

def make_squad(ovr):
    squad = []

    for _ in range(22):
        r = clamp(
            ovr + random.randint(-10, 5),
            35,
            92
        )

        age = random.randint(17, 34)

        squad.append({
            "name": rn(),
            "position": random.choice(POSITIONS),
            "ovr": r,
            "age": age,
            "value": r * r * random.randint(25, 70),
            "wage": r * random.randint(80, 220)
        })

    return squad


# ============================================================
# BUDOWANIE ŚWIATA
# ============================================================

def build_world(selected_club=None, selected_league=None):
    clubs = {}
    leagues = {}

    for league, rows in LEAGUES.items():
        leagues[league] = []

        for name, ovr in rows:
            clubs[name] = {
                "name": name,
                "league": league,
                "ovr": ovr,
                "base_ovr": ovr,
                "budget": random.randint(8, 45) * 1_000_000,
                "momentum": 50,
                "squad": make_squad(ovr)
            }

            leagues[league].append(name)

    # Jeżeli wybrany klub nie istnieje w bazie,
    # zostaje utworzony jako nowy klub.
    if selected_club and selected_club not in clubs:
        league = selected_league or "Ekstraklasa"
        ovr = 60

        clubs[selected_club] = {
            "name": selected_club,
            "league": league,
            "ovr": ovr,
            "base_ovr": ovr,
            "budget": 20_000_000,
            "momentum": 50,
            "squad": make_squad(ovr)
        }

        leagues.setdefault(league, []).append(selected_club)

    return {
        "clubs": clubs,
        "leagues": leagues
    }


# ============================================================
# TABELA
# ============================================================

def reset_table(world):
    table = {}

    for league, names in world["leagues"].items():
        table[league] = {}

        for n in names:
            table[league][n] = {
                "name": n,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "gf": 0,
                "ga": 0,
                "gd": 0,
                "pts": 0
            }

    return table


# ============================================================
# MECZ
# ============================================================

def play_match(a, b):
    home = (
        a["ovr"]
        + 2.0
        + (a["momentum"] - 50) * 0.06
    ) / 10

    away = (
        b["ovr"]
        + (b["momentum"] - 50) * 0.06
    ) / 10

    ag = poisson_like(
        clamp(
            1.20 + (home - away) * 0.20,
            0.25,
            3.2
        )
    )

    bg = poisson_like(
        clamp(
            1.00 + (away - home) * 0.20,
            0.20,
            3.0
        )
    )

    return min(6, ag), min(6, bg)


# ============================================================
# WYNIK MECZU W TABELI
# ============================================================

def apply_result(table, a, b, ag, bg):
    A = table[a["league"]][a["name"]]
    B = table[b["league"]][b["name"]]

    A["played"] += 1
    B["played"] += 1

    A["gf"] += ag
    A["ga"] += bg

    B["gf"] += bg
    B["ga"] += ag

    A["gd"] = A["gf"] - A["ga"]
    B["gd"] = B["gf"] - B["ga"]

    if ag > bg:
        A["wins"] += 1
        A["pts"] += 3

        B["losses"] += 1

        a["momentum"] = clamp(
            a["momentum"] + 3,
            20,
            80
        )

        b["momentum"] = clamp(
            b["momentum"] - 2,
            20,
            80
        )

    elif ag < bg:
        B["wins"] += 1
        B["pts"] += 3

        A["losses"] += 1

        b["momentum"] = clamp(
            b["momentum"] + 3,
            20,
            80
        )

        a["momentum"] = clamp(
            a["momentum"] - 2,
            20,
            80
        )

    else:
        A["draws"] += 1
        B["draws"] += 1

        A["pts"] += 1
        B["pts"] += 1

        a["momentum"] = clamp(
            a["momentum"] + 1,
            20,
            80
        )

        b["momentum"] = clamp(
            b["momentum"] + 1,
            20,
            80
        )


# ============================================================
# TRANSFERY
# ============================================================

def transfer_window(world, news):
    clubs = list(world["clubs"].values())
    transfers = []

    for _ in range(random.randint(18, 32)):
        selling, buying = random.sample(clubs, 2)

        if len(selling["squad"]) <= 18:
            continue

        if len(buying["squad"]) >= 27:
            continue

        candidates = [
            p
            for p in selling["squad"]
            if abs(p["ovr"] - buying["ovr"]) <= 8
        ]

        if not candidates:
            continue

        p = random.choice(candidates)

        fee = int(
            p["value"] * random.uniform(0.8, 1.45)
        )

        if buying["budget"] < fee:
            continue

        # AI preferuje młodszych zawodników
        # i zawodników o zbliżonym poziomie.

        if random.random() > (
            0.55 + (2 if p["age"] < 23 else 0) / 10
        ):
            continue

        selling["squad"].remove(p)
        buying["squad"].append(p)

        buying["budget"] -= fee
        selling["budget"] += int(fee * 0.94)

        transfers.append({
            "player": p["name"],
            "ovr": p["ovr"],
            "from": selling["name"],
            "to": buying["name"],
            "fee": fee
        })

    # ========================================================
    # WOLNI AGENCI
    # ========================================================

    for c in clubs:
        while (
            len(c["squad"]) < 19
            and random.random() < 0.55
        ):
            p = {
                "name": rn(),
                "position": random.choice(POSITIONS),
                "ovr": clamp(
                    c["ovr"] + random.randint(-8, 2),
                    35,
                    82
                ),
                "age": random.randint(18, 30),
                "value": 0,
                "wage": 0
            }

            p["value"] = (
                p["ovr"]
                * p["ovr"]
                * random.randint(20, 55)
            )

            p["wage"] = (
                p["ovr"]
                * random.randint(70, 160)
            )

            c["squad"].append(p)

    # ========================================================
    # NEWSY TRANSFEROWE
    # ========================================================

    for t in transfers[:8]:
        news.append(
            f"🔄 {t['player']} ({t['ovr']} OVR): "
            f"{t['from']} → {t['to']} "
            f"za {money(t['fee']):,} PLN".replace(",", " ")
        )

    return transfers


# ============================================================
# SYMULACJA SEZONU
# ============================================================

def season(session):
    world = session["world"]

    table = reset_table(world)
    news = []
    matches = []

    # ========================================================
    # DWIE RUNDY KAŻDY Z KAŻDYM
    # ========================================================

    for league, names in world["leagues"].items():

        for home in names:

            for away in names:

                if home == away:
                    continue

                a = world["clubs"][home]
                b = world["clubs"][away]

                ag, bg = play_match(a, b)

                apply_result(
                    table,
                    a,
                    b,
                    ag,
                    bg
                )

                if len(matches) < 500:
                    matches.append({
                        "league": league,
                        "home": home,
                        "away": away,
                        "homeScore": ag,
                        "awayScore": bg
                    })

    # ========================================================
    # OKNO TRANSFEROWE PO SEZONIE
    # ========================================================

    transfers = transfer_window(
        world,
        news
    )

    # ========================================================
    # ROZWÓJ / REGRES KLUBÓW
    # ========================================================

    for c in world["clubs"].values():

        avg = (
            sum(
                p["ovr"]
                for p in c["squad"]
            )
            / max(1, len(c["squad"]))
        )

        c["ovr"] = clamp(
            round(
                c["ovr"] * 0.72
                + avg * 0.28
                + random.uniform(-1.2, 1.2)
            ),
            45,
            92
        )

        c["budget"] += (
            random.randint(2, 10)
            * 1_000_000
        )

    # ========================================================
    # TABELA KOŃCOWA
    # ========================================================

    standings = {}

    for league, rows in table.items():
        standings[league] = sorted(
            rows.values(),
            key=lambda x: (
                x["pts"],
                x["gd"],
                x["gf"]
            ),
            reverse=True
        )

    # ========================================================
    # ZAWODNIK
    # ========================================================

    p = session["player"]

    club = world["clubs"].get(
        p["club"]
    )

    league = p["league"]

    row = next(
        (
            r
            for r in standings[league]
            if r["name"] == p["club"]
        ),
        None
    )

    # ========================================================
    # STATYSTYKI ZAWODNIKA
    # ========================================================

    matches_played = random.randint(
        22,
        34
    )

    participation = clamp(
        p["ovr"] / 88,
        0.35,
        0.96
    )

    matches_played = max(
        10,
        round(
            matches_played
            * participation
        )
    )

    pos = p["position"]

    if pos == "Napastnik":
        goals = random.randint(
            4,
            18
        )

    elif pos == "Pomocnik":
        goals = random.randint(
            2,
            10
        )

    elif pos == "Obrońca":
        goals = random.randint(
            0,
            5
        )

    else:
        goals = random.randint(
            0,
            2
        )

    if pos == "Napastnik":
        assists = random.randint(
            1,
            8
        )

    elif pos == "Pomocnik":
        assists = random.randint(
            3,
            12
        )

    else:
        assists = random.randint(
            0,
            5
        )

    old = p["ovr"]

    impact = goals + assists

    if impact >= 10:
        delta = random.choice([
            1,
            1,
            2,
            2,
            3
        ])

    elif impact >= 5:
        delta = random.choice([
            0,
            1,
            1,
            2
        ])

    else:
        delta = random.choice([
            -1,
            0,
            0,
            1
        ])

    p["ovr"] = clamp(
        old + delta,
        40,
        92
    )

    p["year"] += 1

    p["stats"] = {
        "matches": matches_played,
        "minutes": (
            matches_played
            * random.randint(55, 88)
        ),
        "goals": goals,
        "assists": assists,
        "yellow": random.randint(0, 6),
        "red": (
            1
            if random.random() < 0.1
            else 0
        )
    }

    p["value"] = max(
        25_000,
        p["ovr"]
        * p["ovr"]
        * random.randint(35, 75)
    )

    # ========================================================
    # PODSUMOWANIE
    # ========================================================

    summary = {
        "season": (
            f"{p['year'] - 1}/"
            f"{p['year']}"
        ),

        "club": p["club"],

        "league": league,

        "position": (
            standings[league].index(row) + 1
            if row
            else None
        ),

        "matches": matches_played,

        "goals": goals,

        "assists": assists,

        "oldOVR": old,

        "newOVR": p["ovr"],

        "transfers": transfers[:20],

        "standings": {
            k: v[:18]
            for k, v in standings.items()
        },

        "news": news[:30],

        "matches": matches[:200]
    }

    # ========================================================
    # ZAPIS SESJI
    # ========================================================

    session["history"].append(
        summary
    )

    session["table"] = standings

    session["last_summary"] = summary

    return summary


# ============================================================
# CORS
# ============================================================

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type"
    )
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, OPTIONS"
    )
    response.headers["Cache-Control"] = "no-store"

    return response


# ============================================================
# OPTIONS
# ============================================================

@app.route(
    "/<path:path>",
    methods=["OPTIONS"]
)
@app.route(
    "/",
    methods=["OPTIONS"]
)
def options_handler(path=None):
    return "", 204


# ============================================================
# STRONA GŁÓWNA
# ============================================================

@app.route("/")
@app.route("/index.html")
def index():
    if not HTML_FILE.exists():
        return jsonify({
            "error": "Brak pliku HTML",
            "expected": str(HTML_FILE)
        }), 404

    return send_from_directory(
        ROOT,
        HTML_FILE.name
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():
    return jsonify({
        "ok": True,
        "engine": "Python Football Simulation Engine",
        "version": "1.0",
        "framework": "Flask",
        "status": "running"
    })


# ============================================================
# TWORZENIE SESJI
# ============================================================

@app.route(
    "/api/session",
    methods=["POST"]
)
def create_session():

    try:
        body = request.get_json(
            silent=True
        ) or {}

        sid = uuid.uuid4().hex

        player = body.get(
            "player",
            {}
        )

        club = body.get(
            "club",
            {}
        )

        selected_club = club.get(
            "name"
        )

        selected_league = club.get(
            "league"
        )

        world = build_world(
            selected_club,
            selected_league
        )

        # Jeżeli frontend nie podał klubu,
        # wybieramy pierwszy klub Ekstraklasy.

        if not selected_club:
            selected_club = (
                world["leagues"]["Ekstraklasa"][0]
            )

        if selected_club not in world["clubs"]:
            return jsonify({
                "error": "Nie znaleziono wybranego klubu"
            }), 400

        chosen = world["clubs"][
            selected_club
        ]

        # ====================================================
        # ZAWODNIK
        # ====================================================

        try:
            player_ovr = int(
                player.get(
                    "ovr",
                    48
                )
            )
        except (TypeError, ValueError):
            player_ovr = 48

        try:
            player_year = int(
                player.get(
                    "year",
                    2026
                )
            )
        except (TypeError, ValueError):
            player_year = 2026

        p = {
            "name": player.get(
                "name",
                "Zawodnik"
            ),

            "position": player.get(
                "position",
                "Napastnik"
            ),

            "ovr": player_ovr,

            "year": player_year,

            "club": chosen["name"],

            "league": chosen["league"],

            "stats": player.get(
                "stats",
                {}
            ),

            "value": player.get(
                "value",
                100000
            )
        }

        # ====================================================
        # SESJA
        # ====================================================

        SESSIONS[sid] = {
            "world": world,
            "player": p,
            "history": [],
            "table": {},
            "last_summary": None
        }

        return jsonify({
            "sessionId": sid,
            "engine": "python",

            "club": {
                "name": chosen["name"],
                "league": chosen["league"],
                "ovr": chosen["ovr"]
            }
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# SYMULACJA SEZONU
# ============================================================

@app.route(
    "/api/season",
    methods=["POST"]
)
def simulate_season():

    try:
        body = request.get_json(
            silent=True
        ) or {}

        sid = body.get(
            "sessionId"
        )

        session = SESSIONS.get(
            sid
        )

        if not session:
            return jsonify({
                "error":
                    "Sesja wygasła lub nie istnieje"
            }), 404

        result = season(
            session
        )

        return jsonify({
            "ok": True,
            "summary": result,
            "player": session["player"]
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# STAN SESJI
# ============================================================

@app.route(
    "/api/state",
    methods=["POST"]
)
def get_state():

    try:
        body = request.get_json(
            silent=True
        ) or {}

        sid = body.get(
            "sessionId"
        )

        session = SESSIONS.get(
            sid
        )

        if not session:
            return jsonify({
                "error": "Brak sesji"
            }), 404

        return jsonify({
            "player": session["player"],

            "summary": session.get(
                "last_summary"
            ),

            "history": session["history"]
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# DODATKOWY ENDPOINT - INFORMACJE O KLUBACH
# ============================================================

@app.route(
    "/api/clubs",
    methods=["GET"]
)
def get_clubs():

    try:
        world = build_world()

        result = {}

        for league, names in world["leagues"].items():

            result[league] = []

            for name in names:

                club = world["clubs"][name]

                result[league].append({
                    "name": club["name"],
                    "league": club["league"],
                    "ovr": club["ovr"],
                    "budget": club["budget"],
                    "players": len(
                        club["squad"]
                    )
                })

        return jsonify({
            "ok": True,
            "leagues": result
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# DODATKOWY ENDPOINT - TRANSFERY Z OSTATNIEGO SEZONU
# ============================================================

@app.route(
    "/api/transfers",
    methods=["POST"]
)
def get_transfers():

    try:
        body = request.get_json(
            silent=True
        ) or {}

        sid = body.get(
            "sessionId"
        )

        session = SESSIONS.get(
            sid
        )

        if not session:
            return jsonify({
                "error": "Brak sesji"
            }), 404

        summary = session.get(
            "last_summary"
        )

        if not summary:
            return jsonify({
                "ok": True,
                "transfers": []
            })

        return jsonify({
            "ok": True,
            "transfers": summary.get(
                "transfers",
                []
            )
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# DODATKOWY ENDPOINT - TABELA
# ============================================================

@app.route(
    "/api/standings",
    methods=["POST"]
)
def get_standings():

    try:
        body = request.get_json(
            silent=True
        ) or {}

        sid = body.get(
            "sessionId"
        )

        session = SESSIONS.get(
            sid
        )

        if not session:
            return jsonify({
                "error": "Brak sesji"
            }), 404

        return jsonify({
            "ok": True,
            "standings": session.get(
                "table",
                {}
            )
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# DODATKOWY ENDPOINT - HISTORIA SEZONÓW
# ============================================================

@app.route(
    "/api/history",
    methods=["POST"]
)
def get_history():

    try:
        body = request.get_json(
            silent=True
        ) or {}

        sid = body.get(
            "sessionId"
        )

        session = SESSIONS.get(
            sid
        )

        if not session:
            return jsonify({
                "error": "Brak sesji"
            }), 404

        return jsonify({
            "ok": True,
            "history": session.get(
                "history",
                []
            )
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# USUWANIE SESJI
# ============================================================

@app.route(
    "/api/session/delete",
    methods=["POST"]
)
def delete_session():

    try:
        body = request.get_json(
            silent=True
        ) or {}

        sid = body.get(
            "sessionId"
        )

        if not sid:
            return jsonify({
                "error": "Brak sessionId"
            }), 400

        if sid not in SESSIONS:
            return jsonify({
                "error": "Sesja nie istnieje"
            }), 404

        del SESSIONS[sid]

        return jsonify({
            "ok": True,
            "message": "Sesja usunięta"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# URUCHOMIENIE LOKALNE
# ============================================================

if __name__ == "__main__":

    print(
        "============================================"
    )

    print(
        " FOOTBALL PYTHON ENGINE"
    )

    print(
        "============================================"
    )

    print(
        "Serwer Flask uruchamia się lokalnie."
    )

    print(
        "Adres: http://127.0.0.1:8000"
    )

    print(
        "============================================"
    )

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False
    )
