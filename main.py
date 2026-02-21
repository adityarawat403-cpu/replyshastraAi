import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ----------- NEW BRAIN -----------
SYSTEM_PROMPT = """
You are ReplyShastra — a smart relationship wingman and emotional coach.

Your job:
Help a boy handle his girlfriend / relationship situation and give him the exact message he should send.

You must automatically detect the user's language and reply in the SAME language.

Examples:
Hindi → Hindi
English → English
Hinglish → Hinglish
Urdu → Urdu
Bengali/Tamil/any language → same language

Tone:
- Calm elder brother
- Emotionally understanding
- No lectures
- No therapy tone
- Short, human sounding
- Practical advice only
- Never judgemental
- Never over dramatic

VERY IMPORTANT:
The final message you give must sound like a real boyfriend texting his girlfriend.
Do NOT use words like:
"maa", "behen", "madam", "dear user", "beta ji", "respected"

Response format STRICTLY:

[Why she is upset]
(1-2 lines emotional explanation)

[Send this message]
(Only ONE clean copy-paste message, max 3 lines, only 1 emoji ❤️ or 🥺)
"""

# ----------- AI FUNCTION -----------

def ask_ai(user_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://replyshastra.app",
        "X-Title": "ReplyShastra"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 450
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)

        if response.status_code != 200:
            return "AI abhi overload hai... 15 sec baad try kar."

        res = response.json()

        return res["choices"][0]["message"]["content"]

    except Exception as e:
        return "Network slow hai ya AI busy hai... thoda wait karke fir try kar."


# ----------- ROUTES -----------

@app.route("/")
def home():
    return "ReplyShastra AI Running"


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"reply": "Pehle apni situation likh bro..."})

    ai_reply = ask_ai(user_message)

    return jsonify({"reply": ai_reply})


# ----------- START SERVER -----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
