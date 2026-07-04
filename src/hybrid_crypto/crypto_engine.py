"""Hybrid cryptography engine: AES-GCM, RSA-OAEP, DSA, SHA-256, DH, and LSB stego."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .key_exchange import derive_dh_session_key
from .key_manager import load_private_key, load_public_key
from .stego_lsb import embed_payload, extract_payload, payload_capacity_bytes
from .utils import b64d, b64e, canonical_json, human_size, random_bytes, sha256_bytes, utc_now_iso


AAD = b"kripto-hibrida-steganografi-v1"


def _build_signing_material(payload_without_signature: Dict[str, Any]) -> bytes:
    return canonical_json(payload_without_signature)


def _rsa_encrypt_key(public_key, aes_key: bytes) -> bytes:
    return public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def _rsa_decrypt_key(private_key, encrypted_key: bytes) -> bytes:
    return private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def _dsa_sign(private_key, data: bytes) -> bytes:
    return private_key.sign(data, hashes.SHA256())


def _dsa_verify(public_key, signature: bytes, data: bytes) -> None:
    public_key.verify(signature, data, hashes.SHA256())


def _derive_stego_seed(sender_dh_private_path: str | Path | None = None,
                       receiver_dh_public_path: str | Path | None = None,
                       sender_dh_public_path: str | Path | None = None,
                       receiver_dh_private_path: str | Path | None = None,
                       salt: bytes = b"") -> bytes:
    """Derive the same stego seed from either sender or receiver side."""
    if sender_dh_private_path and receiver_dh_public_path:
        private_key = load_private_key(sender_dh_private_path)
        public_key = load_public_key(receiver_dh_public_path)
    elif receiver_dh_private_path and sender_dh_public_path:
        private_key = load_private_key(receiver_dh_private_path)
        public_key = load_public_key(sender_dh_public_path)
    else:
        raise ValueError("Pasangan kunci DH tidak lengkap.")
    return derive_dh_session_key(private_key, public_key, salt=salt)


def encrypt_file_to_stego(
    input_file: str | Path,
    cover_image: str | Path,
    output_stego: str | Path,
    recipient_rsa_public: str | Path,
    sender_dsa_private: str | Path,
    sender_dh_private: str | Path,
    recipient_dh_public: str | Path,
) -> Dict[str, Any]:
    """Encryption with a stable DH-derived stego seed.

    A fixed info/salt is used for stego position derivation so the receiver can locate
    the hidden package before reading metadata. The package still stores a separate
    random audit salt to prove per-run freshness in the cryptographic metadata.
    """
    input_path = Path(input_file)
    plaintext = input_path.read_bytes()
    plaintext_sha256 = sha256_bytes(plaintext)

    aes_key = random_bytes(32)
    nonce = random_bytes(12)
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, AAD)

    rsa_public = load_public_key(recipient_rsa_public)
    encrypted_key = _rsa_encrypt_key(rsa_public, aes_key)

    # Stable DH seed for randomized LSB ordering. Both parties can derive it.
    fixed_stego_salt = b"RaihanAzhariLubis-231111619-LSB"
    stego_seed = _derive_stego_seed(
        sender_dh_private_path=sender_dh_private,
        receiver_dh_public_path=recipient_dh_public,
        salt=fixed_stego_salt,
    )

    audit_salt = random_bytes(16)
    payload_without_signature = {
        "version": "1.0",
        "created_at_utc": utc_now_iso(),
        "student": {"nama": "Raihan Azhari Lubis", "nim": "231111619"},
        "original_filename": input_path.name,
        "algorithm": {
            "symmetric": "AES-256-GCM",
            "key_protection": "RSA-OAEP-SHA256",
            "signature": "DSA-SHA256",
            "hash": "SHA-256",
            "key_exchange": "Diffie-Hellman + HKDF-SHA256",
            "steganography": "Modified randomized LSB, 2 bits per RGB carrier byte",
        },
        "aad_b64": b64e(AAD),
        "nonce_b64": b64e(nonce),
        "dh_audit_salt_b64": b64e(audit_salt),
        "encrypted_aes_key_b64": b64e(encrypted_key),
        "ciphertext_b64": b64e(ciphertext),
        "original_sha256": plaintext_sha256,
        "plaintext_size_bytes": len(plaintext),
    }

    sender_private = load_private_key(sender_dsa_private)
    signing_material = _build_signing_material(payload_without_signature)
    signature = _dsa_sign(sender_private, signing_material)

    package = dict(payload_without_signature)
    package["signature_b64"] = b64e(signature)
    package["signing_material_sha256"] = sha256_bytes(signing_material)

    payload_json = json.dumps(package, sort_keys=True, indent=2).encode("utf-8")
    stego_stats = embed_payload(cover_image, output_stego, payload_json, stego_seed)

    return {
        "input_file": str(input_path),
        "output_stego": str(output_stego),
        "plaintext_sha256": plaintext_sha256,
        "plaintext_size": human_size(len(plaintext)),
        "payload_json_size": human_size(len(payload_json)),
        "stego_stats": stego_stats,
        "dh_seed_sha256": sha256_bytes(stego_seed),
        "signature_valid_at_creation": True,
    }


def extract_and_decrypt_stego(
    stego_image: str | Path,
    output_file: str | Path,
    recipient_rsa_private: str | Path,
    sender_dsa_public: str | Path,
    sender_dh_public: str | Path,
    recipient_dh_private: str | Path,
) -> Dict[str, Any]:
    fixed_stego_salt = b"RaihanAzhariLubis-231111619-LSB"
    stego_seed = _derive_stego_seed(
        receiver_dh_private_path=recipient_dh_private,
        sender_dh_public_path=sender_dh_public,
        salt=fixed_stego_salt,
    )

    payload_json = extract_payload(stego_image, stego_seed)
    package = json.loads(payload_json.decode("utf-8"))
    signature = b64d(package.pop("signature_b64"))
    expected_signing_material_hash = package.pop("signing_material_sha256")
    signing_material = _build_signing_material(package)

    if sha256_bytes(signing_material) != expected_signing_material_hash:
        raise ValueError("Hash signing material tidak sesuai; payload kemungkinan berubah.")

    sender_public = load_public_key(sender_dsa_public)
    try:
        _dsa_verify(sender_public, signature, signing_material)
        signature_status = "valid"
    except InvalidSignature as exc:
        raise ValueError("Tanda tangan DSA tidak valid.") from exc

    rsa_private = load_private_key(recipient_rsa_private)
    aes_key = _rsa_decrypt_key(rsa_private, b64d(package["encrypted_aes_key_b64"]))

    aesgcm = AESGCM(aes_key)
    plaintext = aesgcm.decrypt(b64d(package["nonce_b64"]), b64d(package["ciphertext_b64"]), b64d(package["aad_b64"]))

    recovered_sha256 = sha256_bytes(plaintext)
    if recovered_sha256 != package["original_sha256"]:
        raise ValueError("SHA-256 file hasil dekripsi tidak cocok dengan metadata asli.")

    Path(output_file).write_bytes(plaintext)
    return {
        "stego_image": str(stego_image),
        "output_file": str(output_file),
        "signature_status": signature_status,
        "original_filename": package["original_filename"],
        "plaintext_size": human_size(len(plaintext)),
        "recovered_sha256": recovered_sha256,
        "dh_seed_sha256": sha256_bytes(stego_seed),
        "algorithm": package["algorithm"],
    }
