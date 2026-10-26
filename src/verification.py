
# src/verification.py

from collections import OrderedDict
from math import prod

import torch

from src.model import MNISTModel


# Map saved dtype names to PyTorch types
DTYPE_MAP = {
    "torch.float32": torch.float32,
    "torch.float64": torch.float64,
    "torch.float16": torch.float16,
    "torch.int64": torch.int64,
    "torch.int32": torch.int32,
    "torch.int16": torch.int16,
    "torch.int8": torch.int8,
    "torch.uint8": torch.uint8,
    "torch.bool": torch.bool,
}


def reconstruct_tensors(payload, manifest):
    """
    Reconstruct PyTorch tensors from the
    original bytes recovered by the decoder.
    """

    state_dict = OrderedDict()
    expected_offset = 0

    for item in manifest:
        name = item["name"]
        shape = item["shape"]
        dtype_name = item["dtype"]
        offset = item["offset"]
        length = item["length"]

        if name in state_dict:
            raise ValueError("Duplicate tensor name")

        if dtype_name not in DTYPE_MAP:
            raise ValueError("Unsupported tensor dtype")

        if offset != expected_offset:
            raise ValueError("Incorrect tensor offset")

        if not isinstance(shape, list):
            raise ValueError("Invalid tensor shape")

        if any(type(dim) is not int or dim < 0 for dim in shape):
            raise ValueError("Invalid tensor dimensions")

        dtype = DTYPE_MAP[dtype_name]

        expected_length = (
            prod(shape) *
            torch.empty((), dtype=dtype).element_size()
        )

        if length != expected_length:
            raise ValueError("Incorrect tensor byte length")

        tensor_bytes = bytearray(
            payload[offset:offset + length]
        )

        if len(tensor_bytes) != length:
            raise ValueError("Incomplete tensor data")

        tensor = torch.frombuffer(
            tensor_bytes,
            dtype=dtype
        ).clone()

        tensor = tensor.reshape(shape)

        state_dict[name] = tensor

        expected_offset += length

    if expected_offset != len(payload):
        raise ValueError("Tensor manifest does not cover payload")

    return state_dict


def verify_payload(original_payload, decoded_payload):
    """
    Check exact byte-for-byte equality.
    """

    return original_payload == decoded_payload


def tensor_to_bytes(tensor):
    """
    Convert a tensor into its exact raw bytes.
    """

    return (
        tensor.detach()
        .cpu()
        .contiguous()
        .reshape(-1)
        .view(torch.uint8)
        .numpy()
        .tobytes()
    )


def verify_parameters(original_state, decoded_state):
    """
    Compare original and reconstructed model parameters.
    """

    if original_state.keys() != decoded_state.keys():
        return False

    for name in original_state:
        original = original_state[name]
        decoded = decoded_state[name]

        if original.shape != decoded.shape:
            return False

        if original.dtype != decoded.dtype:
            return False

        if tensor_to_bytes(original) != tensor_to_bytes(decoded):
            return False

    return True


def load_reconstructed_model(payload, manifest):
    """
    Create a new MNIST model and load recovered weights.
    """

    state_dict = reconstruct_tensors(payload, manifest)

    model = MNISTModel()

    model.load_state_dict(state_dict, strict=True)

    model.eval()

    return model


def evaluate_model(model, data_loader):
    """
    Calculate model accuracy and save predictions.
    """

    model.eval()

    correct = 0
    total = 0
    predictions_list = []

    with torch.no_grad():
        for images, labels in data_loader:

            outputs = model(images)

            predictions = outputs.argmax(dim=1)

            correct += (
                predictions == labels
            ).sum().item()

            total += labels.size(0)

            predictions_list.extend(
                predictions.tolist()
            )

    accuracy = correct / total if total else 0.0

    return accuracy, predictions_list


def compare_models(original_model, restored_model, data_loader):
    """
    Compare accuracy and predictions before and after decompression.
    """

    accuracy_before, predictions_before = evaluate_model(
        original_model, data_loader
    )

    accuracy_after, predictions_after = evaluate_model(
        restored_model, data_loader
    )

    return {
        "accuracy_before": accuracy_before,
        "accuracy_after": accuracy_after,
        "predictions_identical": (
            predictions_before == predictions_after
        ),
        "accuracy_identical": (
            accuracy_before == accuracy_after
        )
    }
