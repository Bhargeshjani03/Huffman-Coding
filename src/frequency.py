
def count_byte_frequencies(payload):
    """
    Count occurrences of every byte value from 0 to 255.

    Returns:
        frequencies: list of 256 integer counts
    """

    frequencies = [0] * 256

    for byte_value in payload:
        frequencies[byte_value] += 1

    return frequencies


def print_frequency_summary(frequencies):
    """Print useful statistics about the byte distribution."""

    total_bytes = sum(frequencies)
    distinct_bytes = sum(
        1 for frequency in frequencies if frequency > 0
    )

    print(f"Total bytes: {total_bytes:,}")
    print(f"Distinct byte values: {distinct_bytes}/256")

    print("\nMost frequent byte values:")

    top_values = sorted(
        range(256),
        key=lambda value: frequencies[value],
        reverse=True,
    )[:10]

    for value in top_values:
        print(
            f"Byte {value:3d} "
            f"(0x{value:02X}): "
            f"{frequencies[value]:,} occurrences"
        )
