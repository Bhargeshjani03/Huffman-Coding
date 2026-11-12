
import json
import sys
import subprocess
import struct

from collections import Counter
from pathlib import Path

from flask import Flask, render_template, jsonify

ROOT = Path(__file__).resolve().parents[1]

RESULTS_FILE = ROOT / "checkpoints" / "compression_results.json"
COMPRESSED_FILE = ROOT / "checkpoints" / "mnist_model.huf"

# HUFC v1 binary header:
# 4 bytes magic + 1 byte version + 4 bytes metadata length
HEADER = struct.Struct(">4sBI")

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------
# 1. COMPRESSION RESULTS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# 2. HUFFMAN ANALYSIS + CONTAINER COMPOSITION
# ---------------------------------------------------------

@app.route("/api/analysis", methods=["GET"])
def get_huffman_analysis():

    if not COMPRESSED_FILE.exists():
        return jsonify({
            "success": False,
            "error": "Compressed file not found. Run compression first."
        }), 404

    try:

        from src.decoder import decode_container

        from src.huffman_tree import (
            build_huffman_tree,
            generate_codebook
        )

        # Read the complete HUFC container.
        container = COMPRESSED_FILE.read_bytes()

        total_container_size = len(container)

        # -------------------------------------------------
        # Extract HUFC header and metadata
        # -------------------------------------------------

        if len(container) < HEADER.size:
            raise ValueError("Invalid HUFC container: header is incomplete.")

        magic, version, metadata_length = HEADER.unpack_from(container)

        if magic != b"HUFC":
            raise ValueError("Invalid HUFC container: incorrect magic identifier.")

        if version != 1:
            raise ValueError(f"Unsupported HUFC version: {version}")

        metadata_start = HEADER.size
        metadata_end = metadata_start + metadata_length

        if metadata_end > total_container_size:
            raise ValueError("Invalid HUFC container: metadata exceeds file size.")

        metadata_bytes = container[metadata_start:metadata_end]

        metadata = json.loads(
            metadata_bytes.decode("utf-8")
        )

        # Actual encoded payload is everything after metadata.
        encoded_payload_size = len(container) - metadata_end

        # Metadata records the encoded payload size.
        declared_encoded_size = int(metadata["encoded_size"])

        if encoded_payload_size != declared_encoded_size:
            raise ValueError(
                "Container size mismatch: actual encoded payload size "
                "does not match metadata."
            )

        # -------------------------------------------------
        # Calculate exact container composition
        # -------------------------------------------------

        header_size = HEADER.size
        metadata_size = len(metadata_bytes)

        container_overhead = header_size + metadata_size

        calculated_total = (
            header_size
            + metadata_size
            + encoded_payload_size
        )

        if calculated_total != total_container_size:
            raise ValueError(
                "Container size verification failed."
            )

        payload_percentage = (
            encoded_payload_size / total_container_size * 100
            if total_container_size else 0
        )

        overhead_percentage = (
            container_overhead / total_container_size * 100
            if total_container_size else 0
        )

        # -------------------------------------------------
        # Decode container and analyse Huffman distribution
        # -------------------------------------------------

        decoded_payload, manifest = decode_container(container)

        frequency_map = Counter(decoded_payload)

        root = build_huffman_tree(frequency_map)

        codebook = generate_codebook(root)

        # -------------------------------------------------
        # Serialize Huffman tree
        # -------------------------------------------------

        def serialize_tree(node, depth=0):

            if node is None:
                return None

            return {
                "symbol": node.symbol,
                "frequency": node.frequency,
                "depth": depth,
                "left": serialize_tree(node.left, depth + 1),
                "right": serialize_tree(node.right, depth + 1)
            }

        # -------------------------------------------------
        # Frequency distribution
        # -------------------------------------------------

        frequency_distribution = []

        for symbol, frequency in frequency_map.most_common(20):

            frequency_distribution.append({
                "symbol": symbol,
                "hex": f"0x{symbol:02X}",
                "frequency": frequency,

                "percentage": (
                    frequency / len(decoded_payload) * 100
                    if decoded_payload else 0
                ),

                "code": codebook.get(symbol, ""),

                "code_length": len(codebook.get(symbol, ""))
            })

        # -------------------------------------------------
        # Codebook
        # -------------------------------------------------

        codebook_data = []

        for symbol, frequency in frequency_map.most_common(32):

            code = codebook.get(symbol, "")

            codebook_data.append({
                "symbol": symbol,
                "hex": f"0x{symbol:02X}",
                "frequency": frequency,
                "code": code,
                "code_length": len(code)
            })

        # -------------------------------------------------
        # Average code length and theoretical encoded bits
        # -------------------------------------------------

        total_bits = sum(
            frequency * len(codebook[symbol])
            for symbol, frequency in frequency_map.items()
        )

        average_code_length = (
            total_bits / len(decoded_payload)
            if decoded_payload else 0
        )

        # -------------------------------------------------
        # API RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            # Original payload analysis
            "total_bytes": len(decoded_payload),

            "distinct_symbols": len(frequency_map),

            "average_code_length": average_code_length,

            "theoretical_encoded_bits": total_bits,

            # Frequency and Huffman information
            "frequency_distribution": frequency_distribution,

            "codebook": codebook_data,

            "tree": serialize_tree(root),

            # Exact HUFC container composition
            "header_size": header_size,

            "metadata_size": metadata_size,

            "encoded_payload_size": encoded_payload_size,

            "container_overhead": container_overhead,

            "total_container_size": total_container_size,

            "payload_percentage": payload_percentage,

            "overhead_percentage": overhead_percentage

        })

    except Exception as error:

        app.logger.exception("Huffman analysis failed")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# 3. RUN COMPRESSION
# ---------------------------------------------------------

@app.route("/api/run", methods=["POST"])
def run_compression():

    try:

        process = subprocess.run(

            [
                sys.executable,
                "-m",
                "scripts.integrate_mnist"
            ],

            cwd=ROOT,

            capture_output=True,

            text=True,

            timeout=300
        )

        if process.returncode != 0:

            error_message = (
                process.stderr[-3000:]
                or process.stdout[-3000:]
                or "Compression integration failed."
            )

            return jsonify({
                "success": False,
                "error": error_message
            }), 500

        results = json.loads(
            RESULTS_FILE.read_text(encoding="utf-8")
        )

        return jsonify({
            "success": True,
            **results
        })

    except subprocess.TimeoutExpired:

        return jsonify({
            "success": False,
            "error": "Compression exceeded the 5-minute request limit."
        }), 504

    except (OSError, ValueError) as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------------------------------------------------
# 4. START FLASK
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
