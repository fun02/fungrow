from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)
CORS(app)

# =========================
# ENV
# =========================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY belum diset di environment variable")


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
# MODEL
# =========================
def get_model():
    return "gemini-1.5-flash"


# =========================
# HEALTH CHECK
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

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{get_model()}:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": SYSTEM_PROMPT + "\n\nUser: " + user
                        }
                    ]
                }
            ]
        }

        res = requests.post(url, json=payload)
        result = res.json()

        if "error" in result:
            return jsonify({"reply": result["error"]["message"]})

        try:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return jsonify({"reply": "AI tidak merespon, coba lagi."})

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

        img_bytes = file.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{get_model()}:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Jelaskan gambar ini"},
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

        try:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return jsonify({"reply": "AI tidak bisa membaca gambar."})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error vision: {str(e)}"})


# =========================
# RUN LOCAL / RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
