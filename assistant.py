from openai import OpenAI
import json

client = OpenAI()


try:
    with open("aufgaben.json", "r") as datei:
        aufgaben = json.load(datei)
except FileNotFoundError:
    aufgaben = []
for i, aufgabe in enumerate(aufgaben):
    if isinstance(aufgabe, str):
        aufgaben[i] = {"text": aufgabe, "prioritaet": "normal"}
system_prompt = """
Du bist mein persönlicher KI-Assistent.

Deine Aufgaben:
- Beantworte meine allgemeinen Fragen.
- Hilf mir bei der Organisation meines Tages.
- Wenn ich Aufgaben nenne, erkenne diese und hilf mir, sie zu strukturieren.
- Hilf mir, Prioritäten zu setzen.
- Erstelle auf Wunsch einen realistischen Tagesplan.
- Berücksichtige feste Termine und Pausen.
- Antworte auf Deutsch.
- Sei freundlich, praktisch und verständlich.
"""

print("🤖 Dein persönlicher Assistent ist gestartet!")
print("Befehle: 'aufgabe: ...', 'aufgaben', 'ende'")
print()

while True:
    frage = input("Du: ")

    if frage.lower() == "ende":
        print("Bis bald! 👋")
        break

    if frage.lower() == "aufgaben":
        if aufgaben:
            print("\n📋 Deine Aufgaben:")
            for nummer, aufgabe in enumerate(aufgaben, 1):
                print(f"{nummer}. {aufgabe['text']} — Priorität: {aufgabe['prioritaet']}")
        else:
            print("\n📋 Du hast noch keine Aufgaben gespeichert.")
        print()
        continue
    if frage.lower() == "tagesplan":
        if not aufgaben:
            print("\n📅 Du hast noch keine Aufgaben für einen Tagesplan.\n")
            continue

        aufgaben_text = "\n".join(
            f"- {a.get('text', '')} | Priorität: {a.get('prioritaet', 'normal')} | Fälligkeit: {a.get('faelligkeit', 'ohne')}"
            for a in aufgaben
        )

        prompt = f"""
Erstelle mir aus meinen gespeicherten Aufgaben einen realistischen Tagesplan.

Berücksichtige:
- Aufgaben mit hoher Priorität zuerst.
- Aufgaben mit Fälligkeit heute besonders berücksichtigen.
- Plane sinnvolle Pausen ein.
- Erstelle einen übersichtlichen Ablauf.
- Erfinde keine festen Termine oder Uhrzeiten, wenn ich keine angegeben habe.

Meine Aufgaben:
{aufgaben_text}
"""

        antwort = client.responses.create(
            model="gpt-5",
            instructions=system_prompt,
            input=prompt
        )

        print("\n📅 Dein Tagesplan:\n")
        print(antwort.output_text)
        print()
        continue
    if frage.lower().startswith("erledigt "):
        nummer_text = frage[9:].strip()
        if nummer_text.isdigit(): 
            nummer = int(nummer_text)
            if 1 <= nummer <= len(aufgaben):
                erledigte_aufgabe = aufgaben.pop(nummer - 1)
                with open("aufgaben.json", "w") as datei:
                    json.dump(aufgaben, datei, ensure_ascii=False, indent=2)
                print(f"✅ Erledigt: {erledigte_aufgabe['text']}")
            else:
                print("Diese Aufgabennummer gibt es nicht.")
        else:
                print("Bitte gib eine Nummer ein, zum Beispiel: erledigt 2")
        continue

    if frage.lower().startswith("aufgabe:"):
        aufgabe = frage[8:].strip()
        faelligkeit = "ohne"
        prioritaet = "normal"

        if "heute" in aufgabe.lower():
            faelligkeit = "heute"
        elif "morgen" in aufgabe.lower():
            faelligkeit = "morgen"

        if "wichtig" in aufgabe.lower() or "dringend" in aufgabe.lower():
            prioritaet = "hoch"
        elif "später" in aufgabe.lower() or "nicht dringend" in aufgabe.lower():
            prioritaet = "niedrig"

        if aufgabe:
            aufgaben.append({
                "text": aufgabe,
                "prioritaet": prioritaet,
                "faelligkeit": faelligkeit
            })

            with open("aufgaben.json", "w") as datei:
                json.dump(aufgaben, datei, ensure_ascii=False, indent=2)

            print(f"✅ Aufgabe gespeichert: {aufgabe}")
            print(f"📅 Fälligkeit: {faelligkeit}")
            print(f"⭐ Priorität: {prioritaet}\n")
        else:
            print("Bitte schreibe nach 'aufgabe:' noch eine Aufgabe.\n")

        continue
    antwort = client.responses.create(
        model="gpt-5",
        instructions=system_prompt,
        input=frage
    )

    print("\nAssistent:", antwort.output_text)
    print()

