
import hashlib
import json

from src.container_format import HEADER, MAGIC, VERSION


def read_bits(packed_bytes, valid_bit_count):
    if not isinstance(valid_bit_count, int) or isinstance(valid_bit_count, bool):
        raise ValueError("Invalid bit count")

    if not 0 <= valid_bit_count <= len(packed_bytes) * 8:
        raise ValueError("Bit count out of range")

    bits_read = 0

    for byte in packed_bytes:
        for i in range(8):
            if bits_read == valid_bit_count:
                return

            bit = (byte >> (7 - i)) & 1
            yield bit
            bits_read += 1


def build_decoding_tree(codebook):
    root = {}

    for symbol, code in codebook.items():
        if type(symbol) is not int or not 0 <= symbol <= 255:
            raise ValueError("Invalid byte symbol")

        if not isinstance(code, str) or not code:
            raise ValueError("Invalid Huffman code")

        if any(bit not in "01" for bit in code):
            raise ValueError("Huffman code must contain only 0 or 1")

        current = root

        for bit in code:
            if "symbol" in current:
                raise ValueError("Prefix conflict in codebook")

            current = current.setdefault(bit, {})

        if current:
            raise ValueError("Duplicate or overlapping Huffman code")

        current["symbol"] = symbol

    return root


def decode_payload(packed_bytes, valid_bit_count, codebook, original_size):
    if type(original_size) is not int or original_size < 0:
        raise ValueError("Invalid original size")

    if not isinstance(packed_bytes, (bytes, bytearray, memoryview)):
        raise TypeError("Encoded payload must be bytes")

    if not isinstance(codebook, dict):
        raise ValueError("Invalid codebook")

    packed_bytes = bytes(packed_bytes)

    if not 0 <= valid_bit_count <= len(packed_bytes) * 8:
        raise ValueError("Invalid valid-bit count")

    if original_size == 0:
        if valid_bit_count != 0 or packed_bytes or codebook:
            raise ValueError("Invalid empty payload")
        return b""

    if not codebook:
        raise ValueError("Missing Huffman codebook")

    tree = build_decoding_tree(codebook)

    result = bytearray()
    current = tree

    for bit in read_bits(packed_bytes, valid_bit_count):
        direction = str(bit)

        if direction not in current:
            raise ValueError("Invalid encoded bitstream")

        current = current[direction]

        if "symbol" in current:
            result.append(current["symbol"])

            if len(result) > original_size:
                raise ValueError("Decoded payload exceeds original size")

            current = tree

    if current is not tree:
        raise ValueError("Incomplete Huffman code")

    if len(result) != original_size:
        raise ValueError("Decoded payload size mismatch")

    return bytes(result)


def decode_container(container):
    if not isinstance(container, (bytes, bytearray, memoryview)):
        raise TypeError("Container must be bytes")

    container = bytes(container)

    if len(container) < HEADER.size:
        raise ValueError("Container header is incomplete")

    magic, version, metadata_length = HEADER.unpack_from(container)

    if magic != MAGIC:
        raise ValueError("Invalid HUFC identifier")

    if version != VERSION:
        raise ValueError("Unsupported container version")

    metadata_start = HEADER.size
    metadata_end = metadata_start + metadata_length

    if metadata_end > len(container):
        raise ValueError("Container metadata is incomplete")

    try:
        metadata = json.loads(
            container[metadata_start:metadata_end].decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid container metadata") from exc

    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be an object")

    required = [
        "original_size",
        "valid_bit_count",
        "encoded_size",
        "codebook",
        "tensor_manifest",
        "checksum_sha256"
    ]

    for key in required:
        if key not in metadata:
            raise ValueError(f"Missing metadata: {key}")

    encoded_bytes = container[metadata_end:]

    encoded_size = metadata["encoded_size"]
    valid_bit_count = metadata["valid_bit_count"]

    if type(encoded_size) is not int or encoded_size < 0:
        raise ValueError("Invalid encoded size")

    if type(valid_bit_count) is not int or valid_bit_count < 0:
        raise ValueError("Invalid valid-bit count")

    if encoded_size != len(encoded_bytes):
        raise ValueError("Encoded byte count mismatch")

    if encoded_size != (valid_bit_count + 7) // 8:
        raise ValueError("Invalid bitstream length")

    if not isinstance(metadata["codebook"], list):
        raise ValueError("Invalid codebook format")

    codebook = {}

    for item in metadata["codebook"]:
        if not isinstance(item, dict):
            raise ValueError("Invalid codebook entry")

        if "symbol" not in item or "code" not in item:
            raise ValueError("Missing codebook entry field")

        symbol = item["symbol"]
        code = item["code"]

        if type(symbol) is not int or not isinstance(code, str):
            raise ValueError("Invalid codebook entry types")

        if symbol in codebook:
            raise ValueError("Duplicate Huffman symbol")

        codebook[symbol] = code

    payload = decode_payload(
        encoded_bytes,
        valid_bit_count,
        codebook,
        metadata["original_size"]
    )

    checksum = hashlib.sha256(payload).hexdigest()

    if checksum != metadata["checksum_sha256"]:
        raise ValueError("SHA-256 checksum mismatch")

    manifest = metadata["tensor_manifest"]

    if not isinstance(manifest, list):
        raise ValueError("Invalid tensor manifest")

    return payload, manifest
