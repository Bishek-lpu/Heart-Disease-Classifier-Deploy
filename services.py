import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import warnings
import logging

warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)

import numpy as np  # noqa: E402
import cv2  # noqa: E402
import tensorflow as tf  # noqa: E402
import joblib  # noqa: E402
from openai import OpenAI  # noqa: E402
from io import BytesIO  # noqa: E402
from scipy.signal import find_peaks  # noqa: E402
from datetime import datetime  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # noqa: E402
from reportlab.lib.units import inch  # noqa: E402
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # noqa: E402

# -------------------------------
# LOAD MODELS
# -------------------------------
cnn_model = tf.keras.models.load_model("heart_ecg_cnn.h5")
ml_model = joblib.load("heart_model.pkl")

classes = ["Normal", "MI", "History_MI", "Abnormal"]

CLINICAL_FEATURE_COLS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "age_group",
    "chol_level",
    "thalach_level",
    "age_chol_interaction",
    "oldpeak_log",
]


def get_ai_suggestion(input_type, data, result):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model_name = "gpt-3.5-turbo"

    prompt = f"""
    You are an experienced cardiologist AI assistant. A patient has undergone heart disease analysis.

    INPUT TYPE: {input_type}
    PATIENT / MODEL DATA: {data}
    MODEL PREDICTION: {result}

    Provide a concise interpretation (not a formal diagnosis). Use EXACTLY these 4 section headers:
    Risk Level:
    Explanation:
    Actionable Steps:
    When to see a doctor:

    Do not use markdown formatting like asterisks (**). Use plain text with clear line breaks.
    Be calm, clear, and avoid causing undue alarm. This is decision support, not a diagnosis.
    """
    try:
        response = client.chat.completions.create(
            model=model_name, messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI service error: {e!s}"


def clinical_risk_percent_and_tier(input_scaled):
    try:
        if hasattr(ml_model, "predict_proba"):
            p = ml_model.predict_proba(input_scaled)[0]
            p_disease = float(p[1] if len(p) > 1 else p[0])
        else:
            p_disease = 0.5
    except Exception:
        p_disease = 0.5
    risk_pct = round(100.0 * p_disease, 1)
    if risk_pct < 35:
        return risk_pct, "Low"
    if risk_pct < 65:
        return risk_pct, "Medium"
    return risk_pct, "High"


def contributing_factors(age, sex, trestbps, chol, thalach, exang, oldpeak, cp):
    f = []
    if age >= 55:
        f.append("Age in a range where cardiovascular risk is often reassessed.")
    if chol >= 240:
        f.append("Cholesterol value that often warrants follow-up.")
    if trestbps >= 140:
        f.append("Resting blood pressure in a range that may need monitoring.")
    if thalach < 120 and age < 60:
        f.append("Relatively low maximum heart rate.")
    if exang == 1:
        f.append("Exercise angina (yes).")
    if oldpeak >= 2.0:
        f.append("ST depression (oldpeak) is a notable signal.")
    if cp in (0, 1):
        f.append("Chest pain pattern may influence risk.")
    if not f:
        f.append("Continue routine preventive care.")
    return f[:5]


def preprocess_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img / 255.0
    img = cv2.resize(img, (240, 200))
    return img


def predict_cnn(img):
    cnn_input = img.reshape(1, 200, 240, 1)
    pred = cnn_model.predict(cnn_input, verbose=0)
    class_id = int(np.argmax(pred))
    return classes[class_id], float(np.max(pred))


def waveform_analysis(img):
    wave = np.mean(img, axis=0)
    wave = (wave - wave.min()) / (wave.max() - wave.min() + 1e-8)
    peaks, _ = find_peaks(wave, distance=20)
    return wave.tolist(), peaks.tolist(), len(peaks) * 6, float(np.std(wave))


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_report_pdf(
    title, mode_label, input_block, result_block, ai_text, contact_info=""
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0f766e"),
        fontSize=12,
    )

    safe_ai_text = _escape(ai_text)[:12000].replace("\n", "<br/>")
    for header in [
        "Risk Level:",
        "Explanation:",
        "Actionable Steps:",
        "When to see a doctor:",
    ]:
        safe_ai_text = safe_ai_text.replace(
            header, f"<b><font color='#0f766e'>{header}</font></b>"
        )

    story = [
        Paragraph(f"<b>{_escape(title)}</b>", styles["Title"]),
        Paragraph(
            f"<i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>", body
        ),
        Spacer(1, 0.2 * inch),
        Paragraph(
            "Medical disclaimer: This report is for informational support only.", body
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("Mode", h2),
        Paragraph(_escape(mode_label), body),
        Spacer(1, 0.1 * inch),
        Paragraph("Inputs & context", h2),
        Paragraph(_escape(input_block)[:15000] or "—", body),
        Spacer(1, 0.1 * inch),
        Paragraph("Model output", h2),
        Paragraph(_escape(result_block)[:8000] or "—", body),
        Spacer(1, 0.1 * inch),
        Paragraph("AI summary (non-clinical)", h2),
        Paragraph(safe_ai_text or "—", body),
    ]

    if contact_info:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("Doctor Contact Information", h2))
        story.append(
            Paragraph(
                f"<b><font color='#ef4444'>{_escape(contact_info)}</font></b>", body
            )
        )

    doc.build(story)
    return buffer.getvalue()
