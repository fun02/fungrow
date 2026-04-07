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
# CONFIG
# =========================
def get_model():
    return "gemini-1.5-flash"  # ✅ FIX MODEL

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
# LIST MODELS (OPTIONAL)
# =========================
@app.route("/models")
def models():
    API_KEY = get_api_key()

    if not API_KEY:
        return {"error": "API KEY belum diset"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    res = requests.get(url)

    return res.json()


# =========================
# CHAT AI
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        API_KEY = get_api_key()

        if not API_KEY:
            return jsonify({"reply": "❌ API KEY belum diset di Railway"})

        data = request.get_json()

        if not data:
            return jsonify({"reply": "❌ Body harus JSON"})

        user = data.get("message", "")

        if not user:
            return jsonify({"reply": "❌ Pesan kosong"})

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

        headers = {
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)
        result = res.json()

        # ===== ERROR HANDLE =====
        if "error" in result:
            return jsonify({
                "reply": "❌ " + result["error"]["message"]
            })

        candidates = result.get("candidates")

        if not candidates:
            return jsonify({"reply": "❌ Respon AI kosong"})

        parts = candidates[0]["content"]["parts"]

        if not parts:
            return jsonify({"reply": "❌ Tidak ada isi respon"})

        reply = parts[0].get("text", "❌ Tidak ada teks")

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({
            "reply": f"❌ Error server: {str(e)}"
        })


# =========================
# VISION AI
# =========================
@app.route("/vision", methods=["POST"])
def vision():
    try:
        API_KEY = get_api_key()

        if not API_KEY:
            return jsonify({"reply": "❌ API KEY belum diset di Railway"})

        file = request.files.get("file")

        if not file:
            return jsonify({"reply": "❌ Tidak ada file dikirim"})

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

        headers = {
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)
        result = res.json()

        if "error" in result:
            return jsonify({"reply": "❌ " + result["error"]["message"]})

        candidates = result.get("candidates")

        if not candidates:
            return jsonify({"reply": "❌ Respon vision kosong"})

        reply = candidates[0]["content"]["parts"][0]["text"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({
            "reply": f"❌ Error vision: {str(e)}"
        })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
