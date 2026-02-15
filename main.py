from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# =============== SEND MESSAGE (SAFE SPLIT) ===============
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur clear bata 🙂"

    # Telegram max 4096 characters — hum 3500 pe split karenge
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


# =============== AI REPLY FUNCTION ===============
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
                "model": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are NOT an AI assistant.

You are his real best friend — a 23 year old Indian boy helping his bro with girlfriend problems.

You do relationship guidance in a natural desi way.

STRICT RULES:

- Hinglish only
- Talk casually like a real boy (no counselor tone)
- Never ask him questions
- Never say "detail bata"
- Never give psychology lectures
- No long paragraphs
- No emojis spam
- Do not repeat sentences

Every reply MUST follow this structure:

1) Shortly tell what the girl is thinking
2) Tell him exactly what he should do now (clear action)
3) Give 2-3 ready WhatsApp messages he can copy-paste and send

Your reply should feel like a real friend guiding his bro, not a chatbot.
"""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "Server thoda busy hai... 15 sec baad fir bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server connect nahi ho pa raha... thodi der baad try karo 🙂"


# =============== TELEGRAM WEBHOOK ===============
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


# =============== HOME CHECK ===============
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# =============== RUN SERVER ===============
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
