import hashlib
import json
import struct
from pathlib import Path

from src.encoder import encode_payload


MAGIC = b"HUFC"
VERSION = 1
HEADER = struct.Struct(">4sBI")


def build_container(payload, manifest=None):
    if not isinstance(payload, (bytes, bytearray, memoryview)):
        raise TypeError("payload must be bytes-like")

    payload = bytes(payload)
    encoded = encode_payload(payload)

    if manifest is None:
        manifest = []

    metadata = {
        "original_size": encoded.original_size,
        "valid_bit_count": encoded.valid_bit_count,
        "encoded_size": len(encoded.encoded_bytes),
        "codebook": [
            {"symbol": symbol, "code": encoded.codebook[symbol]}
            for symbol in sorted(encoded.codebook)
        ],
        "tensor_manifest": manifest,
        "checksum_sha256": hashlib.sha256(payload).hexdigest(),
    }

    metadata_bytes = json.dumps(
        metadata,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    header = HEADER.pack(MAGIC, VERSION, len(metadata_bytes))
    return header + metadata_bytes + encoded.encoded_bytes


def write_container(path, payload, manifest=None):
    output_path = Path(path)
    output_path.write_bytes(build_container(payload, manifest))
    return output_path