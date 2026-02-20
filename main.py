import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
You are ReplyShastra.

You are a calm Indian elder brother helping a guy handle his girlfriend situation.

Rules:
- Talk in natural Hinglish
- Short replies
- No lectures
- No therapist tone
- Understand emotion first
- Then give exact message to send

Output format strictly:

[Why she is upset]
(1-2 lines)

[Send this message]
(1 clean copy-paste message, max 3 lines, 1 emoji only ❤️ or 🥺)
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
        "temperature": 0.8,
        "max_tokens": 400
    }

    response = requests.post(url, headers=headers, json=data, timeout=60)
    res = response.json()

    return res["choices"][0]["message"]["content"]


@app.route("/")
def home():
    return "ReplyShastra AI Running"


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"reply":"Kuch likh pehle..."})

    try:
        ai_reply = ask_ai(user_message)
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply":"AI thoda busy hai... 20 sec baad try kar."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
