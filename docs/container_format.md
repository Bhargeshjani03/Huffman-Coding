# Huffman Container Format — Version 1

## Purpose

This file format stores a Huffman-compressed byte payload with enough metadata for a decoder to interpret the encoded bytes and reconstruct the original payload.

## Binary layout

The container is written in this order:

| Field | Size | Description |
|---|---:|---|
| Magic identifier | 4 bytes | ASCII `HUFC` |
| Format version | 1 byte | Version number `1` |
| Metadata length | 4 bytes | Unsigned big-endian length of the JSON metadata |
| Metadata | Variable | UTF-8 encoded JSON |
| Encoded data | Variable | Huffman bits packed into bytes |

The fixed header is 9 bytes. The encoded data starts immediately after the metadata.

## Metadata fields

The JSON metadata contains:

- `original_size`: number of bytes in the original payload.
- `valid_bit_count`: number of meaningful Huffman bits. Padding bits are not included.
- `encoded_size`: number of bytes in the packed encoded data.
- `codebook`: list of objects containing a byte `symbol` and its binary `code`.
- `tensor_manifest`: tensor information supplied by the caller, such as each tensor’s name, shape, data type, offset, and byte length.
- `checksum_sha256`: SHA-256 checksum of the original payload.

The codebook is stored as a list so each symbol and its code are explicit in the JSON.

## Bit packing

Huffman code bits are packed most-significant bit first. If the last byte is not full, unused low-order bits are padded with zeroes. `valid_bit_count` tells the decoder how many bits to read and ignore the padding.

For a payload containing one repeated byte, the code is `0`; `original_size` records how many times that byte occurred. An empty payload has an empty codebook, zero valid bits, and no encoded data bytes.

## Size calculation

The complete container size includes the fixed header, JSON metadata, and encoded data:

`container size = 9 + metadata length + encoded_size`

Compression results must use the complete container size, including its metadata.