
import json
import os
import re
import psycopg
from flask import Flask, request, render_template_string
from openai import OpenAI
app = Flask(__name__)
client = OpenAI()
HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mein KI-Assistent</title>
<style>
body {
    margin: 0;
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(160deg, #07111f, #101b33, #151229);
    color: white;
}
.container {
    max-width: 520px;
    margin: 0 auto;
    padding: 28px 20px;
}
.core {
    width: 86px;
    height: 86px;
    margin: 20px auto;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #ffffff, #7dd3fc 20%, #6366f1 55%, #312e81);
}
.core {
    box-shadow:
        0 0 20px rgba(125, 211, 252, 0.7),
        0 0 50px rgba(99, 102, 241, 0.45);
}
.core {
    animation: pulse 3s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.85; }
    50% { transform: scale(1.08); opacity: 1; }
}
h1 {
    text-align: center;
    font-size: 28px;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}
input {
    width: 100%;
    box-sizing: border-box;
    padding: 16px;
    margin: 8px 0;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    background: rgba(255,255,255,0.08);
    color: white;
    font-size: 16px;
}
button {
    width: 100%;
    padding: 14px 18px;
    border: 0;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
}
button {
    background: linear-gradient(135deg, #38bdf8, #6366f1);
    color: white;
    box-shadow: 0 6px 24px rgba(99, 102, 241, 0.3);
}
.task {
    margin: 8px 0;
    padding: 8px 10px;
    border-radius: 20px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(14px);
}
.task p {
    margin: 2px 0 4px 0;
    font-size: 14px;
    line-height: 1.3;
}
.task button {
    padding: 6px 9px;
    font-size: 12px;
    border-radius: 9px;
}
.status {
    text-align: center;
    font-size: 12px;
    letter-spacing: 2px;
    margin-bottom: 22px;
    opacity: 0.8;
}
.task.hoch {
    border: 1px solid rgba(248, 113, 113, 0.65);
    box-shadow: 0 0 24px rgba(248, 113, 113, 0.22);
.task.niedrig {
    opacity: 0.65;
}
.badge {
    float: right;
    padding: 3px 7px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    background: rgba(255,255,255,0.1);
}
.task.hoch .badge {
    background: rgba(248,113,113,0.22);
    color: #ff8a8a;
    box-shadow: 0 0 12px rgba(248,113,113,0.35);
    animation: badgePulse 1.8s ease-in-out infinite;
}

@keyframes badgePulse {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 1; }
}
.bereich {
    margin: 22px 0 8px;
    font-size: 12px;
    letter-spacing: 2px;
    opacity: 0.65;
}

@media (max-width: 600px) {
    form {
        width: 100%;
    }

    body {
        padding: 12px;
    }

    .container {
        width: 100%;
        max-width: 100%;
    }

    input, button {
        width: 100%;
        min-height: 48px;
        font-size: 16px;
        box-sizing: border-box;
    }

    .task {
        padding: 14px;
        margin: 10px 0;
    }

    .bereich {
        margin: 20px 4px 8px;
    }
}

</style>
</head>
<body>
<div class="core"></div>
<div class="status">● KI ONLINE</div>
<div class="container">
<h1>🤖 Mein KI-Assistent</h1>
<form method="post" onsubmit="kiDenkt()">
    <input name="frage" placeholder="Was möchtest du wissen?" autocomplete="off">
    <button type="submit">Senden</button>
</form>
<form method="post">
<input name="neue_aufgabe" placeholder="Neue Aufgabe">
<button type="submit">➕ Aufgabe hinzufügen</button>
</form>

<form method="post">
    <button type="submit" name="tagesplan" value="1">🧠 Tagesplan erstellen</button>
</form>
<h2>📋 Meine Aufgaben</h2>
<h3 class="bereich">HEUTE</h3>
{% for nummer, aufgabe in heute %}
<div class="task {{ aufgabe['prioritaet'] }}">
<p>• {{ aufgabe['text'] }} {% if aufgabe.get('uhrzeit') and aufgabe.get('uhrzeit') != 'ohne' %}⏰ {{ aufgabe['uhrzeit'] }}{% endif %} <span class="badge">{{ aufgabe['prioritaet']|upper }}</span></p>
<form method="post">
<input type="hidden" name="erledigt" value="{{ nummer  }}">
<button type="submit">✅ Erledigt</button>
</form>
</div>
{% endfor %}
<h3 class="bereich">MORGEN</h3>
{% for nummer, aufgabe in morgen %}
<div class="task {{ aufgabe['prioritaet'] }}">
<p>• {{ aufgabe['text'] }} {% if aufgabe.get('uhrzeit') and aufgabe.get('uhrzeit') != 'ohne' %}⏰ {{ aufgabe['uhrzeit'] }}{% endif %} <span class="badge">{{ aufgabe['prioritaet']|upper }}</span></p>
<form method="post">
<input type="hidden" name="erledigt" value="{{ nummer  }}">
<button type="submit">✅ Erledigt</button>
</form>
</div>
{% endfor %}
<h3 class="bereich">SPÄTER</h3>
{% for nummer, aufgabe in spaeter %}
<div class="task {{ aufgabe['prioritaet'] }}">
<p>• {{ aufgabe['text'] }} {% if aufgabe.get('uhrzeit') and aufgabe.get('uhrzeit') != 'ohne' %}⏰ {{ aufgabe['uhrzeit'] }}{% endif %} <span class="badge">{{ aufgabe['prioritaet']|upper }}</span></p>
<form method="post">
<input type="hidden" name="erledigt" value="{{ nummer }}">
<button type="submit">✅ Erledigt</button>
</form>
</div>
{% endfor %}

{% if antwort %}
<div>
    <h2>Antwort:</h2>
    <p>{{ antwort }}</p>
</div>
{% endif %}
</div>
<script>
function kiDenkt() {
    document.querySelector(".status").textContent = "◉ KI DENKT …";
}
</script>
</body>
</html>
"""
def lade_aufgaben():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS aufgaben (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        prioritaet TEXT NOT NULL,
                        faelligkeit TEXT NOT NULL,
                        uhrzeit TEXT
                    )
                """)
                cur.execute("""
                    SELECT id, text, prioritaet, faelligkeit, uhrzeit
                    FROM aufgaben
                    ORDER BY id
                """)
                return [
                    {
                        "id": row[0],
                        "text": row[1],
                        "prioritaet": row[2],
                        "faelligkeit": row[3],
                        "uhrzeit": row[4] or "ohne"
                    }
                    for row in cur.fetchall()
                ]

    try:
        with open("aufgaben.json", "r") as datei:
            return json.load(datei)
    except FileNotFoundError:
        return []

@app.route("/", methods=["GET", "POST"])
def startseite():
    aufgaben = lade_aufgaben()
    heute = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "heute"]
    morgen = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "morgen"]
    spaeter = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "ohne"]
    antwort = ""

    if request.method == "POST":
        neue_aufgabe = request.form.get("neue_aufgabe", "").strip()
        if neue_aufgabe:
            prioritaet = "normal"
            faelligkeit = "ohne"
            uhrzeit = "ohne"
            treffer = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", neue_aufgabe)
            if treffer:
                uhrzeit = treffer.group(0)
            if "heute" in neue_aufgabe.lower():
                faelligkeit = "heute"
            elif "morgen" in neue_aufgabe.lower():
                faelligkeit = "morgen"
            if "wichtig" in neue_aufgabe.lower() or "dringend" in neue_aufgabe.lower():
                prioritaet = "hoch"
            elif "später" in neue_aufgabe.lower() or "nicht dringend" in neue_aufgabe.lower():
                prioritaet = "niedrig"
            if os.environ.get("DATABASE_URL"):
                with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO aufgaben (text, prioritaet, faelligkeit, uhrzeit) VALUES (%s, %s, %s, %s)",
                            (neue_aufgabe, prioritaet, faelligkeit, uhrzeit)
                        )
                aufgaben = lade_aufgaben()
            else:
                aufgaben.append({
                    "text": neue_aufgabe,
                    "prioritaet": prioritaet,
                    "faelligkeit": faelligkeit,
                    "uhrzeit": uhrzeit
                })
                with open("aufgaben.json", "w") as datei:
                    json.dump(aufgaben, datei, ensure_ascii=False, indent=2)
            antwort = "➕ Aufgabe hinzugefügt."
            heute = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "heute"]
            spaeter = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "ohne"]
            morgen = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "morgen"]
            return render_template_string(HTML, antwort=antwort, aufgaben=aufgaben, heute=heute, morgen=morgen, spater=spaeter)

        erledigt = request.form.get("erledigt")
        if erledigt is not None:
            nummer = int(erledigt)
            if 0 <= nummer < len(aufgaben):
                if os.environ.get("DATABASE_URL"):
                    aufgabe_id = aufgaben[nummer]["id"]
                    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM aufgaben WHERE id = %s", (aufgabe_id,))
                    aufgaben = lade_aufgaben()
                else:
                    aufgaben.pop(nummer)
                    with open("aufgaben.json", "w") as datei:
                        json.dump(aufgaben, datei, ensure_ascii=False, indent=2)
                antwort = "✅ Aufgabe erledigt."
                heute = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "heute"]
                morgen = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "morgen"]
                spaeter = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "ohne"]
                return render_template_string(HTML, antwort=antwort, aufgaben=aufgaben, heute=heute, morgen=morgen, spater=spaeter)
        if request.form.get("tagesplan"):
            aufgaben_text = "\n".join(
                f"- {a['text']} (Priorität: {a['prioritaet']}, Fälligkeit: {a['faelligkeit']}, Uhrzeit: {a.get('uhrzeit', 'ohne')})"                for a in aufgaben
            )

            ergebnis = client.responses.create(
                model="gpt-5",
                instructions="Erstelle einen kurzen, realistischen Tagesplan aus meinen Aufgaben. Priorisiere wichtige und heute fällige Aufgaben.",
                input=aufgaben_text
            )
            antwort = ergebnis.output_text
        frage = request.form.get("frage", "").strip()

        if frage:
            ergebnis = client.responses.create(
                model="gpt-5",
                instructions="Du bist mein persönlicher KI-Assistent. Antworte auf Deutsch, freundlich und verständlich.",
                input=frage
            )
            antwort = ergebnis.output_text

    return render_template_string(HTML, antwort=antwort, aufgaben=aufgaben, heute=heute, morgen=morgen, spaeter=spaeter)


if __name__ == "__main__":
    port=int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
