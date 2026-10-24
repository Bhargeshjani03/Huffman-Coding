from src.encoder import encode_payload


def test_encode_empty_payload():
    encoded = encode_payload(b"")

    assert encoded.encoded_bytes == b""
    assert encoded.valid_bit_count == 0
    assert encoded.original_size == 0
    assert encoded.codebook == {}


def test_encode_one_repeated_byte():
    encoded = encode_payload(b"aaaa")

    assert encoded.codebook == {97: "0"}
    assert encoded.encoded_bytes == b"\x00"
    assert encoded.valid_bit_count == 4
    assert encoded.original_size == 4
    