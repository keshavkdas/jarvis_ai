import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.0-flash"  # or "gemini-pro"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def ask_gpt(prompt):
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(body))

    if response.status_code != 200:
        return f"ERROR: {response.status_code} - {response.text}"

    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]
