from src.bitstream import pack_codes


def test_pack_codes_pads_final_byte():
    packed, bit_count = pack_codes(["10", "11", "0"])

    assert packed == bytes([0b10110000])
    assert bit_count == 5


def test_pack_codes_handles_empty_input():
    assert pack_codes([]) == (b"", 0)