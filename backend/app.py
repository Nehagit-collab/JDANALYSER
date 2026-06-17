import os
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai

# 1. Target and load the .env file located in the main root folder (one level back from the backend folder)
root_env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=root_env_path)

# 2. Initialize the Gemini Client explicitly using the verified API key from the root folder
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is completely missing from the .env file in your main root folder.")
    
    client = genai.Client(api_key=api_key)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Gemini Client: {str(e)}")

# 3. Configure Flask to serve assets out of your sibling frontend folder
app = Flask(
    __name__, 
    static_url_path='',  # Serves script.js directly at the root endpoint level
    static_folder='../frontend', 
    template_folder='../frontend'
)
CORS(app)

def extract_text_from_pdf(file):
    """Extracts text content cleanly from an uploaded PDF file."""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF file: {str(e)}")

@app.route("/", methods=["GET"])
def health_check():
    """Serves the main frontend application file UI directly."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Fetch files from the incoming request payload
        resume_file = request.files.get("resume")
        jd_file = request.files.get("jd")

        if not resume_file or not jd_file:
            return jsonify({"error": "Both Resume PDF and Job Description PDF are required."}), 400

        # Extract text from both documents
        resume_text = extract_text_from_pdf(resume_file)
        jd_text = extract_text_from_pdf(jd_file)

        if not resume_text or not jd_text:
            return jsonify({"error": "Could not extract readable text from one or both PDFs. Ensure they aren't scanned images."}), 400

        # Construct the optimized prompt context for Gemini
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

        # Current supported flagship models for the modern Google GenAI SDK
        models_to_try = ['gemini-2.5-flash', 'gemini-2.5-pro']
        max_retries = 2
        retry_delay = 2  # initial delay in seconds
        
        response = None
        last_error = None

        for model_name in models_to_try:
            for attempt in range(max_retries):
                try:
                    print(f"Sending request using model: {model_name} (Attempt {attempt + 1})")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    break  # Break inner retry loop on success
                    
                except Exception as e:
                    last_error = e
                    err_msg = str(e).upper()
                    
                    # Exponential backoff for temporary remote 503 traffic spikes
                    if "503" in err_msg or "UNAVAILABLE" in err_msg:
                        if attempt < max_retries - 1:
                            print(f"{model_name} busy. Retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                    break  # Break out to try fallback model if it's a structural 400/401/403/404 error
            
            if response:
                break  # Stop trying fallback models if primary succeeded

        if response and response.text:
            return jsonify({"analysis": response.text}), 200
        else:
            raise last_error if last_error else Exception("Unknown error occurred during processing.")

    except Exception as e:
        err_msg = str(e).upper()
        print(f"Error caught in processing pipeline: {err_msg}")
        
        if "503" in err_msg or "UNAVAILABLE" in err_msg:
            return jsonify({"error": "Gemini servers are currently overloaded. Please wait a moment and try again."}), 503
        elif "403" in err_msg or "401" in err_msg or "APIKEY" in err_msg:
            return jsonify({"error": "Authentication failed. Please verify your GEMINI_API_KEY value inside the main folder .env file."}), 403
        elif "404" in err_msg:
            return jsonify({"error": "Targeted model generation route was not found. Please verify SDK compatibility."}), 404
        
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)