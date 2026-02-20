import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
You are ReplyShastra.

You are a real Indian male best friend and relationship fixer.

You do NOT give advice.
You ONLY give the exact message the user should send to the girl.

Style:
Short, natural Hinglish
Calm, emotionally intelligent
No lectures
No long explanations

Response format STRICT:

Why she reacted:
(1 line explanation)

Send this message:
(Only 1 copy-paste message, max 3 lines, 1 emoji allowed ❤️ or 🥺)
"""

def ask_ai(user_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "google/gemma-2-9b-it",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.8,
        "max_tokens": 400
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res = response.json()

        if "choices" in res:
            return res["choices"][0]["message"]["content"]

        return "Thoda network issue aya, ek baar fir likh."

    except Exception as e:
        print(e)
        return "Server busy hai 10 sec baad try kar."

@app.route("/")
def home():
    return "ReplyShastra WebApp Running"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"reply": "Message empty hai."})

    ai_reply = ask_ai(user_message)

    return jsonify({"reply": ai_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
