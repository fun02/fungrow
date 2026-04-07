from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)
CORS(app)

# =========================
# API KEY (AMAN)
# =========================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("WARNING: GEMINI_API_KEY belum diset")

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
Kamu adalah AI seperti Gemini.

Aturan:
- Gunakan bahasa Indonesia yang natural & profesional
- Format jawaban dengan markdown rapi
- Gunakan heading (##), bullet, dan spacing
- Hindari simbol aneh seperti ###
- Buat jawaban enak dibaca di layar HP
- Jangan terlalu panjang, tapi tetap jelas
"""

# =========================
# GET MODEL
# =========================
def get_model():
    return "gemini-1.5-flash"


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "API RUNNING 🚀"


# =========================
# CHAT AI
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user = data.get("message", "")

        if not user:
            return jsonify({"reply": "Pesan kosong"})

        if not API_KEY:
            return jsonify({"reply": "API KEY belum diset di Railway"})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{get_model()}:generateContent?key={API_KEY}"

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

        # Debug response kalau error
        if "error" in result:
            return jsonify({"reply": result["error"]["message"]})

        if "candidates" not in result:
            return jsonify({"reply": "Error: respon AI tidak valid"})

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error server: {str(e)}"})


# =========================
# VISION AI
# =========================
@app.route("/vision", methods=["POST"])
def vision():
    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"reply": "Tidak ada file dikirim"})

        if not API_KEY:
            return jsonify({"reply": "API KEY belum diset di Railway"})

        img_bytes = file.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{get_model()}:generateContent?key={API_KEY}"

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

        res = requests.post(url, json=payload)
        result = res.json()

        if "error" in result:
            return jsonify({"reply": result["error"]["message"]})

        if "candidates" not in result:
            return jsonify({"reply": "Error: respon vision tidak valid"})

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error vision: {str(e)}"})


# =========================
# RUN LOCAL / RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
