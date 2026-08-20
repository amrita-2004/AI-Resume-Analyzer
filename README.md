# 🚀 AI Resume Analyzer

<div align="center">

An AI-powered web application that analyzes PDF resumes, scores them against ATS standards, matches them to job descriptions, and generates tailored interview questions.

[Live Demo](#) · [Report Bug](https://github.com/amrita-2004/AI-Resume-Analyzer/issues) · [Request Feature](https://github.com/amrita-2004/AI-Resume-Analyzer/issues)

</div>

---

## 📖 Overview

**AI Resume Analyzer** helps job seekers understand exactly how their resume will perform in front of an Applicant Tracking System (ATS) — and in front of a human recruiter. Upload a PDF resume, optionally paste a job description, and get:

* An **ATS Optimization Score** out of 100
* A skill breakdown across key technical categories
* Job description match analysis and gap detection
* AI-rewritten bullet points for stronger impact
* Personalized interview questions based on your actual skill set

---

## 🖼️ Screenshots

<div align="center">

### 📤 Dashboard & Resume Upload
![Upload Interface](https://via.placeholder.com/800x450/0f172a/6366f1?text=AI+Resume+Analyzer+-+Glassmorphism+Upload+UI)
*Clean, dark-themed UI with glassmorphism design for seamless file upload and JD parsing.*

<br>

### 📊 ATS Score & Analytics Overview
![ATS Analytics Dashboard](https://via.placeholder.com/800x450/0f172a/38bdf8?text=ATS+Score+%26+Skill+Categorization+Heatmap)
*Real-time breakdown of ATS scores, detected skill categories, and keyword heatmap.*

<br>

### ✍️ AI Bullet Rewriter & Interview Prep
![AI Suggestions](https://via.placeholder.com/800x450/0f172a/a855f7?text=AI+Bullet+Rewriter+%26+Tailored+Interview+Prep)
*Achievement-oriented bullet rewrites alongside custom interview questions generated from your skills.*

</div>

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 📄 **PDF Text Extraction** | Extracts resume text in-memory (no disk writes) using `PyPDF2` |
| 🧠 **Skill Categorization** | Automatically detects and groups skills into Programming, Frameworks, Databases, Data Science, and Cloud/DevOps |
| 📊 **ATS Optimization Score** | Scores your resume out of 100 based on industry-standard keywords and structure |
| 🎯 **JD Matching** | Compares your resume against a job description to surface match strength and skill gaps |
| ✍️ **AI Bullet Rewriter** | Rewrites weak resume bullet points into stronger, achievement-oriented statements |
| 🗣️ **Interview Generator** | Generates role-specific interview questions based on detected skills |
| 💎 **Premium UI** | Dark theme with glassmorphism, fully responsive layouts, and smooth CSS animations |
| 🔌 **REST API** | Headless JSON endpoints for programmatic/async analysis |

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **PDF Processing:** PyPDF2
* **Frontend:** HTML5, Vanilla CSS3 (Glassmorphism), JavaScript
* **Deployment:** Vercel
* **Fonts & Icons:** Google Fonts, Font Awesome

---

## 📂 Project Structure

```text
AI-Resume-Analyzer/
├── app.py                 # Main Flask application & API routes
├── analyzer.py             # Core resume analysis & ATS scoring logic
├── jd_matcher.py            # Job description matching engine
├── ai_rewriter.py           # Bullet point rewriting logic
├── interview_gen.py         # Interview question generator
├── generate_sample.py       # Sample resume/data generator
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS, JS, and image assets
├── requirements.txt         # Python dependencies
├── vercel.json               # Vercel deployment config
└── README.md
