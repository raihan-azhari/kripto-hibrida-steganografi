"""Diffie-Hellman key agreement helpers."""
from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_dh_session_key(private_key, peer_public_key, salt: bytes, info: bytes = b"hybrid-crypto-stego-seed") -> bytes:
    """Derive 32 bytes from a DH shared secret with HKDF-SHA256."""
    shared_secret = private_key.exchange(peer_public_key)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
    ).derive(shared_secret)
