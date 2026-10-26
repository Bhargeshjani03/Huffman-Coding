
# src/metrics.py

import time


def calculate_metrics(original_size, compressed_size):
    """
    Calculate compression ratio and space savings.
    """

    if original_size <= 0:
        raise ValueError("Original size must be greater than zero")

    if compressed_size <= 0:
        raise ValueError("Compressed size must be greater than zero")

    compression_ratio = original_size / compressed_size

    space_saved = (
        (original_size - compressed_size) / original_size
    ) * 100

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "space_saved_percent": space_saved
    }


def bytes_to_kb(size):
    """
    Convert bytes into KiB (1024 bytes).
    """
    return size / 1024


def measure_execution(function, *args, **kwargs):
    """
    Measure how long a function takes to execute.
    """

    start_time = time.perf_counter()

    result = function(*args, **kwargs)

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    return result, execution_time
