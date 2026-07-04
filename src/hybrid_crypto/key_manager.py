"""Key generation and PEM loading for RSA, DSA, and Diffie-Hellman."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dsa, rsa, dh

from .utils import ensure_dir

# RFC 3526, 2048-bit MODP Group (Group 14). Using a standard group avoids slow
# parameter generation while still producing fresh DH private/public key pairs.
RFC3526_GROUP14_P_HEX = """
FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E08
8A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD
3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E
7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899F
A5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF05
98DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C
62F356208552BB9ED529077096966D670C354E4ABC9804F1746C
08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2E
C07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956
AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
"""


def get_dh_parameters(key_size: int = 2048):
    if key_size == 2048:
        p = int("".join(RFC3526_GROUP14_P_HEX.split()), 16)
        return dh.DHParameterNumbers(p, 2).parameters()
    return dh.generate_parameters(generator=2, key_size=key_size)


def save_private_key(path: str | Path, private_key) -> None:
    data = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    Path(path).write_bytes(data)


def save_public_key(path: str | Path, public_key) -> None:
    data = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    Path(path).write_bytes(data)


def load_private_key(path: str | Path):
    return serialization.load_pem_private_key(Path(path).read_bytes(), password=None)


def load_public_key(path: str | Path):
    return serialization.load_pem_public_key(Path(path).read_bytes())


def save_dh_parameters(path: str | Path, parameters) -> None:
    Path(path).write_bytes(
        parameters.parameter_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.ParameterFormat.PKCS3,
        )
    )


def load_dh_parameters(path: str | Path):
    return serialization.load_pem_parameters(Path(path).read_bytes())


def generate_rsa_key_pair(key_size: int = 2048) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    return private_key, private_key.public_key()


def generate_dsa_key_pair(key_size: int = 2048) -> Tuple[dsa.DSAPrivateKey, dsa.DSAPublicKey]:
    private_key = dsa.generate_private_key(key_size=key_size)
    return private_key, private_key.public_key()


def generate_key_bundle(output_dir: str | Path, key_size: int = 2048) -> dict:
    """Generate all keys required by the project.

    Sender owns DSA and DH private keys. Receiver owns RSA and DH private keys.
    """
    out = ensure_dir(output_dir)

    receiver_rsa_priv, receiver_rsa_pub = generate_rsa_key_pair(key_size)
    sender_dsa_priv, sender_dsa_pub = generate_dsa_key_pair(key_size)

    parameters = get_dh_parameters(key_size)
    sender_dh_priv = parameters.generate_private_key()
    receiver_dh_priv = parameters.generate_private_key()

    paths = {
        "receiver_rsa_private": out / "receiver_rsa_private.pem",
        "receiver_rsa_public": out / "receiver_rsa_public.pem",
        "sender_dsa_private": out / "sender_dsa_private.pem",
        "sender_dsa_public": out / "sender_dsa_public.pem",
        "dh_parameters": out / "dh_parameters.pem",
        "sender_dh_private": out / "sender_dh_private.pem",
        "sender_dh_public": out / "sender_dh_public.pem",
        "receiver_dh_private": out / "receiver_dh_private.pem",
        "receiver_dh_public": out / "receiver_dh_public.pem",
    }

    save_private_key(paths["receiver_rsa_private"], receiver_rsa_priv)
    save_public_key(paths["receiver_rsa_public"], receiver_rsa_pub)
    save_private_key(paths["sender_dsa_private"], sender_dsa_priv)
    save_public_key(paths["sender_dsa_public"], sender_dsa_pub)
    save_dh_parameters(paths["dh_parameters"], parameters)
    save_private_key(paths["sender_dh_private"], sender_dh_priv)
    save_public_key(paths["sender_dh_public"], sender_dh_priv.public_key())
    save_private_key(paths["receiver_dh_private"], receiver_dh_priv)
    save_public_key(paths["receiver_dh_public"], receiver_dh_priv.public_key())

    return {k: str(v) for k, v in paths.items()}
