import os
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SITE_URL = os.getenv("SITE_URL")

# ---------------- TELEGRAM FUNCTIONS ---------------- #

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
    requests.post(url, json={
        "chat_id": chat_id,
        "action": "typing"
    })

# ---------------- AI BRAIN ---------------- #

def ask_groq(prompt, temp=0.7, tokens=700):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": tokens
    }

    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=40
    ).json()

    return res["choices"][0]["message"]["content"]

# ---------------- SMART REPLY SYSTEM ---------------- #

def get_ai_reply(user_message):

    # STEP 1 — ANALYSIS (AI sochega)
    analysis_prompt = f"""
Tu ek smart Indian ladka dost hai jo relationship samajhta hai.

User problem:
{user_message}

Seedha reply mat de.

Pehle analyse kar aur strictly is format me likh:

PROBLEM:
(real issue kya hai)

GIRL PSYCHOLOGY:
(ladki kyu gussa hui emotionally)

USER MISTAKE:
(user ne kya galti kari)

BEST ACTION:
(user ko ab kya behaviour rakhna chahiye)
"""

    try:
        analysis = ask_groq(analysis_prompt, 0.3, 400)

        # STEP 2 — FINAL HUMAN REPLY
        final_prompt = f"""
Tu ab uska real best friend hai.

Yeh analysis hai:
{analysis}

Ab Hinglish me usko reply de:

Rules:
- natural bol
- bhai wali tone
- pehle usko samjha
- fir short practical advice
- last me EXACT message likh jo wo ladki ko bheje
- "beta", "dear", "user" mat bol
- over philosophical mat ho
- realistic ho
"""

        final_reply = ask_groq(final_prompt, 0.7, 700)
        return final_reply

    except Exception as e:
        print("AI ERROR:", e)
        return "Bhai thoda network issue aa gaya 😅 20 sec baad fir likh."

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return "ReplyShastra Running"

@app.route("/setwebhook")
def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={SITE_URL}/webhook"
    return requests.get(url).text

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"ok": True})

    if "message" not in data:
        return jsonify({"ok": True})

    message = data["message"]
    chat_id = message["chat"]["id"]

    if "text" not in message:
        return jsonify({"ok": True})

    text = message["text"]

    print("USER:", text)

    # start command
    if text == "/start":
        send_message(chat_id, "Bhai welcome 😎\nApni problem detail me bata, main hoon na.")
        return jsonify({"ok": True})

    # typing simulation
    send_typing(chat_id)
    time.sleep(2)

    ai_reply = get_ai_reply(text)
    send_message(chat_id, ai_reply)

    return jsonify({"ok": True})

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
