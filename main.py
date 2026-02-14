from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# =============== TEXT CLEANER (VERY IMPORTANT) ===============
def clean_text(text):
    if not text:
        return "Hmm... dubara bhejo 🙂"

    # remove markdown / weird symbols (Telegram drop issue fix)
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.replace("`", "")
    text = text.replace("#", "")
    text = text.replace("<", "")
    text = text.replace(">", "")
    text = text.replace("[", "")
    text = text.replace("]", "")

    # telegram limit safety
    return text[:350]


# =============== TELEGRAM SEND MESSAGE ===============
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    safe_text = clean_text(text)

    payload = {
        "chat_id": chat_id,
        "text": safe_text,
        "parse_mode": "HTML"
    }

    r = requests.post(url, json=payload)
    print("TELEGRAM RESPONSE:", r.text)


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
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a male Indian relationship texting expert. "
                            "Reply like a real Indian guy in natural Hinglish. "
                            "Keep replies SHORT (1-2 lines max). "
                            "No paragraphs. No options. No explanations. "
                            "Direct ready-to-send WhatsApp message only."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 120
            },
            timeout=90
        )

        data = response.json()
        print("OPENROUTER RESPONSE:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "Thoda network slow hai... 20 sec baad bhejo 🙂"

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
