from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    # Telegram 4096 char limit → hum 3500 pe split karenge
    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": part
        }
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass


# ================= AI REPLY =================
def get_ai_reply(user_message):

    system_prompt = """
You are ReplyShastra.

You are NOT an assistant, NOT a therapist, NOT a coach.

You are a 24 year old Indian boy helping another boy with his relationship problems like a real friend.

You talk casually like a normal Indian guy on WhatsApp/Telegram.

VERY IMPORTANT RULES:

- Talk in natural Hinglish
- No long lectures
- No motivational lines
- No formal language
- No bullet points
- No multiple options
- No "it depends"
- Max 5-6 lines explanation

Your response structure MUST be:

1) First explain what girl is likely thinking (simple psychology)
2) Then clearly tell what he should do RIGHT NOW
3) Then give EXACT message he should send (copy-paste)

The final ready message MUST be inside quotes.

Example style:

Samajh kya ho raha hai — woh hurt hai ya wait kar rahi hai ki tu initiate kare.

Ab tu call nahi karega. 5-6 ghante kuch nahi bhejna.

Uske baad ye bhej:

"Achha sun, agar busy ho ya thoda space chahiye toh le lo. Bas itna bata dena sab theek hai, I’m here."
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.8,
                "max_tokens": 700,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()

        return "Network thoda slow hai… fir se bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… 20 sec baad try karo 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        if "message" not in data:
            return "ok"

        message = data["message"]
        chat_id = message["chat"]["id"]

        # /start greeting
        if "text" in message and message["text"].lower() == "/start":
            greeting = """Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, crush — sab handle karenge.

Apni situation detail me bata 👇
(Main tujhe exact samjhaunga + ready message bhi dunga)"""

            send_message(chat_id, greeting)
            return "ok"

        if "text" not in message:
            return "ok"

        user_message = message["text"]

        reply = get_ai_reply(user_message)
        send_message(chat_id, reply)

        return "ok"

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ok"


# ================= HOME =================
@app.route("/")
def home():
    return "ReplyShastra running"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
