from flask import Flask, request
import requests
import os
from collections import defaultdict

app = Flask(__name__)

# ================== TOKENS ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ================== CHAT MEMORY ==================
# har user ka alag conversation memory
chat_memory = defaultdict(list)

# ================== SEND MESSAGE ==================
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    # Telegram limit handling
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

# ================== AI REPLY ==================
def get_ai_reply(user_message, chat_id):
    try:
        # user message memory me save
        chat_memory[chat_id].append({
            "role": "user",
            "content": user_message
        })

        # sirf last 8 messages rakhenge
        history = chat_memory[chat_id][-8:]

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.7,
                "max_tokens": 120,
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are a real Indian boyfriend writing a WhatsApp message to his girlfriend.

You must understand previous conversation context.

STRICT RULES:
- Only 1 final sendable message
- Max 2 lines
- Hinglish only
- Romantic, calm and natural
- No advice
- No explanation
- No questions asking for details
- Never say: 'detail bata', 'samjha nahi', 'kya hua'

Only the exact WhatsApp text he should send.
"""
                    }
                ] + history
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            ai_text = data["choices"][0]["message"]["content"].strip()

            # assistant reply bhi memory me save
            chat_memory[chat_id].append({
                "role": "assistant",
                "content": ai_text
            })

            return ai_text

        return "Network slow hai… 10 sec baad bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai… thodi der baad try karo 🙂"

# ================== WEBHOOK ==================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:
            reply = get_ai_reply(user_message, chat_id)
            send_message(chat_id, reply)

    return "ok"

# ================== HOME ==================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"

# ================== RUN ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
