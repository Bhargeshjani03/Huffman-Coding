def pack_codes(codes):
    output = bytearray()
    current_byte = 0
    bits_in_byte = 0
    valid_bit_count = 0

    for code in codes:
        for bit in code:
            if bit not in "01":
                raise ValueError("Codes can contain only 0 and 1")

            current_byte = (current_byte << 1) | int(bit)
            bits_in_byte += 1
            valid_bit_count += 1

            if bits_in_byte == 8:
                output.append(current_byte)
                current_byte = 0
                bits_in_byte = 0

    if bits_in_byte:
        output.append(current_byte << (8 - bits_in_byte))

    return bytes(output), valid_bit_count