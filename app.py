import numpy as np
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_file
from io import BytesIO

from services import (
    CLINICAL_FEATURE_COLS,
    get_ml_model,
    get_scaler,
    clinical_risk_percent_and_tier,
    contributing_factors,
    get_ai_suggestion,
    preprocess_image,
    predict_cnn,
    waveform_analysis,
    generate_report_pdf,
)

load_dotenv()

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/app")
def index():
    return render_template("index.html")


@app.route("/api/clinical", methods=["POST"])
def predict_clinical():
    try:
        # pandas is imported here — only loaded when this endpoint is hit
        import pandas as pd

        data = request.json
        age       = float(data.get("age"))
        sex       = float(data.get("sex"))
        cp        = float(data.get("cp"))
        trestbps  = float(data.get("trestbps"))
        chol      = float(data.get("chol"))
        fbs       = float(data.get("fbs"))
        restecg   = float(data.get("restecg"))
        thalach   = float(data.get("thalach"))
        exang     = float(data.get("exang"))
        oldpeak   = float(data.get("oldpeak"))
        slope     = float(data.get("slope"))
        ca        = float(data.get("ca"))
        thal      = float(data.get("thal"))

        age_group       = pd.cut([age],    bins=[0, 40, 55, 70, 100], labels=[0, 1, 2, 3]).astype(int)[0]
        chol_level      = pd.cut([chol],   bins=[0, 200, 240, 600],   labels=[0, 1, 2]).astype(int)[0]
        thalach_level   = pd.cut([thalach],bins=[0, 100, 150, 220],   labels=[0, 1, 2]).astype(int)[0]
        age_chol_interaction = age * chol
        oldpeak_log = np.log1p(oldpeak)

        input_df = pd.DataFrame(
            [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang,
              oldpeak, slope, ca, thal, age_group, chol_level, thalach_level,
              age_chol_interaction, oldpeak_log]],
            columns=CLINICAL_FEATURE_COLS,
        )

        scaler   = get_scaler()
        ml_model = get_ml_model()

        input_scaled = scaler.transform(input_df)
        pred = int(ml_model.predict(input_scaled)[0])
        result_label = (
            "Likely heart disease"
            if pred == 1
            else "Lower likelihood (no disease class)"
        )
        risk_pct, risk_tier = clinical_risk_percent_and_tier(input_scaled)
        factors = contributing_factors(age, sex, trestbps, chol, thalach, exang, oldpeak, cp)

        input_snapshot  = f"Age {age}, sex {sex}, cp {cp}, BP {trestbps}, chol {chol}, FBS {fbs}, restECG {restecg}, max HR {thalach}, exang {exang}, oldpeak {oldpeak}, slope {slope}, ca {ca}, thal {thal}"
        result_snapshot = f"Binary class: {pred} ({result_label}) | Model risk score: {risk_pct}% | Tier: {risk_tier}"

        suggestion = get_ai_suggestion("Clinical Data", input_df.values.tolist(), result_snapshot)

        return jsonify({
            "result_label":    result_label,
            "risk_pct":        risk_pct,
            "risk_tier":       risk_tier,
            "factors":         factors,
            "suggestion":      suggestion,
            "input_snapshot":  input_snapshot,
            "result_snapshot": result_snapshot,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/ecg", methods=["POST"])
def predict_ecg():
    try:
        import cv2  # deferred — only loaded when ECG endpoint is hit

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files["file"]
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        if img is None:
            return jsonify({"error": "Could not read image"}), 400

        processed = preprocess_image(img)
        label, confidence = predict_cnn(processed)
        wave, peaks, hr, var = waveform_analysis(processed)

        result_line = f"ECG class: {label} (confidence {confidence * 100:.1f}%)"
        suggestion  = get_ai_suggestion(
            "ECG image", f"Class={label}, conf={confidence:.3f}", result_line
        )

        return jsonify({
            "label":          label,
            "confidence":     confidence,
            "wave":           wave,
            "peaks":          peaks,
            "hr":             hr,
            "var":            var,
            "suggestion":     suggestion,
            "result_snapshot": f"{result_line}; HR est. {hr} bpm; signal var. {var:.4f}",
            "input_snapshot":  "Image uploaded; CNN + waveform heuristics",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/report", methods=["POST"])
def get_report():
    try:
        data = request.json
        pdf_bytes = generate_report_pdf(
            title        = data.get("title", "Cardio Risk Report"),
            mode_label   = data.get("mode_label", ""),
            input_block  = data.get("input_snapshot", ""),
            result_block = data.get("result_snapshot", ""),
            ai_text      = data.get("suggestion", ""),
            contact_info = data.get("contact_info", ""),
        )
        return send_file(
            BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="cardio_report.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=8501)
