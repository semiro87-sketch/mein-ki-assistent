
import json
import os
import re
import psycopg
from flask import Flask, request, render_template_string, session, redirect
from openai import OpenAI
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lokal-nur-zum-testen")
client = OpenAI()
HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#030805"><meta name="apple-mobile-web-app-capable" content="yes">
<title>Matrix AI Command Center</title>
<style>
:root{color-scheme:dark;--bg:#030805;--panel:#07170d;--line:#165c2c;--green:#00ff66;--muted:#83a78e;--white:#f1fff4}
*{box-sizing:border-box}html{background:var(--bg)}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 50% 5%,#0c2816 0%,#030805 55%);color:var(--white);font:15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.13;background:repeating-linear-gradient(0deg,transparent 0,transparent 3px,#1b6a31 4px);z-index:0}
main{position:relative;max-width:650px;margin:auto;padding:calc(22px + env(safe-area-inset-top)) 18px calc(35px + env(safe-area-inset-bottom))}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px}.eyebrow,.mono,.section-head,.small,.chip,.status{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:1.3px;text-transform:uppercase}.eyebrow{font-size:10px;color:var(--green);font-weight:800}h1{font-size:27px;line-height:1.05;letter-spacing:-.9px;margin:7px 0 0;font-weight:900}.online{color:var(--green);border:1px solid #176d34;background:#071f10;padding:8px 11px;border-radius:50px;font-size:10px;white-space:nowrap}.online:before{content:"● ";color:var(--green)}
.orb-wrap{height:236px;display:grid;place-items:center;position:relative}.orbit{position:absolute;width:188px;height:188px;border:1px dashed #12622e;border-radius:50%;animation:spin 32s linear infinite}.orbit:after{content:"";position:absolute;inset:16px;border:1px solid #155b2b;border-radius:50%}.orb{width:136px;height:136px;border-radius:50%;background:radial-gradient(circle at 36% 28%,#e6ffe9 0%,#71ff94 9%,#00f45b 25%,#007e30 52%,#001807 76%);box-shadow:0 0 17px #00ff6677,0 0 58px #00ff6633,inset -16px -20px 22px #001507;animation:pulse 3.2s ease-in-out infinite}.orb:after{content:"";display:block;width:50px;height:50px;border:1px solid #8dffb1;border-radius:50%;position:relative;left:39px;top:38px;box-shadow:0 0 12px #00ff66}.core-label{text-align:center;margin:-6px 0 24px}.core-label strong{display:block;font-size:19px;letter-spacing:1px}.status{color:var(--green);font-size:10px;margin-top:7px}
.panel{background:linear-gradient(150deg,#071b0e,#06120a);border:1px solid #17632f;border-radius:15px;padding:15px;margin:12px 0;box-shadow:0 0 20px #00ff6609}.section-head{color:var(--green);font-size:11px;font-weight:800;margin:25px 0 11px;display:flex;justify-content:space-between;align-items:center}.label{font-size:10px;color:var(--green);font-family:ui-monospace,monospace;letter-spacing:1px;margin-bottom:8px}.field{display:block;width:100%;border:1px solid #215d34;background:#07140c;color:white;border-radius:10px;padding:13px;font:inherit;outline:none;min-height:48px}.field:focus{border-color:var(--green);box-shadow:0 0 0 2px #00ff6622}.field::placeholder{color:#9caea1}button{font:inherit;cursor:pointer}.primary{width:100%;background:linear-gradient(100deg,#00cb52,#00ff73);color:#00200a;border:0;border-radius:10px;padding:13px;font-weight:850;min-height:46px;margin-top:9px}.primary:active{transform:scale(.99)}.quick-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.tile{background:#071b0e;border:1px solid #166c32;border-radius:13px;padding:17px 12px;text-align:left;color:white;width:100%;min-height:115px}.tile-icon{font-size:23px;color:var(--green);display:block;margin-bottom:16px}.tile b{display:block;font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.4px}.tile small{display:block;color:#77ad86;font-size:10px;margin-top:5px}.task{background:#07180d;border:1px solid #185a2c;border-radius:12px;padding:13px;margin:9px 0}.task.hoch{border-color:#9a4b4b}.task.niedrig{opacity:.8}.task-row{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.task-text{line-height:1.4;overflow-wrap:anywhere}.chip{font-size:9px;border:1px solid #24613a;color:#9edbb0;border-radius:6px;padding:4px 6px;white-space:nowrap}.hoch .chip{border-color:#a54848;color:#ff9a9a}.task-actions{display:flex;gap:8px;margin-top:12px}.task-actions form{flex:1}.subbtn{background:#0c2815;color:#a4ffbb;border:1px solid #216f3a;border-radius:8px;width:100%;min-height:38px;font-size:12px;font-weight:700}.subbtn.done{background:#0c391b;color:var(--green)}.notice{white-space:pre-wrap;line-height:1.6;color:#e3ffe9;overflow-wrap:anywhere}.notice h2{margin-top:0;font-size:17px}.muted{color:var(--muted);font-size:12px}.logout{color:#9acaab;font-size:12px;text-decoration:none;border-bottom:1px solid #315b3c}.edit{border-color:#00b64a}.hidden{display:none}.footer{text-align:center;color:#47785a;font-size:10px;margin-top:28px;letter-spacing:2px}
@keyframes pulse{0%,100%{transform:scale(.97);filter:brightness(.9)}50%{transform:scale(1.04);filter:brightness(1.2)}}@keyframes spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.orb,.orbit{animation:none}}@media(max-width:360px){h1{font-size:23px}.orb-wrap{height:210px}main{padding-left:12px;padding-right:12px}}
</style>
</head>
<body><main>
<header class="top"><div><div class="eyebrow">MATRIX // AI SYSTEM</div><h1>COMMAND CENTER</h1></div><div class="online mono">ONLINE</div></header>
<div class="orb-wrap"><div class="orbit"></div><div class="orb" aria-hidden="true"></div></div>
<div class="core-label"><strong>NEURAL CORE</strong><div class="status" id="status">● ASSISTANT READY</div></div>
<section class="panel"><div class="label">SYSTEM INPUT_</div><form method="post" id="questionForm"><input class="field" name="frage" placeholder="Was kann ich für dich tun?" aria-label="Frage an KI" required autocomplete="off"><button class="primary" type="submit">↗ KI-TERMINAL ÖFFNEN</button></form></section>
<div class="quick-grid"><button class="tile" type="button" onclick="document.querySelector('[name=frage]').focus()"><span class="tile-icon">●</span><b>KI TERMINAL</b><small>FRAGEN STELLEN</small></button><form method="post"><input type="hidden" name="tagesplan" value="1"><button class="tile" type="submit"><span class="tile-icon">◎</span><b>MISSION PLAN</b><small>TAGESPLAN ERSTELLEN</small></button></form></div>
{% if antwort %}<section class="panel notice" id="result"><h2>▸ SYSTEM RESPONSE</h2>{{ antwort }}</section>{% endif %}
<div class="section-head"><span>▱ ACTIVE MISSIONS</span><span>+ NEU</span></div>
<section class="panel"><div class="label">NEUE MISSION_</div><form method="post"><input class="field" name="neue_aufgabe" placeholder="z. B. Heute 16:00 einkaufen" required autocomplete="off"><button class="primary" type="submit">+ AUFGABE HINZUFÜGEN</button></form></section>
{% for titel, liste in [('HEUTE', heute), ('MORGEN', morgen), ('SPÄTER', spaeter)] %}
<div class="section-head"><span>{{ titel }}</span><span>{{ liste|length }} MISSION{{ 'S' if liste|length != 1 else '' }}</span></div>
{% for nummer, aufgabe in liste %}<article class="task {{ aufgabe['prioritaet']|e }}"><div class="task-row"><div class="task-text">{{ aufgabe['text'] }}{% if aufgabe.get('uhrzeit') and aufgabe.get('uhrzeit') != 'ohne' %}<div class="muted">◷ {{ aufgabe['uhrzeit'] }}</div>{% endif %}</div><span class="chip">{{ aufgabe['prioritaet']|upper }}</span></div><div class="task-actions"><form method="post"><button class="subbtn" name="bearbeiten" value="{{ nummer }}">✎ BEARBEITEN</button></form><form method="post"><button class="subbtn done" name="erledigt" value="{{ nummer }}">✓ ERLEDIGT</button></form></div></article>{% else %}<p class="muted">Keine Missionen.</p>{% endfor %}{% endfor %}
{% if bearbeiten_aufgabe %}<section class="panel edit" id="edit"><div class="label">MISSION BEARBEITEN_</div><form method="post"><input type="hidden" name="speichern_nummer" value="{{ bearbeiten_aufgabe['nummer'] }}"><input class="field" name="bearbeiten_text" value="{{ bearbeiten_aufgabe['text'] }}" required><button class="primary" type="submit">ÄNDERUNGEN SPEICHERN</button></form></section>{% endif %}
<div class="footer">MATRIX AI // <a class="logout" href="/logout">ABMELDEN ↗</a></div>
</main><script>const f=document.getElementById('questionForm');f.addEventListener('submit',()=>{document.getElementById('status').textContent='◉ KI DENKT …'});if(location.hash==='#edit'){document.getElementById('edit')?.scrollIntoView({behavior:'smooth'})}</script></body></html>
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

@app.route("/login", methods=["GET", "POST"])
def login():
    fehler = ""
    if request.method == "POST":
        passwort = request.form.get("passwort", "")
        if os.environ.get("APP_PASSWORD") and passwort == os.environ.get("APP_PASSWORD"):
            session["angemeldet"] = True
            return redirect("/")
        fehler = "Falsches Passwort."

    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Matrix AI Login</title><meta name="theme-color" content="#030805"><style>body{background:#030805;color:#00ff66;font-family:-apple-system,sans-serif;max-width:440px;margin:15vh auto;padding:24px}h2{font-size:28px}input,button{display:block;width:100%;box-sizing:border-box;padding:15px;margin:12px 0;border-radius:10px;font-size:16px}input{background:#07170d;border:1px solid #17632f;color:white}button{background:#00ff66;color:#00200a;border:0;font-weight:800}</style>
    </head>
    <body>
        <h2>🔐 KI-Assistent</h2>
        <form method="post">
            <input type="password" name="passwort" placeholder="Passwort" required>
            <button type="submit">Anmelden</button>
        </form>
        <p>{fehler}</p>
    </body>
    </html>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def startseite():
    if not session.get("angemeldet"):
        return redirect("/login")

    aufgaben = lade_aufgaben()
    antwort = ""
    bearbeiten_aufgabe = None

    if request.method == "POST":
        neue_aufgabe = request.form.get("neue_aufgabe", "").strip()
        speichern_nummer = request.form.get("speichern_nummer")
        bearbeiten = request.form.get("bearbeiten")
        erledigt = request.form.get("erledigt")

        if neue_aufgabe:
            prioritaet = "normal"
            faelligkeit = "ohne"
            uhrzeit = "ohne"
            treffer = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", neue_aufgabe)
            if treffer:
                uhrzeit = treffer.group(0)
            klein = neue_aufgabe.lower()
            if "heute" in klein:
                faelligkeit = "heute"
            elif "morgen" in klein:
                faelligkeit = "morgen"
            if "nicht dringend" in klein or "später" in klein:
                prioritaet = "niedrig"
            elif "wichtig" in klein or "dringend" in klein:
                prioritaet = "hoch"
            if os.environ.get("DATABASE_URL"):
                with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO aufgaben (text, prioritaet, faelligkeit, uhrzeit) VALUES (%s, %s, %s, %s)", (neue_aufgabe, prioritaet, faelligkeit, uhrzeit))
            else:
                aufgaben.append({"text": neue_aufgabe, "prioritaet": prioritaet, "faelligkeit": faelligkeit, "uhrzeit": uhrzeit})
                with open("aufgaben.json", "w") as datei:
                    json.dump(aufgaben, datei, ensure_ascii=False, indent=2)
            aufgaben = lade_aufgaben()
            antwort = "✓ Mission hinzugefügt."

        elif speichern_nummer is not None and speichern_nummer.isdigit():
            nummer = int(speichern_nummer)
            neuer_text = request.form.get("bearbeiten_text", "").strip()
            if 0 <= nummer < len(aufgaben) and neuer_text:
                aufgaben[nummer]["text"] = neuer_text
                if os.environ.get("DATABASE_URL"):
                    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
                        with conn.cursor() as cur:
                            cur.execute("UPDATE aufgaben SET text = %s WHERE id = %s", (neuer_text, aufgaben[nummer]["id"]))
                else:
                    with open("aufgaben.json", "w") as datei:
                        json.dump(aufgaben, datei, ensure_ascii=False, indent=2)
                aufgaben = lade_aufgaben()
                antwort = "✓ Mission aktualisiert."

        elif bearbeiten is not None and bearbeiten.isdigit():
            nummer = int(bearbeiten)
            if 0 <= nummer < len(aufgaben):
                bearbeiten_aufgabe = dict(aufgaben[nummer], nummer=nummer)

        elif erledigt is not None and erledigt.isdigit():
            nummer = int(erledigt)
            if 0 <= nummer < len(aufgaben):
                if os.environ.get("DATABASE_URL"):
                    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM aufgaben WHERE id = %s", (aufgaben[nummer]["id"],))
                else:
                    aufgaben.pop(nummer)
                    with open("aufgaben.json", "w") as datei:
                        json.dump(aufgaben, datei, ensure_ascii=False, indent=2)
                aufgaben = lade_aufgaben()
                antwort = "✓ Mission abgeschlossen."

        elif request.form.get("tagesplan"):
            if not aufgaben:
                antwort = "Du hast aktuell keine Aufgaben."
            else:
                aufgaben_text = "\n".join(f"- {a['text']} (Priorität: {a['prioritaet']}, Fälligkeit: {a['faelligkeit']}, Uhrzeit: {a.get('uhrzeit', 'ohne')})" for a in aufgaben)
                try:
                    ergebnis = client.responses.create(model="gpt-5", instructions="Erstelle einen kurzen, realistischen Tagesplan aus meinen Aufgaben. Priorisiere wichtige und heute fällige Aufgaben.", input=aufgaben_text)
                    antwort = ergebnis.output_text
                except Exception:
                    app.logger.exception("Tagesplan konnte nicht erstellt werden")
                    antwort = "Der Tagesplan ist momentan nicht verfügbar. Bitte später erneut versuchen."

        else:
            frage = request.form.get("frage", "").strip()
            if frage:
                try:
                    ergebnis = client.responses.create(model="gpt-5", instructions="Du bist mein persönlicher KI-Assistent. Antworte auf Deutsch, freundlich und verständlich.", input=frage)
                    antwort = ergebnis.output_text
                except Exception:
                    app.logger.exception("KI-Anfrage fehlgeschlagen")
                    antwort = "Die KI ist momentan nicht erreichbar. Bitte später erneut versuchen."

    heute = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "heute"]
    morgen = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") == "morgen"]
    spaeter = [(i, a) for i, a in enumerate(aufgaben) if a.get("faelligkeit") not in ("heute", "morgen")]
    return render_template_string(HTML, antwort=antwort, heute=heute, morgen=morgen, spaeter=spaeter, bearbeiten_aufgabe=bearbeiten_aufgabe)

@app.route("/api/frage", methods=["POST"])
def api_frage():
    daten = request.get_json(silent=True) or {}
    frage = daten.get("frage", "").strip()

    if not frage:
        return {"antwort": "Bitte stelle mir eine Frage."}, 400

    ergebnis = client.responses.create(
        model="gpt-5",
        instructions="Du bist mein persönlicher KI-Assistent. Antworte auf Deutsch, freundlich und verständlich.",
        input=frage
    )

    return {"antwort": ergebnis.output_text}
@app.route("/api/aufgaben", methods=["GET"])
def api_aufgaben():
    aufgaben = lade_aufgaben()
    return {"aufgaben": aufgaben}
@app.route("/api/aufgaben", methods=["POST"])
def api_aufgabe_hinzufuegen():
    daten = request.get_json(silent=True) or {}
    text = daten.get("text", "").strip()

    if not text:
        return {"fehler": "Aufgabe darf nicht leer sein."}, 400

    aufgaben = lade_aufgaben()

    faelligkeit = "ohne"
    if "heute" in text.lower():
        faelligkeit = "heute"
    elif "morgen" in text.lower():
        faelligkeit = "morgen"
    prioritaet = "normal"
    if "nicht dringend" in text.lower() or "später" in text.lower():
        prioritaet = "niedrig"
    elif "wichtig" in text.lower() or "dringend" in text.lower():
        prioritaet = "hoch"

    neue_aufgabe = {
        "text": text,
        "prioritaet": prioritaet,
        "faelligkeit": faelligkeit,
        "uhrzeit": "ohne"
    }

    aufgaben.append(neue_aufgabe)
    if os.environ.get("DATABASE_URL"):
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO aufgaben (text, prioritaet, faelligkeit, uhrzeit)
                       VALUES (%s, %s, %s, %s)""",
                    (text, prioritaet, faelligkeit, "ohne")
                )
    else:
        with open("aufgaben.json", "w") as datei:
            json.dump(aufgaben, datei, ensure_ascii=False, indent=2)
    return {"erfolg": True}
@app.route("/api/tagesplan", methods=["GET"])
def api_tagesplan():
    aufgaben = lade_aufgaben()

    if not aufgaben:
        return {"tagesplan": "Du hast aktuell keine Aufgaben."}

    aufgaben_text = "\n".join(
        f"- {a['text']} (Priorität: {a['prioritaet']}, Fälligkeit: {a['faelligkeit']}, Uhrzeit: {a.get('uhrzeit', 'ohne')})"
        for a in aufgaben
    )

    ergebnis = client.responses.create(
        model="gpt-5",
        instructions="Erstelle einen kurzen, realistischen Tagesplan aus meinen Aufgaben. Priorisiere wichtige und heute fällige Aufgaben.",
        input=aufgaben_text
    )

    return {"tagesplan": ergebnis.output_text}


@app.route("/api/aufgaben/<int:aufgabe_id>", methods=["DELETE"])
def api_aufgabe_erledigen(aufgabe_id):
    if os.environ.get("DATABASE_URL"):
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM aufgaben WHERE id = %s", (aufgabe_id,))
        return {"erfolg": True}

    return {"fehler": "Löschen ist lokal noch nicht verfügbar."}, 400


if __name__ == "__main__":
    port=int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
