import os
from dotenv import load_dotenv
import requests

# ⬅️ تحميل متغيرات البيئة من ملف .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(prompt):
    if not API_KEY:
        return "❌ Error: API key not found."
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "❌ No response.")
    else:
        return f"❌ API Error {response.status_code}: {response.text}"
