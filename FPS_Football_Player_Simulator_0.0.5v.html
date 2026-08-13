<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FPS Football Player Simulator 0.1.0v by.mEmmor</title>

<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        font-family: Arial, sans-serif;
        background: #10141c;
        color: white;
    }

    .game {
        max-width: 900px;
        margin: auto;
        padding: 20px;
    }

    h1 {
        text-align: center;
        margin-bottom: 5px;
    }

    .version {
        text-align: center;
        color: #8f9aaa;
        margin-bottom: 20px;
    }

    .card {
        background: #191f2b;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 5px 20px #0005;
    }

    .stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }

    .stat {
        background: #242b39;
        padding: 12px;
        border-radius: 10px;
    }

    .bar {
        height: 8px;
        background: #11151d;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 6px;
    }

    .fill {
        height: 100%;
        background: #35c759;
        width: 0%;
    }

    button {
        width: 100%;
        padding: 14px;
        margin-top: 8px;
        border: 0;
        border-radius: 10px;
        background: #287cff;
        color: white;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }

    button:hover {
        background: #1768df;
    }

    button.secondary {
        background: #343d4d;
    }

    .event {
        font-size: 18px;
        line-height: 1.5;
    }

    .money {
        color: #ffd84d;
        font-weight: bold;
    }

    .positive {
        color: #43dc72;
    }

    .negative {
        color: #ff5757;
    }

    .footer {
        text-align: center;
        color: #687385;
        font-size: 13px;
        margin-top: 25px;
    }
</style>
</head>

<body>

<div class="game">

    <h1>⚽ FPS Football Player Simulator</h1>
    <div class="version">0.1.0v by.mEmmor</div>

    <div class="card">
        <h2 id="playerName">Nowy zawodnik</h2>
        <p>
            Wiek: <span id="age">17</span> |
            Klub: <span id="club">Akademia FC</span>
        </p>
        <p>
            Pozycja: <span id="position">Napastnik</span>
        </p>
        <p>
            Pieniądze: <span class="money">€<span id="money">500</span></span>
        </p>
    </div>

    <div class="card">
        <h2>📊 Statystyki</h2>

        <div class="stats">

            <div class="stat">
                Kondycja: <span id="fitness">50</span>
                <div class="bar">
                    <div class="fill" id="fitnessBar"></div>
                </div>
            </div>

            <div class="stat">
                Umiejętności: <span id="skill">50</span>
                <div class="bar">
                    <div class="fill" id="skillBar"></div>
                </div>
            </div>

            <div class="stat">
                Reputacja: <span id="reputation">10</span>
                <div class="bar">
                    <div class="fill" id="reputationBar"></div>
                </div>
            </div>

            <div class="stat">
                Relacja z trenerem: <span id="coach">50</span>
                <div class="bar">
                    <div class="fill" id="coachBar"></div>
                </div>
            </div>

        </div>
    </div>

    <div class="card">
        <h2>📅 Kariera</h2>
        <p>
            Sezon: <b id="season">1</b>
            &nbsp; | &nbsp;
            Tydzień: <b id="week">1</b>
        </p>
    </div>

    <div class="card">
        <h2>💭 Decyzja</h2>

        <div class="event" id="event">
            Trener zaproponował Ci dodatkowy trening.
            Co robisz?
        </div>

        <button onclick="train()">💪 Idę na trening</button>
        <button onclick="rest()" class="secondary">😴 Odpoczywam</button>
        <button onclick="talkCoach()" class="secondary">🗣️ Rozmawiam z trenerem</button>
    </div>

    <div class="card">
        <h2>📜 Dziennik kariery</h2>
        <div id="log">
            <p>Kariera rozpoczęta.</p>
        </div>
    </div>

    <div class="footer">
        FPS Football Player Simulator 0.1.0v by.mEmmor
    </div>

</div>

<script>

let player = {
    name: "Nowy zawodnik",
    age: 17,
    club: "Akademia FC",
    position: "Napastnik",

    money: 500,

    fitness: 50,
    skill: 50,
    reputation: 10,
    coach: 50,

    season: 1,
    week: 1
};

function clamp(value) {
    return Math.max(0, Math.min(100, value));
}

function update() {

    document.getElementById("playerName").textContent = player.name;
    document.getElementById("age").textContent = player.age;
    document.getElementById("club").textContent = player.club;
    document.getElementById("position").textContent = player.position;
    document.getElementById("money").textContent = player.money;

    document.getElementById("fitness").textContent = player.fitness;
    document.getElementById("skill").textContent = player.skill;
    document.getElementById("reputation").textContent = player.reputation;
    document.getElementById("coach").textContent = player.coach;

    document.getElementById("fitnessBar").style.width =
        player.fitness + "%";

    document.getElementById("skillBar").style.width =
        player.skill + "%";

    document.getElementById("reputationBar").style.width =
        player.reputation + "%";

    document.getElementById("coachBar").style.width =
        player.coach + "%";

    document.getElementById("season").textContent =
        player.season;

    document.getElementById("week").textContent =
        player.week;
}

function nextWeek() {

    player.week++;

    if (player.week > 52) {
        player.week = 1;
        player.season++;
        player.age++;

        addLog(
            "🎂 Rozpoczął się nowy sezon. Masz teraz " +
            player.age + " lat."
        );
    }

    update();
}

function addLog(text) {

    const log = document.getElementById("log");

    const p = document.createElement("p");
    p.innerHTML = text;

    log.prepend(p);
}

function train() {

    player.skill = clamp(player.skill + random(2, 5));
    player.fitness = clamp(player.fitness - random(2, 5));
    player.coach = clamp(player.coach + random(1, 3));

    document.getElementById("event").innerHTML =
        "🔥 Dobry trening! Twoje umiejętności wzrosły.";

    addLog(
        "<span class='positive'>💪 Trening: +umiejętności, +relacja z trenerem.</span>"
    );

    randomEvent();
    nextWeek();
}

function rest() {

    player.fitness = clamp(player.fitness + random(5, 10));
    player.skill = clamp(player.skill - random(0, 1));

    document.getElementById("event").innerHTML =
        "😴 Odpocząłeś i odzyskałeś siły.";

    addLog(
        "<span class='positive'>😴 Odpoczynek: odzyskano kondycję.</span>"
    );

    randomEvent();
    nextWeek();
}

function talkCoach() {

    player.coach = clamp(player.coach + random(3, 7));

    document.getElementById("event").innerHTML =
        "🗣️ Rozmowa z trenerem przebiegła dobrze.";

    addLog(
        "<span class='positive'>🗣️ Relacja z trenerem wzrosła.</span>"
    );

    randomEvent();
    nextWeek();
}

function randomEvent() {

    const chance = Math.random();

    if (chance < 0.15) {

        player.reputation =
            clamp(player.reputation + random(2, 5));

        document.getElementById("event").innerHTML =
            "⭐ Lokalny dziennikarz napisał o Twoim rozwoju!";

        addLog(
            "<span class='positive'>⭐ Reputacja wzrosła.</span>"
        );
    }

    else if (chance < 0.25) {

        player.money += random(50, 150);

        document.getElementById("event").innerHTML =
            "💰 Otrzymałeś premię za dobre zachowanie.";

        addLog(
            "<span class='positive'>💰 Otrzymano premię.</span>"
        );
    }

    else if (chance < 0.32) {

        player.fitness =
            clamp(player.fitness - random(3, 8));

        document.getElementById("event").innerHTML =
            "🤕 Czujesz lekkie zmęczenie po ostatnich dniach.";

        addLog(
            "<span class='negative'>🤕 Kondycja spadła.</span>"
        );
    }
}

function random(min, max) {
    return Math.floor(
        Math.random() * (max - min + 1)
    ) + min;
}

update();

</script>

</body>
</html>
