import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai

load_dotenv()



key = os.getenv("GEMINI_API_KEY")

print("--- DIAGNOSTIC CHECK ---")
if key is None:
    print("❌ NOT LOADED: GEMINI_API_KEY is completely missing or returns None.")
    print("👉 Check if your file is named exactly '.env' (not 'gemini.env' or '.env.txt')")
elif key.strip() == "":
    print("❌ EMPTY: The variable exists but it is blank.")
else:
    print("✅ LOADED SUCCESSFULLY!")
    print(f"Prefix check: {key[:7]}...")
    print(f"Total length: {len(key)} characters")
    
    if not key.startswith("AIzaSy"):
        print("⚠️ WARNING: Your key does not start with 'AIzaSy'. This usually means it is a Google Cloud service account token or an OAuth credential instead of a standard Google AI Studio API key.")
app = Flask(__name__)
CORS(app)

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client()
MODEL_NAME = "gemini-2.5-flash"

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "Backend running",
        "message": "JD Analyser API is live"
    }), 200

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        resume_file = request.files.get("resume")
        jd_file = request.files.get("jd")

        if not resume_file or not jd_file:
            return jsonify({"error": "Resume PDF and JD PDF required"}), 400

        resume_text = extract_text_from_pdf(resume_file)
        jd_text = extract_text_from_pdf(jd_file)

        prompt = f"""
You are an expert AI resume screening assistant and recruitment specialist.

Carefully compare the provided RESUME against the JOB DESCRIPTION.
Analyze the content and provide a well-structured breakdown containing:
1. Skill Match Percentage (e.g., 75%)
2. Key Matching Skills found in both
3. Critical Missing Skills (required by JD but missing in Resume)
4. Highly actionable recommendations to improve the resume for this specific role

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        return jsonify({
            "analysis": response.text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)