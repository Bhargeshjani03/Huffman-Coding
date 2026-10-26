
from pathlib import Path

from src.tensor_payload import extract_tensor_payload
from src.frequency import (
    count_byte_frequencies,
    print_frequency_summary,
)

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "checkpoints" / "mnist_model.pth"

payload, manifest = extract_tensor_payload(CHECKPOINT)
frequencies = count_byte_frequencies(payload)

print("=== Tensor Payload Analysis ===")
print(f"Expected raw bytes: {109386 * 4:,}")
print(f"Extracted raw bytes: {len(payload):,}")
print(f"Number of tensors: {len(manifest)}")
print(f"Number of frequency counters: {len(frequencies)}")

assert len(payload) == 109386 * 4, (
    "Extracted payload size does not match "
    "the expected float32 parameter size."
)

assert len(frequencies) == 256
assert sum(frequencies) == len(payload)

print("\nAll validation checks passed.")

print_frequency_summary(frequencies)
