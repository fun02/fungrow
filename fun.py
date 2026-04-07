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
# API KEY
# =========================
def get_api_key():
    return os.getenv("GEMINI_API_KEY")


# =========================
# AMBIL MODEL OTOMATIS
# =========================
def get_available_model():
    API_KEY = get_api_key()

    url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
    res = requests.get(url).json()

    for m in res.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            return m["name"]  # langsung pakai model valid

    return None


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "API RUNNING 🚀"


# =========================
# DEBUG MODEL
# =========================
@app.route("/debug")
def debug():
    return {
        "api_key": str(get_api_key()),
        "model_auto": get_available_model()
    }


# =========================
# CHAT AI (AUTO MODEL)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        API_KEY = get_api_key()

        if not API_KEY:
            return jsonify({"reply": "❌ API KEY belum diset"})

        model = get_available_model()

        if not model:
            return jsonify({"reply": "❌ Tidak ada model tersedia"})

        data = request.get_json(force=True)
        user = data.get("message", "")

        if not user:
            return jsonify({"reply": "❌ Pesan kosong"})

        url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={API_KEY}"

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

        return jsonify({
            "model_used": model,
            "reply": reply
        })

    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}"})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
