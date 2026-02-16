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



# ---------------- WEBHOOK ----------------
@adef get_ai_reply(user_message):

    if len(user_message.strip()) < 4:
        return "Thoda detail me bata bhai, kya hua?"

    system_prompt = """
You are ReplyShastra.

You are a male best friend helping a boy fix his relationship.

He is not chatting with his girlfriend.
He is telling YOU the situation.

Your job:
Understand the emotional situation first.
Then generate the exact WhatsApp message he should send her.

Rules:
- Only message to send
- Max 2 lines
- Hinglish natural texting
- Caring but self-respecting
- No advice
- No explanation
- No talking to boy
- No acting like girl
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
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.6,
                "max_tokens": 120
            },
            timeout=45
        )

        data = response.json()

        # ---- DEBUG PRINT (IMPORTANT) ----
        print("GROQ RESPONSE:", data)

        # handle success
        if data.get("choices"):
            reply = data["choices"][0]["message"]["content"]
            reply = reply.strip().replace('"','')
            return reply

        # handle groq error
        if data.get("error"):
            print("GROQ ERROR:", data["error"])
            return "Ek sec bhai, dobara bhej 🙂"

        return "Thoda network slow hai, 10 sec baad bhej 🙂"

    except Exception as e:
        print("AI FAILED:", str(e))
        return "Server busy hai, 15 sec baad bhej 🙂"pp.route("/webhook", methods=["POST"])
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
