
from pathlib import Path

import torch


def extract_tensor_payload(checkpoint_path):
    """
    Load a model checkpoint and convert its parameters
    into one sequence of raw bytes.

    Returns:
        payload: bytes containing all parameter tensor data
        manifest: metadata needed to reconstruct each tensor
    """

    checkpoint_path = Path(checkpoint_path)

    # Load the saved model state dictionary.
    state_dict = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=True,
    )

    payload_parts = []
    manifest = []
    current_offset = 0

    for name, tensor in state_dict.items():

        # Move the tensor to CPU and make its memory contiguous.
        tensor = tensor.detach().cpu().contiguous()

        # Convert the tensor's exact storage representation to bytes.
        tensor_bytes = (
            tensor.reshape(-1)
            .view(torch.uint8)
            .numpy()
            .tobytes()
        )

        # Record information required for reconstruction.
        manifest.append({
            "name": name,
            "shape": list(tensor.shape),
            "dtype": str(tensor.dtype),
            "offset": current_offset,
            "length": len(tensor_bytes),
        })

        payload_parts.append(tensor_bytes)
        current_offset += len(tensor_bytes)

    payload = b"".join(payload_parts)

    return payload, manifest
