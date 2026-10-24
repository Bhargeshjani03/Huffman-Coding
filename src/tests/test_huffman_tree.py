import pytest

from src.huffman_tree import build_huffman_tree, generate_codebook


def test_empty_input():
    assert build_huffman_tree({}) is None
    assert generate_codebook(None) == {}


def test_single_symbol():
    root = build_huffman_tree({"A": 10})
    assert generate_codebook(root) == {"A": "0"}


def test_codebook_contains_all_symbols():
    frequencies = {"A": 5, "B": 2, "C": 1}

    root = build_huffman_tree(frequencies)
    codebook = generate_codebook(root)

    assert set(codebook.keys()) == set(frequencies.keys())


def test_prefix_free_property():
    frequencies = {"A": 5, "B": 2, "C": 1, "D": 4}

    root = build_huffman_tree(frequencies)
    codebook = generate_codebook(root)

    codes = list(codebook.values())

    for i, code in enumerate(codes):
        for j, other_code in enumerate(codes):
            if i != j:
                assert not other_code.startswith(code)


def test_weighted_path_length():
    frequencies = {"A": 5, "B": 2, "C": 1}

    root = build_huffman_tree(frequencies)
    codebook = generate_codebook(root)

    weighted_path_length = sum(
        frequencies[symbol] * len(code)
        for symbol, code in codebook.items()
    )

    assert weighted_path_length == 11


def test_non_positive_frequency():
    with pytest.raises(ValueError):
        build_huffman_tree({"A": 0})


def test_deterministic_output():
    frequencies = {
        "A": 5,
        "B": 5,
        "C": 5,
        "D": 5,
    }

    root1 = build_huffman_tree(frequencies)
    root2 = build_huffman_tree(frequencies)

    codebook1 = generate_codebook(root1)
    codebook2 = generate_codebook(root2)

    assert codebook1 == codebook2
