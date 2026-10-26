
import pytest

from src.encoder import encode_payload
from src.container_format import build_container
from src.decoder import read_bits, decode_payload, decode_container


def test_read_bits():
    packed = bytes([0b10110000])
    bits = list(read_bits(packed, 5))

    assert bits == [1, 0, 1, 1, 0]


def test_empty_bits():
    assert list(read_bits(b"", 0)) == []


def test_invalid_bit_count():
    with pytest.raises(ValueError):
        list(read_bits(b"\x00", 9))


def test_decode_normal_payload():
    original = b"ABACA"
    encoded = encode_payload(original)

    decoded = decode_payload(
        encoded.encoded_bytes,
        encoded.valid_bit_count,
        encoded.codebook,
        encoded.original_size
    )

    assert decoded == original


def test_decode_empty_payload():
    encoded = encode_payload(b"")

    decoded = decode_payload(
        encoded.encoded_bytes,
        encoded.valid_bit_count,
        encoded.codebook,
        encoded.original_size
    )

    assert decoded == b""


def test_decode_single_symbol():
    original = b"AAAAAA"
    encoded = encode_payload(original)

    decoded = decode_payload(
        encoded.encoded_bytes,
        encoded.valid_bit_count,
        encoded.codebook,
        encoded.original_size
    )

    assert decoded == original


def test_full_container_roundtrip():
    original = b"Hello Huffman Coding!"

    container = build_container(original)
    decoded, manifest = decode_container(container)

    assert decoded == original
    assert manifest == []


def test_invalid_container_header():
    with pytest.raises(ValueError):
        decode_container(b"BAD")


def test_invalid_magic_identifier():
    container = bytearray(build_container(b"ABC"))
    container[0:4] = b"XXXX"

    with pytest.raises(ValueError):
        decode_container(bytes(container))


def test_truncated_container():
    container = build_container(b"ABCABC")

    with pytest.raises(ValueError):
        decode_container(container[:-1])


def test_checksum_verification():
    container = bytearray(build_container(b"ABACA"))
    container[-1] ^= 0b10000000

    with pytest.raises(ValueError):
        decode_container(bytes(container))
