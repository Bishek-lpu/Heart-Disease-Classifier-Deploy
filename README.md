<div align="center">

<!-- Animated Header -->
<img src="static/heart.png" alt="Cardio Risk Assistant" width="160" style="border-radius:24px;" />

<h1>
  <img src="https://readme-typing-svg.demolab.com?font=Outfit&size=36&duration=3000&pause=800&color=0EA5E9&center=true&vCenter=true&width=700&lines=Cardio+Risk+Assistant+AI+%F0%9F%AB%80;Multi-Modal+Heart+Disease+Analysis;Clinical+Decision+Support+System" alt="Typing SVG" />
</h1>

<p align="center">
  <strong>A production-ready, multi-modal AI system for cardiovascular risk assessment — combining classical ML, CNN computer vision, and large language model summaries.</strong>
</p>

<br/>

<!-- Badges Row 1 -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.1.1-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/ONNX_Runtime-1.21-005CED?style=for-the-badge&logo=onnx&logoColor=white" alt="ONNX"/>
  <img src="https://img.shields.io/badge/scikit--learn-1.5.2-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" alt="Scikit-learn"/>
</p>

<!-- Badges Row 2 -->
<p align="center">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render"/>
  <img src="https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<!-- Animated Stats -->
<p align="center">
  <img src="https://img.shields.io/badge/ECG_Classes-4-dc2626?style=flat-square" alt="ECG Classes"/>
  <img src="https://img.shields.io/badge/Clinical_Features-18-0ea5e9?style=flat-square" alt="Features"/>
  <img src="https://img.shields.io/badge/Theme-Dark_%2F_Light-8b5cf6?style=flat-square" alt="Theme"/>
  <img src="https://img.shields.io/badge/Responsive-Mobile_%26_Desktop-10b981?style=flat-square" alt="Responsive"/>
</p>

<br/>

> ⚠️ **Medical Disclaimer:** This tool is for **educational and decision-support purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment.

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

**Cardio Risk Assistant AI** is a full-stack clinical decision support application that evaluates cardiovascular disease risk through two independent, complementary analysis modes:

| Mode | Input | Model | Output |
|------|-------|-------|--------|
| 🩺 **Clinical Risk** | 13 patient vitals + derived features | Scikit-Learn Classifier | Risk % score, tier (Low/Medium/High), contributing factors |
| 📈 **ECG Analysis** | Raw ECG image (JPG/PNG) | ONNX CNN (optimised from TensorFlow) | Classification (Normal / MI / History_MI / Abnormal), waveform chart, heart rate estimate |

Both modes feed results into a **Gemini LLM** (Google Generative AI) which generates a plain-English summary with lifestyle recommendations — all rendered in a premium, responsive dark/light theme UI.

---

## 🌐 Live Demo

```
Landing Page : http://localhost:8501/
App Page     : http://localhost:8501/app
```

> Deploy on **Render** using the included `render.yaml`, or self-host with **Docker** using the included `Dockerfile` and `docker-compose.yml`.

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

**🩺 Clinical Tabular Analysis**
- 13 raw vitals + 5 engineered features (age group, cholesterol tier, interaction terms, log transforms)
- Probability-based risk score (0–100%)
- Tiered classification: Low / Medium / High
- Explainable contributing factor bullets

</td>
<td width="50%">

**📈 ECG Image Classification**
- CNN classifies 4 categories: `Normal`, `MI`, `History_MI`, `Abnormal`
- Clinical ECG-paper-style waveform chart (Canvas 2D, ECG grid, R-peak markers)
- Heuristic heart rate & signal spread estimation

</td>
</tr>
<tr>
<td>

**🤖 Generative AI Summaries**
- Powered by **Google Gemini** (`gemini-2.5-flash` default)
- Structured output: Risk Level → Explanation → Actionable Steps → When to see a doctor
- Configurable model via environment variable

</td>
<td>

**📄 PDF Report Export**
- Professional one-page PDF via `reportlab`
- Includes: inputs, model output, AI summary, timestamp, disclaimer
- Instant download, no server-side storage

</td>
</tr>
<tr>
<td>

**🎨 Premium UI/UX**
- Dark / Light theme with system-default detection
- Theme persists via `localStorage` across pages
- Glassmorphism cards, animated tab transitions, micro-animations

</td>
<td>

**📱 Fully Responsive**
- Mobile-first layout (≤600px, ≤900px breakpoints)
- Touch-friendly inputs (`font-size: 16px` prevents iOS auto-zoom)
- Drag-and-drop ECG image upload

</td>
</tr>
</table>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser Client                           │
│  landing.html ──(theme.js)──► index.html                        │
│       │                            │                            │
│  landing.css                   style.css + app.js               │
└────────────────────┬────────────────────────────────────────────┘
                     │  HTTP (Fetch API / multipart)
┌────────────────────▼────────────────────────────────────────────┐
│                    Flask Application  (app.py)                  │
│                                                                 │
│  GET  /          → landing.html                                 │
│  GET  /app       → index.html                                   │
│  POST /api/clinical ──► services.py ──► scikit-learn model      │
│  POST /api/ecg      ──► services.py ──► ONNX CNN + waveform     │
│  POST /api/report   ──► services.py ──► ReportLab PDF           │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┴──────────────┐
         │        services.py       │
         │                          │
         │  ┌─────────────────┐     │
         │  │  Scikit-Learn   │     │  ← heart_model.pkl
         │  │  Classifier     │     │  ← scaler.pkl
         │  └─────────────────┘     │
         │                          │
         │  ┌─────────────────┐     │
         │  │  ONNX Runtime   │     │  ← heart_ecg_cnn.onnx
         │  │  CNN (ECG)      │     │
         │  └─────────────────┘     │
         │                          │
         │  ┌─────────────────┐     │
         │  │  Google Gemini  │     │  ← GEMINI_API_KEY
         │  │  LLM Summary    │     │
         │  └─────────────────┘     │
         │                          │
         │  ┌─────────────────┐     │
         │  │  ReportLab PDF  │     │
         │  └─────────────────┘     │
         └──────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Web Framework** | Flask | 3.1.1 | REST API + template serving |
| **Production Server** | Gunicorn | 23.0.0 | WSGI server for Render/Docker |
| **ML — Tabular** | Scikit-Learn | 1.5.2 | Binary heart disease classifier |
| **ML — Inference** | ONNX Runtime | 1.21.0 | Optimised CNN inference (no TF) |
| **Data Processing** | NumPy / Pandas / SciPy | 1.26.4 / 2.2.3 / 1.11.4 | Feature engineering, peak detection |
| **Image Processing** | OpenCV (headless) | 4.10.0 | ECG preprocessing, grayscale |
| **Generative AI** | Google Generative AI SDK | latest | Clinical plain-English summaries |
| **PDF Generation** | ReportLab | 4.2.5 | Export clinical reports |
| **Config** | python-dotenv | 1.0.1 | Secure environment variable loading |
| **Frontend** | HTML5 + CSS3 + Vanilla JS | — | Responsive dashboard, Canvas 2D |
| **Containerisation** | Docker + Docker Compose | — | Portable deployment |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.9+**
- A **Google Gemini API key** → [Get one free](https://aistudio.google.com/app/apikey)
- Git with **LFS** (for model files)

### 1. Clone the repository

```bash
git clone https://github.com/Bishek-lpu/Heart-Disease-Classifier-Deploy.git
cd Heart-Disease-Classifier-Deploy

# Pull LFS-tracked model files
git lfs pull
```

### 2. Create & activate virtual environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Required: Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: override default model
GEMINI_MODEL=gemini-2.5-flash
```

### 5. Run the development server

```bash
python app.py
```

Open your browser at **[http://localhost:8501](http://localhost:8501)**

---

## 🐳 Docker Deployment

### Build & run with Docker Compose

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

### Pull the pre-built image

```bash
docker pull bisheklpu/heart-disease-classifier:1.0.3
docker run -p 80:80 --env-file .env bisheklpu/heart-disease-classifier:1.0.3
```

The application will be available at **[http://localhost:80](http://localhost:80)**

### Deploy to Render

The project includes a `render.yaml` for one-click Render deployment:

1. Push your code to GitHub
2. Connect your repository to [Render](https://render.com)
3. Set `GEMINI_API_KEY` in Render's Environment Variables
4. Deploy — Render auto-detects `render.yaml`

---

## 📂 Project Structure

```
📦 Heart-Disease-Classifier-Deploy
 ┣ 📂 static/
 ┃ ┣ 📜 app.js              # Fetch API logic, ECG Canvas chart renderer
 ┃ ┣ 📜 theme.js            # Dark/light theme manager (system default + localStorage)
 ┃ ┣ 📜 style.css           # App dashboard design system + light theme overrides
 ┃ ┣ 📜 landing.css         # Landing page design system + light theme overrides
 ┃ ┗ 🖼️  heart.png           # Hero banner image
 ┣ 📂 templates/
 ┃ ┣ 📜 index.html          # Main application dashboard (Clinical + ECG tabs)
 ┃ ┗ 📜 landing.html        # Marketing landing page
 ┣ 📜 app.py                # Flask routes: /, /app, /api/clinical, /api/ecg, /api/report
 ┣ 📜 services.py           # ML inference, Gemini AI, waveform analysis, PDF export
 ┣ 🧠 heart_ecg_cnn.onnx    # ONNX CNN model for ECG classification (LFS tracked)
 ┣ 🧠 heart_model.pkl       # Scikit-Learn binary classifier (LFS tracked)
 ┣ 🧠 scaler.pkl            # StandardScaler for clinical features (LFS tracked)
 ┣ 📜 requirements.txt      # Python dependencies (pinned versions)
 ┣ 📜 Dockerfile            # Multi-stage Docker build
 ┣ 📜 docker-compose.yml    # Docker Compose configuration
 ┣ 📜 render.yaml           # Render.com deployment configuration
 ┣ 📜 Procfile              # Gunicorn entrypoint for PaaS
 ┣ 📜 .env                  # Local secrets (never committed)
 ┗ 📜 README.md             # Project documentation
```

---

## 📡 API Reference

### `POST /api/clinical`
**Body:** `application/json`
```json
{
  "age": 55, "sex": 1, "cp": 0, "trestbps": 130, "chol": 245,
  "fbs": 0, "restecg": 1, "thalach": 145, "exang": 1,
  "oldpeak": 2.3, "slope": 2, "ca": 1, "thal": 2
}
```
**Returns:** `risk_pct`, `risk_tier`, `result_label`, `factors[]`, `suggestion`, `input_snapshot`, `result_snapshot`

---

### `POST /api/ecg`
**Body:** `multipart/form-data` with `file` (JPG/PNG)

**Returns:** `label`, `confidence`, `wave[]`, `peaks[]`, `hr`, `var`, `suggestion`, `result_snapshot`

---

### `POST /api/report`
**Body:** `application/json`
```json
{
  "title": "Cardio Risk — ECG",
  "mode_label": "ECG image CNN",
  "input_snapshot": "...",
  "result_snapshot": "...",
  "suggestion": "..."
}
```
**Returns:** PDF binary stream (`application/pdf`)

---

## 🔐 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | — | Google Gemini API key for AI summaries |
| `GEMINI_MODEL` | ❌ No | `gemini-2.5-flash` | Override the Gemini model name |
| `PORT` | ❌ No | `8501` | Port for Flask / Gunicorn |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ by **Bishek**

<img src="https://img.shields.io/badge/Built_with-Flask_%2B_ONNX_%2B_Gemini-0ea5e9?style=flat-square" alt="Built with"/>
&nbsp;
<img src="https://img.shields.io/badge/Deployed_on-Render_%2F_Docker-46E3B7?style=flat-square" alt="Deployed on"/>

</div>
