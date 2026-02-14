from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= TELEGRAM SEND MESSAGE (FIXED) =================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Safety fallback
    if not text:
        text = "Samajh nahi aya... dubara bhejo 🙂"

    # REMOVE characters that break Telegram
    bad_chars = ["<", ">", "&", "\"", "'", "`", "*", "_", "#"]
    for ch in bad_chars:
        text = text.replace(ch, "")

    # Telegram message size safety
    text = text[:350]

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    r = requests.post(url, json=payload)
    print("TELEGRAM RESPONSE:", r.text)


# ================= AI REPLY FUNCTION =================
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
                            "You are a confident Indian boyfriend texting expert. "
                            "You help boys reply to girls. "
                            "Reply like a real Indian guy on WhatsApp in natural Hinglish. "
                            "Maximum 2 lines only. "
                            "No paragraphs. No explanation. No options. "
                            "Only ready to send message."
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
        print("OPENROUTER RAW:", data)

        # Smart parser (handles all model formats)
        if "choices" in data:
            msg = data["choices"][0]["message"]

            # normal string reply
            if isinstance(msg.get("content"), str) and msg["content"].strip() != "":
                return msg["content"]

            # array type reply (some models send this)
            if isinstance(msg.get("content"), list):
                for part in msg["content"]:
                    if "text" in part:
                        return part["text"]

        return "Soch raha hoon... 5 sec baad bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"


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


# ================= HOME CHECK =================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
