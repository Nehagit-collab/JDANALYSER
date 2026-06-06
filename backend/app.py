import os

from flask import Flask, jsonify, request

from flask_cors import CORS  # 1. Import the package

from pypdf import PdfReader

from dotenv import load_dotenv

from google import genai



# ... load environment variables ...





# ... rest of your backend code stays exactly the same ...



# -----------------------------

# Load environment variables

# -----------------------------

load_dotenv()

print("Gemini Key Loaded:", bool(os.getenv("GEMINI_API_KEY")))



# -----------------------------

# App initialization

# -----------------------------

app = Flask(__name__)

CORS(app)  # 2. Enable CORS for your frontend to connect safely!





# -----------------------------

# Gemini client initialization

# -----------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:

    raise RuntimeError("GEMINI_API_KEY not set")



client = genai.Client(api_key=GEMINI_API_KEY)



# ✅ FIXED: Updated to active, supported 3.5 series model

MODEL_NAME = "gemini-3.5-flash"



# -----------------------------

# Helper: Extract text from PDF

# -----------------------------

def extract_text_from_pdf(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        text += page.extract_text() or ""

    return text.strip()



# -----------------------------

# Routes

# -----------------------------

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



        # Enhanced prompt for better structured output

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



        # Call to the updated Gemini model

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt

        )



        return jsonify({

            "analysis": response.text

        }), 200



    except Exception as e:

        print("ANALYZE ERROR:", e)

        return jsonify({"error": str(e)}), 500





# -----------------------------

# Run app

# -----------------------------

if __name__ == "__main__":

    app.run(debug=True)

