from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# =============== TEXT CLEANER ===============
def clean_text(text):
    if not text:
        return "Hmm... dubara bhejo 🙂"

    text = str(text)

    # markdown & telegram breaking symbols remove
    bad = ["*", "_", "`", "#", "<", ">", "[", "]", "(", ")", "{", "}"]
    for b in bad:
        text = text.replace(b, "")

    return text[:350]


# =============== TELEGRAM SEND ===============
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": clean_text(text)
    }

    r = requests.post(url, json=payload)
    print("TELEGRAM RESPONSE:", r.text)


# =============== AI REPLY (REAL FIX) ===============
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
                            "You are a male Indian texting expert. "
                            "You help boys reply to girls. "
                            "Always reply like a boy, not like a girl. "
                            "Give ONLY 1 short WhatsApp ready message in Hinglish. "
                            "Maximum 2 lines. "
                            "No options. No explanations. No paragraphs."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 120
            },
            timeout=90
        )

        data = response.json()
        print("OPENROUTER RAW:", data)

        # -------- SMART PARSER (MAIN BUG FIX) --------
        if "choices" in data:
            msg = data["choices"][0]["message"]

            # normal string response
            if isinstance(msg.get("content"), str) and msg["content"].strip():
                return msg["content"]

            # array format response (OpenRouter sometimes)
            if isinstance(msg.get("content"), list):
                for part in msg["content"]:
                    if isinstance(part, dict) and "text" in part:
                        return part["text"]

        return "Network slow lag raha... 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"


# =============== TELEGRAM WEBHOOK ===============
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


# =============== HOME CHECK ===============
@app.route("/")
def home():
    return "ReplyShastra AI Running 🚀"


# =============== RUN SERVER ===============
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
