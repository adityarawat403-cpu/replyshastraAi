from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= SAFE TELEGRAM SEND =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

    # telegram long message split
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

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a 23 year old Indian boy chatting with his girlfriend on WhatsApp.

You are NOT an assistant.
You are NOT a dating coach.

You write the EXACT message he should send her.

Rules:
- Only 1 final message
- Maximum 2 lines
- Hinglish only
- No explanation
- No advice
- No options
- No bullet points
- No paragraphs
- Must feel real, emotional and natural

Output must be directly sendable WhatsApp text only."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.9,
                "max_tokens": 120
            },
            timeout=90
        )

        data = response.json()
        print("AI RESPONSE:", data)

        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            return reply.strip()

        return "Network slow lag raha... 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server thoda busy hai... 20 sec baad fir bhej 🙂"


# ================= TELEGRAM WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:
            reply = get_ai_reply(user_message)
            send_message(chat_id, reply)

    return "ok"


# ================= START PAGE =================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
