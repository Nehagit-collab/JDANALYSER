AI Resume & Job Description Analyzer
Overview
-------------------
A web-based application that analyzes how well a resume matches a job description using Google Gemini LLM. It provides semantic comparison instead of keyword matching.

Features
------------------
Upload Resume (PDF)
Upload Job Description (PDF)
AI-based skill match analysis
Matching & missing skills
Resume improvement suggestions

Tech Stack
-------------------
Frontend: HTML, JavaScript
Backend: Python, Flask
AI: Google Gemini (google-genai)
PDF Parsing: PyPDF

Project Structure
-----------------
JDANALYSER/
├── frontend/
│   ├── index.html
│   └── script.js
├── backend/
│   ├── app.py
│   └── .env
└── README.md

Setup & Run
....................
Install dependencies
pip install flask pypdf python-dotenv google-genai
Set API key (backend/.env)
GEMINI_API_KEY=your_api_key_here
Run backend
python app.py
Open frontend
Open index.html in a browser.

Output
//////////////////
Skill match percentage
Matching skills
Missing skills
Resume improvement suggestions

Use Case
///////////////////
Job seekers
Students
Resume screening demos
AI internship projects

Author
----------------------
Neha Sunil
BCA Student | AI & ML Enthusiast
