import requests
import json

with open("config/config.json", encoding="utf-8") as f:
    config = json.load(f)

API_KEY = config["api_key"]
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def ask_gemini(text):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": text}
                ]
            }
        ]
    }

    response = requests.post(URL, headers=headers, json=payload)

    try:
        reply = response.json()
        return reply["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}\n{response.text}"
