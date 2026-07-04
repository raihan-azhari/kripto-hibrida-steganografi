#!/usr/bin/env python3
"""CLI Program Kriptografi Hibrida + Steganografi.

Nama: Raihan Azhari Lubis
NIM : 231111619
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hybrid_crypto.crypto_engine import encrypt_file_to_stego, extract_and_decrypt_stego
from hybrid_crypto.demo_data import create_sample_cover, create_sample_text
from hybrid_crypto.key_exchange import derive_dh_session_key
from hybrid_crypto.key_manager import generate_key_bundle, load_private_key, load_public_key
from hybrid_crypto.stego_lsb import payload_capacity_bytes
from hybrid_crypto.utils import ensure_dir, sha256_bytes, sha256_file


def print_json(title: str, data: dict) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2, sort_keys=True))


def cmd_gen_keys(args: argparse.Namespace) -> None:
    paths = generate_key_bundle(args.out, key_size=args.key_size)
    print_json("Kunci berhasil dibuat", paths)


def cmd_encrypt(args: argparse.Namespace) -> None:
    ensure_dir(Path(args.output).parent)
    result = encrypt_file_to_stego(
        input_file=args.input,
        cover_image=args.cover,
        output_stego=args.output,
        recipient_rsa_public=args.recipient_rsa_public,
        sender_dsa_private=args.sender_dsa_private,
        sender_dh_private=args.sender_dh_private,
        recipient_dh_public=args.recipient_dh_public,
    )
    print_json("Enkripsi + steganografi selesai", result)


def cmd_decrypt(args: argparse.Namespace) -> None:
    ensure_dir(Path(args.output).parent)
    result = extract_and_decrypt_stego(
        stego_image=args.stego,
        output_file=args.output,
        recipient_rsa_private=args.recipient_rsa_private,
        sender_dsa_public=args.sender_dsa_public,
        sender_dh_public=args.sender_dh_public,
        recipient_dh_private=args.recipient_dh_private,
    )
    print_json("Ekstraksi + dekripsi selesai", result)


def cmd_dh_demo(args: argparse.Namespace) -> None:
    sender_priv = load_private_key(args.sender_dh_private)
    sender_pub = load_public_key(args.sender_dh_public)
    receiver_priv = load_private_key(args.receiver_dh_private)
    receiver_pub = load_public_key(args.receiver_dh_public)
    salt = b"RaihanAzhariLubis-231111619-LSB"
    sender_secret = derive_dh_session_key(sender_priv, receiver_pub, salt=salt)
    receiver_secret = derive_dh_session_key(receiver_priv, sender_pub, salt=salt)
    result = {
        "sender_secret_sha256": sha256_bytes(sender_secret),
        "receiver_secret_sha256": sha256_bytes(receiver_secret),
        "match": sender_secret == receiver_secret,
        "function": "Diffie-Hellman exchange + HKDF-SHA256",
    }
    print_json("Demo Diffie-Hellman", result)


def cmd_capacity(args: argparse.Namespace) -> None:
    print_json("Kapasitas LSB", {"image": args.image, "capacity_payload_bytes": payload_capacity_bytes(args.image)})


def cmd_demo(args: argparse.Namespace) -> None:
    base = Path(args.out)
    keys = base / "keys"
    samples = base / "samples"
    output = base / "output"
    ensure_dir(keys)
    ensure_dir(samples)
    ensure_dir(output)

    sample_text = samples / "pesan_raihan.txt"
    cover = samples / "cover.png"
    stego = output / "stego_raihan.png"
    recovered = output / "recovered_pesan_raihan.txt"

    create_sample_text(sample_text)
    create_sample_cover(cover)
    paths = generate_key_bundle(keys, key_size=args.key_size)
    print_json("1. Kunci dibuat", paths)
    print_json("2. File contoh", {
        "plaintext": str(sample_text),
        "plaintext_sha256": sha256_file(sample_text),
        "cover": str(cover),
        "cover_capacity_payload_bytes": payload_capacity_bytes(cover),
    })

    dh_args = argparse.Namespace(
        sender_dh_private=paths["sender_dh_private"],
        sender_dh_public=paths["sender_dh_public"],
        receiver_dh_private=paths["receiver_dh_private"],
        receiver_dh_public=paths["receiver_dh_public"],
    )
    cmd_dh_demo(dh_args)

    enc_result = encrypt_file_to_stego(
        input_file=sample_text,
        cover_image=cover,
        output_stego=stego,
        recipient_rsa_public=paths["receiver_rsa_public"],
        sender_dsa_private=paths["sender_dsa_private"],
        sender_dh_private=paths["sender_dh_private"],
        recipient_dh_public=paths["receiver_dh_public"],
    )
    print_json("3. Enkripsi + steganografi", enc_result)

    dec_result = extract_and_decrypt_stego(
        stego_image=stego,
        output_file=recovered,
        recipient_rsa_private=paths["receiver_rsa_private"],
        sender_dsa_public=paths["sender_dsa_public"],
        sender_dh_public=paths["sender_dh_public"],
        recipient_dh_private=paths["receiver_dh_private"],
    )
    print_json("4. Ekstraksi + dekripsi", dec_result)

    print_json("5. Verifikasi akhir", {
        "plaintext_sha256": sha256_file(sample_text),
        "recovered_sha256": sha256_file(recovered),
        "same_content": sample_text.read_bytes() == recovered.read_bytes(),
        "stego_file": str(stego),
        "recovered_file": str(recovered),
    })


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Program Kriptografi Hibrida + Steganografi Modified LSB")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("gen-keys", help="Generate RSA, DSA, and Diffie-Hellman keys")
    g.add_argument("--out", default="keys", help="Folder output kunci")
    g.add_argument("--key-size", type=int, default=2048, help="Ukuran kunci RSA/DSA/DH")
    g.set_defaults(func=cmd_gen_keys)

    e = sub.add_parser("encrypt", help="Encrypt file and embed package into a PNG image")
    e.add_argument("--input", required=True, help="File plaintext")
    e.add_argument("--cover", required=True, help="Cover image PNG/JPG")
    e.add_argument("--output", required=True, help="Output stego PNG")
    e.add_argument("--recipient-rsa-public", required=True)
    e.add_argument("--sender-dsa-private", required=True)
    e.add_argument("--sender-dh-private", required=True)
    e.add_argument("--recipient-dh-public", required=True)
    e.set_defaults(func=cmd_encrypt)

    d = sub.add_parser("decrypt", help="Extract package from stego PNG and decrypt file")
    d.add_argument("--stego", required=True, help="Stego image PNG")
    d.add_argument("--output", required=True, help="File output hasil dekripsi")
    d.add_argument("--recipient-rsa-private", required=True)
    d.add_argument("--sender-dsa-public", required=True)
    d.add_argument("--sender-dh-public", required=True)
    d.add_argument("--recipient-dh-private", required=True)
    d.set_defaults(func=cmd_decrypt)

    dh = sub.add_parser("dh-demo", help="Verify Diffie-Hellman shared secret equality")
    dh.add_argument("--sender-dh-private", required=True)
    dh.add_argument("--sender-dh-public", required=True)
    dh.add_argument("--receiver-dh-private", required=True)
    dh.add_argument("--receiver-dh-public", required=True)
    dh.set_defaults(func=cmd_dh_demo)

    c = sub.add_parser("capacity", help="Show modified LSB payload capacity of image")
    c.add_argument("--image", required=True)
    c.set_defaults(func=cmd_capacity)

    demo = sub.add_parser("demo", help="Run a complete automatic demonstration")
    demo.add_argument("--out", default="demo_run", help="Folder output demo")
    demo.add_argument("--key-size", type=int, default=2048)
    demo.set_defaults(func=cmd_demo)
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
