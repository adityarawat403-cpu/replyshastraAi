from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- SEND TYPING ----------------
def send_typing(chat_id, seconds=18):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    end = time.time() + seconds
    while time.time() < end:
        try:
            requests.post(url, json=payload, timeout=5)
        except:
            pass
        time.sleep(4)


# ---------------- SEND MESSAGE ----------------
def send_message(chat_id, text):
    if not text:
        text = "Samajh nahi aya bhai, thoda detail me bata 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": part}
        try:
            requests.post(url, json=payload, timeout=20)
        except:
            pass


# ---------------- AI REPLY ----------------
def get_ai_reply(user_message):

    # small message filter (very important)
    if len(user_message.strip()) < 4:
        return "Thoda detail me bata bhai, kya hua?"

    # SYSTEM PROMPT (REAL BRO BRAIN)
    system_prompt = """
You are ReplyShastra.

You are a supportive male friend helping a boy handle his relationship.

He is NOT chatting with his girlfriend.
He is explaining the situation to YOU.

Your task:
First understand what happened emotionally between them.
Then write the exact WhatsApp message he should send to his girlfriend.

Internally think:
- what she is feeling
- what mistake he made
- what message will calm her

But NEVER show this thinking.

Output rules:
- Only the message to send
- Max 2 short lines
- Natural Hinglish texting
- Calm, caring, mature
- Non-needy
- No advice
- No lectures
- No bullet points
- Do not act like the girl
- Do not talk to the boy

Goal: improve their relationship.
"""

    analysis_context = f"""
My friend told me this about his girlfriend:

\"\"\"
{user_message}
\"\"\"

Write the exact message he should send her.
Only the sendable WhatsApp message.
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_context}
                ],
                "temperature": 0.5,
                "max_tokens": 120
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            # remove quotes if AI adds them
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]

            return reply

        return "Aaj thoda server slow hai, 20 sec baad bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai, thoda baad bhej 🙂"


# ---------------- WEBHOOK ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        if not user_message:
            return "ok"

        # start command
        if user_message.lower() == "/start":
            send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

GF ignore, naraz, breakup, late reply — sab handle karenge.

Apni situation simple likh 👇""")
            return "ok"

        # typing animation
        send_typing(chat_id, 18)

        # AI reply
        reply = get_ai_reply(user_message)

        # send
        send_message(chat_id, reply)

    return "ok"


@app.route("/")
def home():
    return "ReplyShastra Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
