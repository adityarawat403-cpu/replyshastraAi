from flask import Flask, request
import requests
import os
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ========= USER MEMORY =========
user_memory = {}

# ========= TELEGRAM FUNCTIONS =========
def send_typing(chat_id, stop_event):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}

    while not stop_event.is_set():
        try:
            requests.post(url, json=payload, timeout=10)
        except:
            pass
        time.sleep(4)


def send_message(chat_id, text):
    if not text:
        text = "Samjha hu bhai... thoda aur detail me bata 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": part}
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass


# ========= AI BRAIN =========
def get_ai_reply(chat_id, user_message):

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    # store message
    user_memory[chat_id].append({"role": "user", "content": user_message})
    user_memory[chat_id] = user_memory[chat_id][-12:]  # last 12 msgs

    # ----------- SYSTEM BRAIN PROMPT -----------
    system_prompt = """
You are ReplyShastra.

You are not an assistant.
You are a calm, mature Indian male friend helping a boy handle his girlfriend situation.

Your job:
First understand the situation.
Then either guide him OR write the exact message he should send.

Behavior rules:
• Talk like a real human, not a coach
• Short responses
• Hinglish natural tone
• No lectures
• No psychology explanation
• No long paragraphs

If user asks "kya karu":
→ briefly guide him (3-4 lines max)

If user asks "msg de", "kya bheju", "reply kya du":
→ write ONLY the exact WhatsApp message
→ Maximum 2 lines
→ Soft respectful tone

If girl is angry:
→ apology type message

If girl is ignoring:
→ calm non-needy message

If girl said bye / don't text:
→ respectful space message

Never insult the girl.
Never abuse.
Never act like a guru.

Be emotionally intelligent and practical.
"""

    messages = [{"role": "system", "content": system_prompt}] + user_memory[chat_id]

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": messages,
                "temperature": 0.7
            },
            timeout=120
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]
            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Network slow hai... 10 sec baad fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... thoda baad try kar 🙂"


# ========= WEBHOOK =========
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if user_message:

            # reset memory
            if user_message.lower() == "/start":
                user_memory[chat_id] = []
                send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, late reply — sab handle karenge.

Apni situation simple likh 👇""")
                return "ok"

            # start typing animation
            stop_event = threading.Event()
            typing_thread = threading.Thread(target=send_typing, args=(chat_id, stop_event))
            typing_thread.start()

            reply = get_ai_reply(chat_id, user_message)

            stop_event.set()
            typing_thread.join()

            send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
