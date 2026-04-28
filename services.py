import os
import gc
import warnings
import logging
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("absl").setLevel(logging.ERROR)


# ── Constants (no heavy libs needed) ─────────────────────────────────────────
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
_ECG_CLASSES = ["Normal", "MI", "History_MI", "Abnormal"]

# ── Lazy singletons ───────────────────────────────────────────────────────────
# Each is loaded once on first use, never at import time.
_cnn_session = None
_cnn_input_name = None
_ml_model = None
_scaler = None


def _get_cnn():
    global _cnn_session, _cnn_input_name
    if _cnn_session is None:
        import onnxruntime as ort  # ~30 MB, deferred

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1   # 1 thread = less memory on 512 MB hosts
        opts.inter_op_num_threads = 1
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        path = os.path.join(os.path.dirname(__file__), "heart_ecg_cnn.onnx")
        _cnn_session = ort.InferenceSession(
            path, sess_options=opts, providers=["CPUExecutionProvider"]
        )
        _cnn_input_name = _cnn_session.get_inputs()[0].name
    return _cnn_session, _cnn_input_name


def _get_ml_models():
    global _ml_model, _scaler
    if _ml_model is None:
        import joblib  # fast, but still deferred

        base = os.path.dirname(__file__)
        _ml_model = joblib.load(os.path.join(base, "heart_model.pkl"))
        _scaler = joblib.load(os.path.join(base, "scaler.pkl"))
    return _ml_model, _scaler


# Public aliases used by app.py
@property
def ml_model(_):  # noqa – accessed via module-level helper below
    return _get_ml_models()[0]


@property
def scaler(_):
    return _get_ml_models()[1]


# Simpler: just expose getter functions app.py can call
def get_ml_model():
    return _get_ml_models()[0]


def get_scaler():
    return _get_ml_models()[1]


# ── AI suggestion (lazy-loads openai) ─────────────────────────────────────────
def get_ai_suggestion(input_type, data, result):
    """Call OpenAI ChatGPT for a plain-English clinical summary."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return (
            "AI interpretation unavailable. Set OPENAI_API_KEY in your environment "
            "or .env file (https://platform.openai.com/api-keys)."
        )

    from openai import OpenAI  # deferred: only loaded when AI summary is requested

    client = OpenAI(api_key=api_key)
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
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI service error: {e!s}"


# ── Clinical helpers ──────────────────────────────────────────────────────────
def clinical_risk_percent_and_tier(input_scaled):
    ml_model, _ = _get_ml_models()
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


# ── Image / ECG helpers (lazy-loads cv2) ─────────────────────────────────────
def preprocess_image(img):
    import cv2  # deferred: libopencv loads ~20 shared libs

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img / 255.0
    img = cv2.resize(img, (240, 200))
    return img


def predict_cnn(img):
    session, input_name = _get_cnn()
    cnn_input = img.reshape(1, 200, 240, 1).astype(np.float32)
    outputs = session.run(None, {input_name: cnn_input})
    pred = outputs[0]
    class_id = int(np.argmax(pred))
    confidence = float(np.max(pred))
    del cnn_input, outputs, pred   # free temporary arrays immediately
    gc.collect()
    return _ECG_CLASSES[class_id], confidence


def waveform_analysis(img):
    from scipy.signal import find_peaks  # deferred: scipy is large

    wave = np.mean(img, axis=0)
    wave = (wave - wave.min()) / (wave.max() - wave.min() + 1e-8)
    peaks, _ = find_peaks(wave, distance=20)
    return wave.tolist(), peaks.tolist(), len(peaks) * 6, float(np.std(wave))


# ── PDF report (lazy-loads reportlab) ────────────────────────────────────────
def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_report_pdf(
    title, mode_label, input_block, result_block, ai_text, contact_info=""
):
    # reportlab deferred: large pure-Python package, only needed for /api/report
    from io import BytesIO
    from datetime import datetime
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

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
