from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== MEMORY STORE =====
user_memory = {}


# ================= TELEGRAM SEND =================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass


# ================= TYPING ANIMATION =================
typing_flags = {}

def typing_loop(chat_id):
    while typing_flags.get(chat_id, False):
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
                timeout=10
            )
        except:
            pass
        time.sleep(4)


# ================= AI REPLY =================
def get_ai_reply(chat_id, user_message):

    # ---- MEMORY INIT ----
    if chat_id not in user_memory:
        user_memory[chat_id] = []

    # save user msg
    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-12:]


    system_prompt = """
You are ReplyShastra.

You are NOT the boyfriend.
You are a ghostwriter.

A boy will tell you what happened between him and his girlfriend.
Your job is to write the exact WhatsApp message HE should send TO HER.

Important:
The message must look like it is written by the boy and sent to his girlfriend.

Write ONLY the message he should copy-paste and send.

Style:
• Natural Indian Hinglish
• Caring, calm, emotionally understanding
• Mature (not cheesy, not poetic)

Rules:
• Maximum 2 short lines
• No explanation
• No advice
• Do not talk to the user
• Do not analyse
• Do not instruct

Always assume:
The girl is upset and the boy wants to fix things.

Output:
Only the sendable WhatsApp message.
Nothing else.
"""

    messages = [{"role": "system", "content": system_prompt}] + user_memory[chat_id]

    # start typing animation
    typing_flags[chat_id] = True
    threading.Thread(target=typing_loop, args=(chat_id,), daemon=True).start()

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": messages,
                "temperature": 0.7
            },
            timeout=70
        )

        typing_flags[chat_id] = False

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            # save assistant reply
            user_memory[chat_id].append({"role": "assistant", "content": reply})

            return reply

        return "Thoda sa network issue aaya… ek baar fir bhej 🙂"

    except Exception as e:
        typing_flags[chat_id] = False
        print("AI ERROR:", e)
        return "Server busy tha… 10 sec baad fir bhej 🙂"


# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

            if user_message.lower() == "/start":
                user_memory[chat_id] = []
                send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, late reply — sab handle karenge.

Apni situation simple likh 👇""")
                return "ok"

            reply = get_ai_reply(chat_id, user_message)
            send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
