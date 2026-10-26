
# web/app.py

import json
import sys
import subprocess
from pathlib import Path

from flask import Flask, render_template, jsonify


ROOT = Path(__file__).resolve().parents[1]

RESULTS_FILE = ROOT / "checkpoints" / "compression_results.json"

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/results", methods=["GET"])
def get_results():

    if not RESULTS_FILE.exists():
        return jsonify({
            "success": False,
            "error": "Results not found. Run MNIST integration first."
        }), 404

    try:
        results = json.loads(
            RESULTS_FILE.read_text(encoding="utf-8")
        )

        return jsonify({
            "success": True,
            **results
        })

    except (OSError, ValueError) as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/api/run", methods=["POST"])
def run_compression():

    try:
        process = subprocess.run(
            [sys.executable, "-m", "scripts.integrate_mnist"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )

        if process.returncode != 0:
            return jsonify({
                "success": False,
                "error": process.stderr[-2000:] or "Integration failed."
            }), 500

        results = json.loads(
            RESULTS_FILE.read_text(encoding="utf-8")
        )

        return jsonify({
            "success": True,
            **results
        })

    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
