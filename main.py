from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)


def get_ai_reply(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
                "X-Title": "ReplyShastra",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "temperature": 0.8,
                "max_tokens": 120,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a male friend helping a boy text a girl. Reply in short Hinglish WhatsApp style. Only 1 message. Max 2 lines. No options, no explanation, no paragraphs."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            },
            timeout=60
        )

        data = response.json()
        print("OPENROUTER:", data)

        # ---- IMPORTANT PART ----
        if "choices" in data:
            choice = data["choices"][0]

            if "message" in choice and "content" in choice["message"]:
                reply = choice["message"]["content"]
            elif "text" in choice:
                reply = choice["text"]
            else:
                return "AI samajh nahi paya... dubara bhejo 🙂"

            reply = reply.strip()

            if len(reply) > 220:
                reply = reply[:220]

            return reply

        else:
            return "AI busy hai... 20 sec baad bhejo 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server issue aa gaya... 1 min baad try karo 🙂"


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


@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
