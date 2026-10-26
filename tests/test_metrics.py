
# tests/test_metrics.py

import pytest

from src.metrics import (
    calculate_metrics,
    bytes_to_kb,
    measure_execution
)


def test_compression_metrics():
    result = calculate_metrics(1000, 700)

    assert result["original_size"] == 1000
    assert result["compressed_size"] == 700
    assert result["compression_ratio"] == pytest.approx(1000 / 700)
    assert result["space_saved_percent"] == pytest.approx(30)


def test_negative_savings():
    result = calculate_metrics(1000, 1200)

    assert result["space_saved_percent"] == pytest.approx(-20)


def test_bytes_to_kb():
    assert bytes_to_kb(2048) == 2.0


def test_execution_time():
    result, seconds = measure_execution(sum, [1, 2, 3])

    assert result == 6
    assert seconds >= 0


def test_invalid_original_size():
    with pytest.raises(ValueError):
        calculate_metrics(0, 700)


def test_invalid_compressed_size():
    with pytest.raises(ValueError):
        calculate_metrics(1000, 0)
