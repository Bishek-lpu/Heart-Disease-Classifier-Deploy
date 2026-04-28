# Cardio Risk Assistant 🫀

![Cardio Risk Assistant Banner](static/heart.png)

A comprehensive, multi-modal clinical decision support system designed to evaluate cardiovascular disease risks. This application combines traditional machine learning, computer vision, and generative AI into a unified, user-friendly web dashboard.

> **Disclaimer:** This tool is for educational and decision-support purposes only and does not provide formal medical diagnoses.

---

## ✨ Key Features

- **Clinical Tabular Analysis**: Input 13 distinct vital signs (age, cholesterol, resting BP, etc.) to generate a probabilistic risk score and tier using a pre-trained Scikit-Learn classification model.
- **Computer Vision on ECG**: Upload raw 1D/2D ECG image strips. A custom-trained TensorFlow Convolutional Neural Network (CNN) automatically classifies the rhythm pattern (Normal, MI, History of MI, Abnormal) with confidence intervals.
- **Generative AI Summaries**: Powered by the **OpenAI GPT-3.5 API**, the assistant translates complex model outputs into plain-English, non-diagnostic explanations and actionable lifestyle steps.
- **Emergency Contact Routing**: Automatically flags medium/high clinical risks and abnormal ECGs, dynamically injecting specialist contact information into the UI and generated reports.
- **PDF Report Generation**: Instantly export a comprehensive medical summary using `reportlab`, complete with patient inputs, model classifications, AI insights, and relevant contact information.
- **Premium UI/UX**: A highly responsive, modern dark-mode aesthetic utilizing glassmorphism, micro-animations, and asynchronous Javascript interactions.

---

## 🛠️ Tech Stack

- **Backend framework**: Python, Flask, Werkzeug
- **Machine Learning**: TensorFlow / Keras (CNN), Scikit-Learn, Joblib, Pandas, NumPy, OpenCV (cv2), SciPy
- **Generative AI**: OpenAI Python SDK (`gpt-3.5-turbo`)
- **Report Generation**: ReportLab
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), Vanilla JS (Fetch API)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- An active OpenAI API Key

### Installation

1. **Clone the repository** (or download the source code)
   ```bash
   git clone https://github.com/yourusername/Cardio-Risk-Assistant.git
   cd Cardio-Risk-Assistant
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API Key**
   Ensure your OpenAI API key is correctly configured. Currently, the key is passed directly in `services.py`, but it is highly recommended to manage this via secure environment variables in a production environment.

### Running the Application

Start the Flask development server:

```bash
python app.py
```

Once running, navigate to `http://localhost:8501/` in your web browser to view the landing page and access the dashboard.

---

## 📂 Project Structure

```text
📦 Cardio-Risk-Assistant
 ┣ 📂 static/               # CSS styles, JavaScript logic, and images
 ┃ ┣ 📜 app.js              # Frontend Fetch API logic
 ┃ ┣ 📜 style.css           # Core dashboard styling
 ┃ ┣ 📜 landing.css         # Landing page styling
 ┃ ┗ 📜 heart.png           # Hero banner image
 ┣ 📂 templates/            # HTML templates
 ┃ ┣ 📜 index.html          # Main application dashboard
 ┃ ┗ 📜 landing.html        # Entry landing page
 ┣ 📜 app.py                # Main Flask application and API routes
 ┣ 📜 services.py           # Core ML inference, OpenAI logic, and PDF generation
 ┣ 📜 heart_ecg_cnn.h5      # Trained TensorFlow CNN model
 ┣ 📜 heart_model.pkl       # Trained Scikit-Learn tabular model
 ┣ 📜 scaler.pkl            # Data scaler for tabular inputs
 ┣ 📜 requirements.txt      # Python dependencies
 ┣ 📜 .gitignore            # Ignored files for version control
 ┗ 📜 README.md             # Project documentation
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to open a Pull Request or issue if you'd like to improve the models, add new vitals, or refine the UI.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
