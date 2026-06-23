import os
import json
import urllib.request
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# API key stored securely as environment variable — never hardcoded
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="


def analyze_with_gemini(text):
    prompt = (
        'You are a 30-year veteran cybersecurity expert. '
        'Analyze this for scam/fraud/phishing: "' + text + '"\n\n'
        'Respond ONLY in this JSON format, no extra text:\n'
        '{\n'
        '  "verdict": "SCAM" or "SUSPICIOUS" or "SAFE",\n'
        '  "risk_score": number 0-100,\n'
        '  "confidence": "HIGH" or "MEDIUM" or "LOW",\n'
        '  "red_flags": ["flag1", "flag2"],\n'
        '  "explanation": "2-3 sentence explanation",\n'
        '  "recommendation": "what the user should do"\n'
        '}'
    )

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL + GEMINI_API_KEY,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            raw = result["candidates"][0]["content"]["parts"][0]["text"]
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
    except Exception:
        return basic_analysis(text)


def basic_analysis(text):
    t = text.lower()
    scam_words = ["free","win","won","prize","lottery","click","urgent",
                  "verify","otp","bank","account","blocked","suspended",
                  "congratulations","selected","kyc","expire","claim","reward","gift"]
    found = [w for w in scam_words if w in t]
    score = min(95, len(found) * 18)
    if len(found) >= 3:
        return {"verdict":"SCAM","risk_score":score,"confidence":"MEDIUM","red_flags":found[:5],
                "explanation":f"Multiple scam indicators: {', '.join(found)}.","recommendation":"Do NOT click links. Block this sender."}
    elif len(found) >= 1:
        return {"verdict":"SUSPICIOUS","risk_score":max(40,score),"confidence":"LOW","red_flags":found,
                "explanation":f"Suspicious keywords: {', '.join(found)}.","recommendation":"Be cautious. Verify with official source."}
    return {"verdict":"SAFE","risk_score":8,"confidence":"LOW","red_flags":[],
            "explanation":"No obvious red flags detected.","recommendation":"Looks okay, but stay cautious."}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("input", "").strip()
    if not text:
        return jsonify({"error": "No input provided"}), 400
    result = analyze_with_gemini(text)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
