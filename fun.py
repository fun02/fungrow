from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)
CORS(app)

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
Kamu adalah AI modern seperti Gemini.

Aturan:
- Gunakan bahasa Indonesia yang natural & profesional
- Format markdown rapi
- Gunakan heading dan bullet
- Jawaban enak dibaca di HP
- Tidak terlalu panjang
"""

# =========================
# CONFIG BARU (FIX)
# =========================
def get_model():
    return "gemini-1.5-flash"  # ✅ MODEL BARU

def get_api_key():
    return os.getenv("GEMINI_API_KEY")


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "API RUNNING 🚀"


# =========================
# DEBUG
# =========================
@app.route("/debug")
def debug():
    return {
        "api_key": str(get_api_key()),
        "model": get_model()
    }


# =========================
# CHAT AI (VERSI BARU)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        API_KEY = get_api_key()

        if not API_KEY:
            return jsonify({"reply": "❌ API KEY belum diset"})

        data = request.get_json(force=True)
        user = data.get("message", "")

        if not user:
            return jsonify({"reply": "❌ Pesan kosong"})

        # 🔥 ENDPOINT BARU (V1)
        url = f"https://generativelanguage.googleapis.com/v1/models/{get_model()}:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT + "\n\nUser: " + user}
                    ]
                }
            ]
        }

        res = requests.post(url, json=payload)
        result = res.json()

        if "error" in result:
            return jsonify({"reply": "❌ " + result["error"]["message"]})

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}"})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
