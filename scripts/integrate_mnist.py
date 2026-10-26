
# scripts/integrate_mnist.py

import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.model import MNISTModel
from src.tensor_payload import extract_tensor_payload
from src.container_format import build_container
from src.decoder import decode_container

from src.verification import (
    reconstruct_tensors,
    verify_payload,
    verify_parameters,
    load_reconstructed_model,
    compare_models,
)

from src.metrics import (
    calculate_metrics,
    measure_execution,
    bytes_to_kb,
)


# STEP 1: Define project paths

ROOT = Path(__file__).resolve().parents[1]

CHECKPOINT = ROOT / "checkpoints" / "mnist_model.pth"
COMPRESSED_FILE = ROOT / "checkpoints" / "mnist_model.huf"
RESULTS_FILE = ROOT / "checkpoints" / "compression_results.json"
DATA_DIR = ROOT / "data"


def main():

    print("\n=== MNIST HUFFMAN COMPRESSION ===")

    # STEP 2: Check model checkpoint

    if not CHECKPOINT.exists():
        raise FileNotFoundError(
            "MNIST checkpoint not found. "
            "Run the training script first."
        )

    # STEP 3: Load original model

    original_state = torch.load(
        CHECKPOINT,
        map_location="cpu",
        weights_only=True,
    )

    original_model = MNISTModel()
    original_model.load_state_dict(original_state)
    original_model.eval()

    # STEP 4: Extract exact parameter bytes

    original_payload, manifest = extract_tensor_payload(
        CHECKPOINT
    )

    print(f"Original parameter bytes: {len(original_payload):,}")
    print(f"Number of tensors: {len(manifest)}")

    # STEP 5: Compress model bytes

    container, encoding_time = measure_execution(
        build_container,
        original_payload,
        manifest,
    )

    COMPRESSED_FILE.write_bytes(container)

    print(f"Compressed file saved: {COMPRESSED_FILE.name}")

    # STEP 6: Decompress the saved file

    saved_container = COMPRESSED_FILE.read_bytes()

    decoded_result, decoding_time = measure_execution(
        decode_container,
        saved_container,
    )

    decoded_payload, decoded_manifest = decoded_result

    # STEP 7: Verify byte equality

    bytes_identical = verify_payload(
        original_payload,
        decoded_payload,
    )

    print(f"Bytes identical: {bytes_identical}")

    # STEP 8: Reconstruct parameter tensors

    decoded_state = reconstruct_tensors(
        decoded_payload,
        decoded_manifest,
    )

    weights_identical = verify_parameters(
        original_state,
        decoded_state,
    )

    print(f"Weights identical: {weights_identical}")

    if not bytes_identical or not weights_identical:
        raise RuntimeError("Lossless verification failed")

    # STEP 9: Calculate compression metrics

    metrics = calculate_metrics(
        len(original_payload),
        len(saved_container),
    )

    print("\n=== COMPRESSION METRICS ===")

    print(
        f"Original size: "
        f"{bytes_to_kb(metrics['original_size']):.2f} KiB"
    )

    print(
        f"Compressed size: "
        f"{bytes_to_kb(metrics['compressed_size']):.2f} KiB"
    )

    print(
        f"Compression ratio: "
        f"{metrics['compression_ratio']:.4f}x"
    )

    print(
        f"Space saved: "
        f"{metrics['space_saved_percent']:.2f}%"
    )

    print(f"Encoding time: {encoding_time:.4f} seconds")
    print(f"Decoding time: {decoding_time:.4f} seconds")

    # STEP 10: Load MNIST test dataset

    test_dataset = datasets.MNIST(
        root=DATA_DIR,
        train=False,
        download=True,
        transform=transforms.ToTensor(),
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=256,
        shuffle=False,
        num_workers=0,
    )

    # STEP 11: Build restored model

    restored_model = load_reconstructed_model(
        decoded_payload,
        decoded_manifest,
    )

    # STEP 12: Compare model accuracy and predictions

    accuracy_results = compare_models(
        original_model,
        restored_model,
        test_loader,
    )

    print("\n=== MODEL ACCURACY ===")

    print(
        f"Accuracy before: "
        f"{accuracy_results['accuracy_before'] * 100:.2f}%"
    )

    print(
        f"Accuracy after: "
        f"{accuracy_results['accuracy_after'] * 100:.2f}%"
    )

    print(
        "Predictions identical: "
        f"{accuracy_results['predictions_identical']}"
    )

    if not accuracy_results["predictions_identical"]:
        raise RuntimeError("Model predictions do not match")

    # STEP 13: Save results for the frontend

    results = {
        **metrics,
        "encoding_seconds": encoding_time,
        "decoding_seconds": decoding_time,
        "tensor_count": len(manifest),
        "bytes_identical": bytes_identical,
        "weights_identical": weights_identical,
        "accuracy_before": (
            accuracy_results["accuracy_before"] * 100
        ),
        "accuracy_after": (
            accuracy_results["accuracy_after"] * 100
        ),
        "predictions_identical": (
            accuracy_results["predictions_identical"]
        ),
        "compressed_file": str(COMPRESSED_FILE.name),
    }

    RESULTS_FILE.write_text(
        json.dumps(results, indent=4),
        encoding="utf-8",
    )

    print("\n=== INTEGRATION COMPLETE ===")
    print(f"Results saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
