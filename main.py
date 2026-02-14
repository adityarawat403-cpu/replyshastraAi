from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Tokens
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# Telegram ko reply bhejne ka function
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


# AI se reply lene ka function
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
                        "content": "You are a 23 year old Indian boy chatting with his girlfriend on WhatsApp.

You are not an assistant and not a coach.

You will write the exact message he should send her.

Rules:
- Only 1 final message
- Max 2 lines
- Hinglish only
- No advice
- No explanation
- No options
- No bullet points
- No paragraphs

Output must look like a real boyfriend message.
Do not guide. Do not teach. Only sendable text. be emotional, short and practical. No long paragraphs."
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
            return "AI busy hai thoda... 20 sec baad fir bhejo 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server connect nahi ho pa raha... thodi der baad try karo 🙂"


# Telegram webhook
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


# Home check
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
