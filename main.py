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

    # Telegram limit fix (long reply split)
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
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are ReplyShastra.

You are NOT a therapist.
You are NOT an AI assistant.

You are a 23 year old Indian boy helping your bro handle his girlfriend situation on WhatsApp.

Your job:
Give real practical help and exact messages he should send.

VERY IMPORTANT STYLE:
- Hinglish
- Simple words
- Friendly tone (bhai, samajh, dekh)
- No long essays
- No theory lectures
- No psychology paragraphs
- No motivational speech

RESPONSE FORMAT (STRICT):
1) First: Explain in 4-6 lines what the girl is likely thinking.
2) Second: Tell exactly what he should do right now.
3) Third: Give 2 or 3 READY-TO-SEND WhatsApp messages.

READY MESSAGE RULES:
- Only 1-2 lines each
- Natural texting language
- Copy-paste sendable
- No long English paragraphs
- No emoji spam
- No numbering

CRITICAL:
If user writes small input like "gf ignore kar rahi hai"
→ You STILL give full help.

Never say:
"samjha nahi"
"detail bata"
"tell me more"

Always give solution."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.9,
                "max_tokens": 500
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "Network thoda slow hai... 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server connect nahi ho pa raha... thodi der baad try karo 🙂"


# ================= WEBHOOK =================
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


# ================= START CHECK =================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
