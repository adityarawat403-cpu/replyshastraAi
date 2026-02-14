from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ================= TEXT CLEANER =================
def clean_text(text):
    if not text:
        return "Hmm... dubara bhejo 🙂"

    text = str(text)

    # telegram markdown break fix
    bad = ["*", "_", "`", "#", "<", ">", "[", "]"]
    for b in bad:
        text = text.replace(b, "")

    return text[:350]


# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": clean_text(text)
    }

    r = requests.post(url, json=payload)
    print("TELEGRAM:", r.text)


# ================= AI REPLY FUNCTION =================
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
                        "content": "You are a MALE Indian texting expert. You help boys reply to girls. Give ONLY 1 short WhatsApp-ready Hinglish message. Max 2 lines. No options. No explanation."
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

        # ======= SMART PARSER (VERY IMPORTANT FIX) =======
        if "choices" in data:

            message = data["choices"][0].get("message", {})

            # normal models
            if isinstance(message.get("content"), str):
                if message["content"].strip():
                    return message["content"]

            # reasoning models (new format)
            if isinstance(message.get("content"), list):
                collected = ""
                for part in message["content"]:
                    if isinstance(part, dict) and "text" in part:
                        collected += part["text"]
                if collected.strip():
                    return collected

            # rare fallback
            if "text" in data["choices"][0]:
                return data["choices"][0]["text"]

        return "Ek sec... fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("INCOMING:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:
            reply = get_ai_reply(user_message)
            send_message(chat_id, reply)

    return "ok"


# ================= HOME =================
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
