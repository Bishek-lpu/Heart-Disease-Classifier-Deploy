"""
One-time model conversion: heart_ecg_cnn.h5 → heart_ecg_cnn.onnx

Uses the SavedModel intermediate format to work around a tf2onnx 1.17 / Keras 3.x
compatibility bug ('KeyError: keras_tensor_90') with from_keras().

Requirements (local only, NOT in production):
    pip install tf2onnx tensorflow onnx

Run:
    python convert_to_onnx.py

After conversion, commit heart_ecg_cnn.onnx to the repo.
The .h5 file is no longer needed in the Docker image.
"""

import os
import sys
import shutil
import subprocess

# Suppress TF noise
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

try:
    import tensorflow as tf
except ImportError:
    print("ERROR: TensorFlow not found. Run: pip install tensorflow tf2onnx onnx")
    sys.exit(1)

H5_PATH = "heart_ecg_cnn.h5"
SAVED_MODEL_DIR = "heart_ecg_cnn_savedmodel"
ONNX_PATH = "heart_ecg_cnn.onnx"

if not os.path.exists(H5_PATH):
    print(f"ERROR: {H5_PATH} not found. Make sure you are in the project root.")
    sys.exit(1)

# ── Step 1: Load the .h5 model ────────────────────────────────────────────────
print(f"Loading Keras model from {H5_PATH} ...")
model = tf.keras.models.load_model(H5_PATH)
model.summary()

# ── Step 2: Export to SavedModel format ──────────────────────────────────────
print(f"\nExporting to SavedModel → {SAVED_MODEL_DIR}/ ...")
if os.path.exists(SAVED_MODEL_DIR):
    shutil.rmtree(SAVED_MODEL_DIR)
model.export(SAVED_MODEL_DIR)   # Keras 3.x API (tf.saved_model compatible)
print("SavedModel export done.")

# ── Step 3: Convert SavedModel → ONNX via tf2onnx CLI ────────────────────────
print(f"\nConverting SavedModel → ONNX ({ONNX_PATH}) ...")
result = subprocess.run(
    [
        sys.executable, "-m", "tf2onnx.convert",
        "--saved-model", SAVED_MODEL_DIR,
        "--output",      ONNX_PATH,
        "--opset",       "13",
        "--verbose",
    ],
    capture_output=False,   # let output stream to terminal
)

if result.returncode != 0:
    print("\n❌ tf2onnx conversion failed. See output above.")
    sys.exit(result.returncode)

# ── Step 4: Cleanup temp SavedModel dir ──────────────────────────────────────
shutil.rmtree(SAVED_MODEL_DIR, ignore_errors=True)
print(f"Cleaned up {SAVED_MODEL_DIR}/")

# ── Report ────────────────────────────────────────────────────────────────────
size_mb = os.path.getsize(ONNX_PATH) / (1024 * 1024)
h5_mb   = os.path.getsize(H5_PATH)   / (1024 * 1024)
print(f"\n✅ Conversion complete!")
print(f"   Output  : {ONNX_PATH}  ({size_mb:.1f} MB)")
print(f"   h5 size : {h5_mb:.1f} MB  →  saved {h5_mb - size_mb:.1f} MB")
print(f"\nNext steps:")
print(f"  1. git add heart_ecg_cnn.onnx")
print(f"  2. git commit -m 'Add ONNX model (replaces TF h5)'")
print(f"  3. git push")
