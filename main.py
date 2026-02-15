from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= SEND MESSAGE (LONG SAFE) =================
def send_message(chat_id, text):
    if not text:
        text = "Samajh gaya... thoda aur detail me bata 🙂"

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


# ================= AI REPLY FUNCTION (FIXED) =================
def get_ai_reply(user_message):
    try:

        # ---- FORCE CONTEXT (MOST IMPORTANT FIX) ----
        forced_context = f"""
Situation: Indian relationship problem.

Boy message:
{user_message}

He is asking help about his girlfriend.

You must:
- explain what girl is thinking
- tell him what to do
- give ready WhatsApp messages

Never ask for more detail.
Never say 'detail bata'.
Never ask questions.
"""

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a real Indian male friend helping your bro with girlfriend problems.

Style:
Hinglish
Friendly
Confident
No lecture
No psychology jargon

You NEVER ask questions.

Always:
1) Explain situation
2) Tell what he should do
3) Give 2-3 exact copy-paste messages he can send."""
                    },
                    {
                        "role": "user",
                        "content": forced_context
                    }
                ],
                "temperature": 0.85,
                "max_tokens": 700
            },
            timeout=90
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "Network slow hai... fir bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai... 20 sec baad bhej 🙂"


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


# ================= START MESSAGE =================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
