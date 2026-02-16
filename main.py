from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

# ===== TOKENS =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== MEMORY STORE =====
user_memory = {}


# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aya, dubara likh 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": part}
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass


# ================= TYPING ANIMATION =================
def send_typing(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    # save user message
    user_memory[chat_id].append({"role": "user", "content": user_message})

    # keep last messages
    user_memory[chat_id] = user_memory[chat_id][-12:]

    system_prompt = """
You are ReplyShastra.

A boy will tell you what happened between him and his girlfriend.

Your job:
Write the exact WhatsApp message he should send her.

Style:
- Natural Hinglish
- Soft and mature
- Emotionally understanding

Rules:
- Only the final message
- Maximum 2 short lines
- No advice
- No explanation
- No bullet points
- No coaching
"""

    messages = [{"role": "system", "content": system_prompt}] + user_memory[chat_id]

    try:

        # typing animation (approx 6 sec)
        for _ in range(6):
            send_typing(chat_id)
            time.sleep(1)

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.85
            },
            timeout=45
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        data = response.json()

        if "choices" not in data:
            return "AI thoda busy hai, 20 sec baad bhej 🙂"

        reply = data["choices"][0]["message"]["content"].strip()

        # save AI reply
        user_memory[chat_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai, thoda baad try 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

            # start command
            if user_message.lower() == "/start":
                user_memory[chat_id] = []
                send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, late reply — sab handle karenge.

Apni situation simple likh 👇""")
                return "ok"

            reply = get_ai_reply(chat_id, user_message)
            send_message(chat_id, reply)

    return "ok"


# ================= HOME =================
@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
