from src.node import HuffmanNode
from src.min_heap import MinHeap


def build_huffman_tree(frequencies):
    """
    Build a Huffman tree from a symbol-frequency dictionary.

    Args:
        frequencies: Dictionary mapping symbols to frequencies.

    Returns:
        The root of the Huffman tree, or None for empty input.
    """
    if not frequencies:
        return None

    heap = MinHeap()

    # Insert symbols in deterministic order.
    for symbol, frequency in sorted(frequencies.items()):
        if frequency <= 0:
            raise ValueError("Frequencies must be positive")

        heap.insert(
            HuffmanNode(symbol=symbol, frequency=frequency)
        )

    # A single symbol does not require any merging.
    if len(heap) == 1:
        return heap.extract_min()

    while len(heap) > 1:
        left = heap.extract_min()
        right = heap.extract_min()

        parent = HuffmanNode(
            symbol=None,
            frequency=left.frequency + right.frequency,
            left=left,
            right=right,
        )

        heap.insert(parent)

    return heap.extract_min()


def generate_codebook(root):
    """
    Generate symbol-to-binary-code mappings by traversing the tree.

    Returns:
        A dictionary mapping each symbol to its Huffman code.
    """
    if root is None:
        return {}

    codebook = {}

    def traverse(node, code):
        if node.left is None and node.right is None:
            # Give a single-symbol tree the code "0".
            codebook[node.symbol] = code or "0"
            return

        if node.left is not None:
            traverse(node.left, code + "0")

        if node.right is not None:
            traverse(node.right, code + "1")

    traverse(root, "")
    return codebook
