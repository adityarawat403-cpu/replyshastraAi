from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# ================== CONFIG ==================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ================ AI FUNCTION ================
def ask_ai(user_message):

    system_prompt = """
You are ReplyShastra — a calm, masculine, psychologically sharp relationship advisor for men.

You are NOT an AI.
You are a real Indian elder brother type person.

Rules:
- Reply in Hinglish
- No long paragraphs
- 2–4 short chat messages style (like WhatsApp)
- First understand situation
- Ask questions first before advice
- Talk natural and human
- No lecture
- No therapist tone
- Minimal emoji only sometimes 🙂

Flow:
1) emotionally connect
2) ask what exactly happened
3) then slowly guide
"""

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_message}
        ],
        "temperature":0.7
    }

    response = requests.post(url, headers=headers, json=payload)

    try:
        reply = response.json()["choices"][0]["message"]["content"]
    except:
        reply = "Network thoda slow hai bhai, ek baar fir likh."

    return reply


# ================= CHAT API =================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message","")

    if not user_message:
        return jsonify({"reply":"Apni situation likh..."})

    ai_reply = ask_ai(user_message)

    return jsonify({"reply": ai_reply})


# ================= ROOT =================
@app.route("/")
def home():
    return "ReplyShastra WebApp Running"
