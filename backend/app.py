import os
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pypdf import PdfReader
from dotenv import load_dotenv
# Import the modern Google GenAI SDK
from google import genai

# Load environment variables from .env file
load_dotenv()

# CHANGED: Configure Flask to look one folder back for your frontend assets
# UPDATE THIS BLOCK: Add static_url_path=''
app = Flask(
    __name__, 
    static_url_path='',  # This tells Flask to serve script.js directly at the root level!
    static_folder='../frontend', 
    template_folder='../frontend'
)
CORS(app)

# Initialize the Gemini Client
# It automatically looks for the GEMINI_API_KEY environment variable
try:
    client = genai.Client()
except Exception as e:
    raise RuntimeError("Failed to initialize Gemini Client. Ensure GEMINI_API_KEY is set in your venv or .env file.") from e

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

# CHANGED: This route now serves your frontend user interface file directly
@app.route("/", methods=["GET"])
def health_check():
    """Serves the main frontend application file."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # 1. Fetch files from the incoming request
        resume_file = request.files.get("resume")
        jd_file = request.files.get("jd")

        if not resume_file or not jd_file:
            return jsonify({"error": "Both Resume PDF and Job Description PDF are required."}), 400

        # 2. Extract text from both PDFs
        resume_text = extract_text_from_pdf(resume_file)
        jd_text = extract_text_from_pdf(jd_file)

        if not resume_text or not jd_text:
            return jsonify({"error": "Could not extract text from one or both PDFs. Ensure they aren't scanned images."}), 400

        # 3. Construct the prompt for Gemini 3
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

        # 4. Define our preferred model sequence and retry parameters
        models_to_try = ['gemini-3.5-flash', 'gemini-3.1-flash-lite']
        max_retries = 2
        retry_delay = 2  # initial delay in seconds
        
        response = None
        last_error = None

        # Outer loop iterates through models (Primary -> Fallback)
        for model_name in models_to_try:
            # Inner loop handles temporary 503 traffic spikes for the active model
            for attempt in range(max_retries):
                try:
                    print(f"Sending request using model: {model_name} (Attempt {attempt + 1})")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    # If execution reaches here, it succeeded! Break inner loop
                    break
                    
                except Exception as e:
                    last_error = e
                    err_msg = str(e).upper()
                    
                    # If it's a 503/Congestion error, wait a moment and try again
                    if "503" in err_msg or "UNAVAILABLE" in err_msg:
                        if attempt < max_retries - 1:
                            print(f"{model_name} busy. Retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                    
                    # If it's a structural error (like 400 or 403), break immediately to try the fallback model
                    break
            
            # If we successfully got a response from the current model, stop trying other models
            if response:
                break

        # 5. Handle final response or throw terminal error
        if response and response.text:
            return jsonify({
                "analysis": response.text
            }), 200
        else:
            # If everything failed, bubble up the exception text
            raise last_error if last_error else Exception("Unknown error occurred during processing.")

    except Exception as e:
        err_msg = str(e).upper()
        # Send clean user-facing error strings back to the UI
        if "503" in err_msg or "UNAVAILABLE" in err_msg:
            return jsonify({"error": "Gemini servers are currently overloaded. Please wait a moment and click Analyze again."}), 503
        elif "403" in err_msg or "APIKEY" in err_msg:
            return jsonify({"error": "Authentication failed. Please verify your GEMINI_API_KEY environment variable."}), 403
        
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure port 5000 is matching your frontend fetch call
    app.run(debug=True, port=5000)
    
# Initialize the Gemini Client explicitly using the environment variable
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is completely missing from environment variables.")
    
    # Passing api_key directly prevents the SDK from falling back to OAuth tokens
    client = genai.Client(api_key=api_key)
except Exception as e:
    raise RuntimeError("Failed to initialize Gemini Client. Check your Render Environment variables.") from e