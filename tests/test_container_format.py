import hashlib
import json
import struct

from src.container_format import build_container


HEADER = struct.Struct(">4sBI")


def test_container_header_and_metadata():
    payload = b"abracadabra"
    manifest = [
        {"name": "layer.weight", "shape": [2, 2], "dtype": "float32"}
    ]

    container = build_container(payload, manifest)

    magic, version, metadata_length = HEADER.unpack_from(container)
    metadata_start = HEADER.size
    metadata_end = metadata_start + metadata_length
    metadata = json.loads(container[metadata_start:metadata_end].decode("utf-8"))
    encoded_bytes = container[metadata_end:]

    assert magic == b"HUFC"
    assert version == 1
    assert metadata["original_size"] == len(payload)
    assert metadata["tensor_manifest"] == manifest
    assert metadata["encoded_size"] == len(encoded_bytes)
    assert len(encoded_bytes) == (metadata["valid_bit_count"] + 7) // 8
    assert metadata["checksum_sha256"] == hashlib.sha256(payload).hexdigest()


def test_empty_payload_has_no_encoded_bytes():
    container = build_container(b"")

    _, _, metadata_length = HEADER.unpack_from(container)
    metadata_start = HEADER.size
    metadata_end = metadata_start + metadata_length
    metadata = json.loads(container[metadata_start:metadata_end].decode("utf-8"))

    assert metadata["original_size"] == 0
    assert metadata["valid_bit_count"] == 0
    assert metadata["encoded_size"] == 0
    assert metadata["codebook"] == []
    assert container[metadata_end:] == b""