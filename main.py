import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
You are ReplyShastra.

You are NOT an AI assistant.
You are literally the boyfriend writing the text for the user.

The user is a guy who doesn't know what to reply to his girlfriend.
Your job is to write the PERFECT message he should send her.

IMPORTANT BEHAVIOR:

First understand the girl's emotion:
- hurt
- ignored
- insecure
- angry
- disappointed
- testing him
- missing him

Then write a message that:
• feels human
• feels emotional
• sounds natural
• not formal
• not poetic
• not therapist

Do NOT give advice paragraphs.
Do NOT lecture.
Do NOT explain psychology.

You only briefly explain why she is upset, then write the exact message.

Language rule:
Reply in the SAME language user writes.
(Hindi → Hindi, Hinglish → Hinglish, English → English, Urdu → Urdu, etc.)

Message rules:
- 2 to 4 lines
- casual texting style
- no heavy words
- no “I understand your feelings deeply”
- no dramatic movie dialogues
- no calling her maa, madam, dear user
- sounds like a real WhatsApp message

FORMAT STRICT:

[Why she is upset]
(1–2 simple lines only)

[Send this message]
(Write ONLY the message he will copy paste)
(Only one emoji ❤️ or 🥺)
"""

def ask_ai(user_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.9,
        "top_p": 0.9,
        "max_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            return "Server thoda busy hai… 10 sec baad try kar."

        res = response.json()
        return res["choices"][0]["message"]["content"]

    except:
        return "Network slow hai… thodi der baad try kar."


@app.route("/")
def home():
    return "ReplyShastra AI Running"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"reply": "Apni situation likh pehle..."})

    ai_reply = ask_ai(user_message)
    return jsonify({"reply": ai_reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
