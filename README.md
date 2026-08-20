# 🚀 AI Resume Analyzer

<div align="center">

**An AI-powered web application that analyzes PDF resumes, scores them against ATS standards, matches them to job descriptions, and generates tailored interview questions.**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://ai-resume-analyzer-kappa.vercel.app)

[Live Demo](https://ai-resume-analyzer-kappa.vercel.app) · [Report Bug](../../issues) · [Request Feature](../../issues)

</div>

---

## 📖 Overview

**AI Resume Analyzer** helps job seekers understand exactly how their resume will perform in front of an Applicant Tracking System (ATS) — and in front of a human recruiter. Upload a PDF resume, optionally paste a job description, and get:

- An **ATS Optimization Score** out of 100
- A **skill breakdown** across key technical categories
- **Job description match** analysis
- **AI-rewritten bullet points** for stronger impact
- **Personalized interview questions** based on your actual skill set

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **PDF Text Extraction** | Extracts resume text in-memory (no disk writes) using `PyPDF2` |
| 🧠 **Skill Categorization** | Automatically detects and groups skills into Programming Languages, Frameworks, Databases, Data Science, and Cloud/DevOps |
| 📊 **ATS Optimization Score** | Scores your resume out of 100 based on industry-standard keywords and structure |
| 🎯 **JD Matching** | Compares your resume against a job description to surface match strength and gaps |
| ✍️ **AI Bullet Rewriter** | Rewrites weak resume bullet points into stronger, achievement-oriented statements |
| 🗣️ **Interview Question Generator** | Generates role-specific interview questions based on detected skills |
| 💎 **Premium UI** | Dark theme with glassmorphism, fully responsive, smooth animations |
| 🔌 **REST API** | Headless JSON endpoints for programmatic/async analysis |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **PDF Processing:** PyPDF2
- **Frontend:** HTML5, Vanilla CSS3 (Glassmorphism), JavaScript
- **Deployment:** Vercel
- **Fonts/Icons:** Google Fonts, Font Awesome

---

## 📂 Project Structure

```
AI-Resume-Analyzer/
├── app.py                 # Main Flask application & routes
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
```

---

## ⚙️ How It Works

1. User uploads a **PDF resume** (and optionally a job description) via the web UI or API.
2. `extract_text_from_stream()` reads the PDF **in-memory** (`io.BytesIO`) — nothing touches disk.
3. `analyze_resume_comprehensive()` scores the resume and returns skills, ATS score, breakdown, heatmap, and recommendations.
4. If a job description is provided, `calculate_jd_match()` compares it against the resume.
5. `generate_interview_questions()` builds tailored interview prep from the detected skills.
6. Sample resume bullets are passed through `batch_rewrite_bullets()` for AI-enhanced rewrites.
7. Results are rendered in the UI — or returned as JSON via the API.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/amrita-2004/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Then open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🔌 API Reference

The app also exposes headless JSON endpoints for integration into other tools.

### `POST /api/analyze`
Analyze a resume (and optional job description).

```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -F "resume=@resume.pdf" \
  -F "job_description=Looking for a Python backend developer..."
```

**Response**
```json
{
  "status": "success",
  "filename": "resume.pdf",
  "ats_score": 82,
  "breakdown": { "...": "..." },
  "skills": { "...": "..." },
  "recommendations": ["..."],
  "heatmap": { "...": "..." },
  "career_recommendations": ["..."],
  "jd_match": { "...": "..." },
  "interview_prep": { "...": "..." }
}
```

### `POST /api/rewrite-bullet`
Rewrite a single resume bullet point.

```bash
curl -X POST http://127.0.0.1:5000/api/rewrite-bullet \
  -H "Content-Type: application/json" \
  -d '{"bullet": "Responsible for managing the team"}'
```

### `POST /api/interview-prep`
Generate interview questions for a given skill set and role.

```bash
curl -X POST http://127.0.0.1:5000/api/interview-prep \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Python", "Flask", "SQL"], "role": "Backend Developer"}'
```

---

## 🖼️ Screenshots

> _Add screenshots or a short GIF of the upload flow and results dashboard here for maximum impact on your GitHub profile._

---

## 🗺️ Roadmap

- [ ] OCR support for scanned/image-based PDFs
- [ ] Semantic (embedding-based) JD matching instead of pure keyword matching
- [ ] Support for DOCX resumes
- [ ] User accounts & resume history
- [ ] Export analysis report as PDF

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Author

**Amrita**
- GitHub: [@amrita-2004](https://github.com/amrita-2004)

---

<div align="center">

If this project helped you, consider giving it a ⭐!

</div>
