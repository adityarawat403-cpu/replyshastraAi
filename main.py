def get_ai_reply(user_message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": os.getenv("SITE_URL"),
                "X-Title": "ReplyShastra"
            },
            json={
                "model": "deepseek/deepseek-chat:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "Tum ek smart Indian relationship advisor ho. Tum Hinglish me natural, emotional, short aur practical replies dete ho jaise real banda chat me deta hai."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 300
            },
            timeout=60
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "AI thoda confuse ho gaya... phir se bhejo 🙂"

    except Exception as e:
        print("OPENROUTER ERROR:", e)
        return "AI abhi connect nahi ho pa raha... 30 sec baad try karo 🙂"
