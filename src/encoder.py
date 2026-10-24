from dataclasses import dataclass

from src.bitstream import pack_codes
from src.frequency import count_byte_frequencies
from src.huffman_tree import build_huffman_tree, generate_codebook


@dataclass(frozen=True)
class EncodedPayload:
    encoded_bytes: bytes
    valid_bit_count: int
    original_size: int
    codebook: dict


def encode_payload(payload):
    if not isinstance(payload, (bytes, bytearray, memoryview)):
        raise TypeError("payload must be bytes-like")

    data = bytes(payload)

    counts = count_byte_frequencies(data)
    frequencies = {
        symbol: count
        for symbol, count in enumerate(counts)
        if count > 0
    }

    root = build_huffman_tree(frequencies)
    codebook = generate_codebook(root)

    packed, bit_count = pack_codes(
        codebook[symbol] for symbol in data
    )

    return EncodedPayload(
        encoded_bytes=packed,
        valid_bit_count=bit_count,
        original_size=len(data),
        codebook=codebook,
    )