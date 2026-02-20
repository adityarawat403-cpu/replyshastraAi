import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# simple memory (per user)
user_memory = {}

SYSTEM_PROMPT = """
You are ReplyShastra.

You are not an assistant.
You are a calm Indian male friend helping a guy handle his girlfriend situation.

RULES:
- Talk natural Hinglish
- First understand, don't jump to solution
- Ask short questions if needed
- When situation becomes clear → give ONE final copy-paste message for girl

FINAL MESSAGE RULE:
Give ONLY this format when ready:

[Send this message]
(actual message he will send her, max 3 lines, soft tone, 1 emoji max ❤️ or 🥺)

Do not give lectures.
Do not give multiple options.
"""

def ask_ai(user_id, text):

    history = user_memory.get(user_id, [])

    history.append({"role": "user", "content": text})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-8:]  # last 8 messages memory

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openchat/openchat-7b",
            "messages": messages,
            "temperature": 0.7
        },
        timeout=60
    )

    data = response.json()

    if "choices" not in data:
        return "Server thoda busy hai… 20 sec baad fir likh."

    reply = data["choices"][0]["message"]["content"]

    history.append({"role": "assistant", "content": reply})
    user_memory[user_id] = history

    return reply


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message")

    reply = ask_ai(user_id, message)

    return jsonify({"reply": reply})


@app.route("/")
def home():
    return "ReplyShastra Brain Running"
