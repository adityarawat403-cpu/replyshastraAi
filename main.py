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
                        "content": "You are a male Indian texting expert. Give ONLY 1 short Hinglish WhatsApp reply. Max 2 lines. No explanation."
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
        print("FULL AI RESPONSE:", data)

        # ---------- UNIVERSAL PARSER ----------
        if "choices" not in data:
            return "Soch raha hoon... fir bhej 🙂"

        choice = data["choices"][0]

        # Case 1: Normal GPT style
        if "message" in choice and isinstance(choice["message"].get("content"), str):
            return choice["message"]["content"]

        # Case 2: Claude / reasoning models
        if "message" in choice and isinstance(choice["message"].get("content"), list):
            text_reply = ""
            for part in choice["message"]["content"]:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_reply += part.get("text", "")
            if text_reply.strip():
                return text_reply

        # Case 3: Some providers send direct text
        if "text" in choice:
            return choice["text"]

        return "Network thoda slow hai... fir bhej 🙂"

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
