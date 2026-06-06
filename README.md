# AI Resume & Job Description Analyzer

## Overview
**AI Resume & Job Description Analyzer** is a web-based application that evaluates how well a candidate’s resume matches a given job description. The system utilizes a Large Language Model (**Google Gemini**) to perform comprehensive semantic analysis rather than simple, surface-level keyword matching, providing deep, meaningful, and actionable insights.

This project is specifically engineered for students, job seekers, and early-career professionals to decode critical skill gaps, refine application profiles, and dramatically improve their resumes for closer career alignment.

---

## Problem Statement
Many candidates distribute their resumes across application channels without clear confirmation of whether their credentials truly align with the targeted job description. This structural disconnect leads to low Applicant Tracking System (ATS) optimization scores, recurrent automatic rejections, and pervasive uncertainty regarding technical or domain-specific missing skills.

### The Solution
The application provides an automated processing channel allowing users to upload:
* **A Resume (PDF)**
* **A Job Description (PDF)**

The backend handles multi-stream text extraction across both documents, optimizes the text inputs into a specialized, structurally bounded prompt payload, sends the content to a Gemini LLM, and returns a detailed structured analysis containing:
* **Skill match percentage metrics**
* **Explicit matching competencies**
* **Critical missing skills and tools**
* **Targeted resume improvement recommendations**

---

## Key Features
* 📂 **Resume PDF Ingestion:** Smooth extraction handling for multi-page applicant CV formats.
* 📄 **Job Description PDF Ingestion:** Dynamic parsing for enterprise job specification sheets.
* ⚙️ **Automated Document Text Extraction:** Native backend stream conversion minimizing raw binary overhead.
* 🧠 **AI-Powered Semantic Comparison:** Advanced multi-vector matching through deep contextual analysis.
* 📊 **Structured Analysis Matrix Output:** Intuitive layout breakdown for direct scannability.
* ⚡ **Lightweight Decoupled Architecture:** Clean client-server separation for faster localized load states.
* 🔌 **Real-Time LLM Integration:** Live asynchronous generation processing handled straight from the source API.

---

## System Workflow

```text
[User Uploads Elements] -> (Resume PDF & Job Description PDF)
                                    │
                                    ▼
[Backend Processor]      -> (Automated PDF Text Extraction Layers)
                                    │
                                    ▼
[Orchestration Engine]  -> (Generation of Targeted Comparison Prompt Matrix)
                                    │
                                    ▼
[Gemini LLM Processing] -> (Semantic Evaluation & Gap Architecture Mapping)
                                    │
                                    ▼
[API Delivery Stream]   -> (Structured Response Serialization)
                                    │
                                    ▼
[Client Frontend View]  -> (Real-time Dynamic UI Output Rendering)

```
Technology Stack
Frontend Layer
HTML5: Clean structural layout foundations.

JavaScript (Vanilla ES6+): Asynchronous request interception via the native Fetch API for non-blocking browser workflows.

Backend Layer
Python 3.10+: Robust application runtime engine.

Flask: Agile micro-framework configuring secure API routing paths.

PyPDF: Secure binary parsing wrapper for server-side text compilation.

python-dotenv: Environment isolation manager protecting runtime parameter contexts.

AI Engine Layer
Google Gemini API: Core semantic analytical processing engine.

google-genai SDK: Next-generation official integration framework libraries.

Project Structure
Plaintext
JDANALYSER/
│
├── frontend/
│   ├── index.html          # UI view structures & modern style presentations
│   └── script.js           # Client-side form handler & API fetching controls
│
├── backend/
│   ├── app.py              # Main Flask application engine & routing logic
│   ├── .env                # Private local environment security parameters
│   └── venv/               # Isolated local Python runtime workspace
│
└── README.md
