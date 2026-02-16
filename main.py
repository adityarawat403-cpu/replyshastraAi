from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

# ================= TOKENS =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ================= USER MEMORY =================
user_memory = {}

# ================= MASTER PROMPT =================
MASTER_PROMPT = """
You are ReplyShastra — a real male friend helping a boy handle his relationship.

First understand the boy’s situation and emotions.

Internally detect:
• what happened
• girl's mood
• seriousness level

Classify the situation into:
1) Romantic / normal talk
2) Ignoring / dry replies
3) Angry / hurt
4) Breakup risk / distancing
5) Emotional sadness / vulnerability

Then write the exact message he should send her.

LANGUAGE RULE:
Reply in the SAME language style the user used.

TONE RULES:
Romantic → warm & caring
Ignore → calm & non-needy
Angry → accept mistake + reassure
Breakup risk → gentle + respectful + low pressure
Emotional → comforting + supportive

IMPORTANT:
You are not a coach.
You are not giving advice.
You are writing HIS message.

OUTPUT RULES:
• Only the final WhatsApp message
• Maximum 2 short lines
• Natural human texting style
• No explanation
• No bullet points
• No lectures

Allowed emoji: ❤️ or 🙂 (max 1)

Return ONLY the sendable message.
"""

# ================= TELEGRAM TYPING =================
def send_typing(chat_id, seconds=4):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    try:
        for _ in range(seconds):
            requests.post(url, json=payload, timeout=5)
            time.sleep(1)
    except:
        pass

# ================= SEND MESSAGE =================
def send_message(chat_id, text):
    if not text:
        text = "Thoda clear likh na 🙂"

    parts = [text[i:i+3500] for i in range(0, len(text), 3500)]

    for part in parts:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": part}
        try:
            requests.post(url, json=payload, timeout=15)
        except:
            pass

# ================= GROQ AI =================
def get_ai_reply(chat_id, user_message):

    if chat_id not in user_memory:
        user_memory[chat_id] = []

    # save user msg
    user_memory[chat_id].append({"role": "user", "content": user_message})

    # keep last 12 messages (memory)
    user_memory[chat_id] = user_memory[chat_id][-12:]

    messages = [
        {"role": "system", "content": MASTER_PROMPT},
        {"role": "system", "content": "If the situation is unclear, still write a suitable message."}
    ] + user_memory[chat_id]

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 140
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"].strip()

            # save AI reply also
            user_memory[chat_id].append({"role": "assistant", "content": reply})
            return reply

        return "Net thoda slow hai... fir bhej 🙂"

    except Exception as e:
        print("AI ERROR:", e)
        return "Server busy hai... 1 min baad try kar 🙂"

# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_message = message.get("text", "")

    if not user_message:
        return "ok"

    # START COMMAND
    if user_message.lower() == "/start":
        user_memory[chat_id] = []
        send_message(chat_id,
"""Hi! Main ReplyShastra hoon 🙂

Apni situation simple likh.
Main tujhe exact message dunga jo tu usse bhejega 👇""")
        return "ok"

    # typing animation
    send_typing(chat_id, 5)

    reply = get_ai_reply(chat_id, user_message)
    send_message(chat_id, reply)

    return "ok"

# ================= HEALTH CHECK =================
@app.route("/")
def home():
    return "ReplyShastra Running"

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
