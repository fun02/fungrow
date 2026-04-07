from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)

# =========================
# CORS FIX (PENTING 🔥)
# =========================
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
Kamu adalah AI seperti ChatGPT.

Aturan:
- Gunakan bahasa Indonesia natural & profesional
- Format markdown rapi
- Gunakan heading & bullet
- Jawaban enak dibaca di HP
"""


# =========================
# MODEL (FIX TERBARU 🔥)
# =========================
def get_model():
    return "models/gemini-2.5-flash"


# =========================
# API KEY
# =========================
def get_api_key():
    return os.getenv("GEMINI_API_KEY")


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "🚀 FUN GROW AI RUNNING"


# =========================
# DEBUG
# =========================
@app.route("/debug")
def debug():
    return {"api_key": str(get_api_key())}


# =========================
# CHAT
# =========================
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    try:
        API_KEY = get_api_key()

        data = request.get_json(force=True)
        user = data.get("message", "")

        if not user:
            return jsonify({"reply": "Pesan kosong"})

        if not API_KEY:
            return jsonify({"reply": "API KEY belum diset di Railway"})

        url = f"https://generativelanguage.googleapis.com/v1beta/{get_model()}:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT + "\n\nUser: " + user}
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)
        result = res.json()

        if "error" in result:
            return jsonify({"reply": "❌ " + result["error"]["message"]})

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({
            "reply": reply,
            "model_used": get_model()
        })

    except Exception as e:
        return jsonify({"reply": f"❌ Error server: {str(e)}"})


# =========================
# VISION
# =========================
@app.route("/vision", methods=["POST", "OPTIONS"])
def vision():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    try:
        API_KEY = get_api_key()

        file = request.files.get("file")

        if not file:
            return jsonify({"reply": "Tidak ada file dikirim"})

        if not API_KEY:
            return jsonify({"reply": "API KEY belum diset di Railway"})

        img_bytes = file.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/{get_model()}:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Jelaskan gambar ini secara detail"},
                        {
                            "inline_data": {
                                "mime_type": file.mimetype,
                                "data": img_base64
                            }
                        }
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)
        result = res.json()

        if "error" in result:
            return jsonify({"reply": "❌ " + result["error"]["message"]})

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"❌ Error vision: {str(e)}"})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
