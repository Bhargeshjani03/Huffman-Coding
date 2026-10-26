
import torch

from src.verification import (
    reconstruct_tensors,
    verify_payload,
    verify_parameters,
    tensor_to_bytes,
)


def test_payload_equality():
    assert verify_payload(b"ABC", b"ABC")
    assert not verify_payload(b"ABC", b"ABD")


def test_tensor_reconstruction():
    original = torch.tensor(
        [[1.5, 2.5], [3.5, 4.5]],
        dtype=torch.float32
    )

    payload = tensor_to_bytes(original)

    manifest = [
        {
            "name": "layer.weight",
            "shape": [2, 2],
            "dtype": "torch.float32",
            "offset": 0,
            "length": len(payload),
        }
    ]

    restored = reconstruct_tensors(payload, manifest)

    assert torch.equal(
        original,
        restored["layer.weight"]
    )


def test_parameter_verification():
    original = {
        "layer.weight": torch.tensor(
            [1.0, 2.0, 3.0]
        )
    }

    restored = {
        "layer.weight": torch.tensor(
            [1.0, 2.0, 3.0]
        )
    }

    assert verify_parameters(original, restored)
