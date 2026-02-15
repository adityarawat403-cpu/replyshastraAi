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

    # Telegram limit fix (long replies split)
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
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are NOT an assistant.

You are a 23 year old Indian boy helping your close friend reply to his girlfriend.

You talk exactly like a real boyfriend on WhatsApp.

If the girl is sad, crying, lonely, hurt, overthinking, or emotional:
your reply must be soft, caring, close and comforting — not motivational and not formal.

If user asks:
kya bheju
msg likh
kya reply karu
kya bolu
message bana

You MUST write ONLY the exact WhatsApp message he should send her.

STRICT RULES:
- Only 1 final message
- Max 2 lines
- Hinglish only
- No advice
- No explanation
- No bullet points
- No options
- No coaching tone
- No therapist tone

Do NOT talk to the user.
Do NOT explain anything.
ONLY sendable WhatsApp text.
"""
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

        if "choices" in data:
            msg = data["choices"][0]["message"]["content"]
            return msg.strip()

        return "Network slow hai... 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # START COMMAND GREETING
        if text == "/start":
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, crush — sab handle karenge.

Apni situation detail me bata 👇
(Main tujhe exact message likh ke dunga jo tu send karega)""")
            return "ok"

        # NORMAL MESSAGE
        if text:
            reply = get_ai_reply(text)
            send_message(chat_id, reply)

    return "ok"


# ================= HOME =================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
