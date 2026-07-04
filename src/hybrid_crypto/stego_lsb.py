"""Modified randomized LSB steganography.

The modification used here is not sequential one-bit embedding. It uses:
1. pseudo-random carrier byte positions derived from SHA-256/HKDF seed;
2. two least significant bits per RGB carrier byte;
3. a framed payload with magic bytes and a 32-bit payload length.
"""
from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path

from PIL import Image

MAGIC = b"KHB1"  # Kripto Hibrida, version 1
BITS_PER_CARRIER = 2


class StegoError(Exception):
    pass


def _normalize_seed(seed: bytes | str) -> bytes:
    if isinstance(seed, str):
        seed = seed.encode("utf-8")
    return hashlib.sha256(seed).digest()


def _position_stream(capacity: int, seed: bytes) -> list[int]:
    rng = random.Random(int.from_bytes(_normalize_seed(seed), "big"))
    positions = list(range(capacity))
    rng.shuffle(positions)
    return positions


def _bytes_to_chunks(data: bytes) -> list[int]:
    chunks: list[int] = []
    for byte in data:
        for shift in (6, 4, 2, 0):
            chunks.append((byte >> shift) & 0b11)
    return chunks


def _chunks_to_bytes(chunks: list[int]) -> bytes:
    out = bytearray()
    if len(chunks) % 4 != 0:
        raise StegoError("Jumlah potongan bit tidak kelipatan 4.")
    for i in range(0, len(chunks), 4):
        value = 0
        for chunk in chunks[i : i + 4]:
            value = (value << 2) | (chunk & 0b11)
        out.append(value)
    return bytes(out)


def payload_capacity_bytes(image_path: str | Path) -> int:
    image = Image.open(image_path).convert("RGB")
    carrier_count = len(image.tobytes())
    return (carrier_count * BITS_PER_CARRIER) // 8 - 8


def embed_payload(cover_path: str | Path, output_path: str | Path, payload: bytes, seed: bytes | str) -> dict:
    image = Image.open(cover_path).convert("RGB")
    raw = bytearray(image.tobytes())

    framed = MAGIC + len(payload).to_bytes(4, "big") + payload
    chunks = _bytes_to_chunks(framed)

    if len(chunks) > len(raw):
        capacity = (len(raw) * BITS_PER_CARRIER) // 8 - 8
        raise StegoError(
            f"Payload terlalu besar. Kapasitas bersih {capacity} byte, payload {len(payload)} byte."
        )

    positions = _position_stream(len(raw), _normalize_seed(seed))
    for chunk, pos in zip(chunks, positions):
        raw[pos] = (raw[pos] & 0b11111100) | chunk

    stego_image = Image.frombytes("RGB", image.size, bytes(raw))
    stego_image.save(output_path, format="PNG")
    return {
        "cover_size": image.size,
        "carrier_bytes": len(raw),
        "payload_bytes": len(payload),
        "framed_bytes": len(framed),
        "used_carriers": len(chunks),
        "capacity_payload_bytes": (len(raw) * BITS_PER_CARRIER) // 8 - 8,
    }


def extract_payload(stego_path: str | Path, seed: bytes | str) -> bytes:
    image = Image.open(stego_path).convert("RGB")
    raw = bytearray(image.tobytes())
    positions = _position_stream(len(raw), _normalize_seed(seed))

    header_carriers = 8 * 4  # 8 bytes framed header, 4 chunks per byte
    header_chunks = [(raw[pos] & 0b11) for pos in positions[:header_carriers]]
    header = _chunks_to_bytes(header_chunks)

    if len(header) != 8 or header[:4] != MAGIC:
        raise StegoError(
            "Header steganografi tidak valid. Kunci DH/seed salah atau gambar bukan hasil program ini."
        )

    payload_len = int.from_bytes(header[4:8], "big")
    total_bytes = 8 + payload_len
    total_carriers = total_bytes * 4
    if total_carriers > len(raw):
        raise StegoError("Ukuran payload pada header melebihi kapasitas gambar.")

    chunks = [(raw[pos] & 0b11) for pos in positions[:total_carriers]]
    framed = _chunks_to_bytes(chunks)
    if framed[:4] != MAGIC:
        raise StegoError("Magic bytes rusak setelah ekstraksi.")
    return framed[8:]
