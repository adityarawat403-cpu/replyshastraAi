from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ========= TOKENS =========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ========= TELEGRAM SEND =========
def send_message(chat_id, text):

    if not text or text.strip() == "":
        text = "Ek sec... fir bhej 🙂"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text[:350]
    }

    try:
        requests.post(url, json=payload, timeout=20)
    except:
        pass


# ========= AI REPLY =========
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
                        "content": (
                            "You are a male Indian dating texting expert. "
                            "You help boys reply to girls. "
                            "Give ONLY one WhatsApp ready message. "
                            "Hinglish language. "
                            "Maximum 2 lines. "
                            "No options. No explanation. No paragraphs."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.9,
                "max_tokens": 80
            },
            timeout=60
        )

        data = response.json()
        print("AI DATA:", data)

        # ---- universal parser ----
        if "choices" in data:

            choice = data["choices"][0]

            # normal models
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                if content and content.strip() != "":
                    return content

            # text models
            if "text" in choice:
                return choice["text"]

        return "Thoda soch raha hoon... 5 sec baad bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"


# ========= WEBHOOK =========
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


# ========= HOME =========
@app.route("/")
def home():
    return "ReplyShastra Running"


# ========= RUN =========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
