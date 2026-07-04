"""Sample data generation for demo/testing."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


def create_sample_text(path: str | Path) -> None:
    content = """Laporan uji program Kriptografi Hibrida + Steganografi
Nama : Raihan Azhari Lubis
NIM  : 231111619

Pesan ini digunakan sebagai contoh plaintext. Program akan mengenkripsi file ini
menggunakan AES-256-GCM, melindungi kunci AES menggunakan RSA-OAEP-SHA256,
menandatangani paket menggunakan DSA-SHA256, menghitung SHA-256 untuk integritas,
menurunkan seed posisi LSB dengan Diffie-Hellman + HKDF-SHA256, lalu menyisipkan
paket terenkripsi ke dalam citra PNG menggunakan modifikasi LSB dua bit secara acak.

Jika dekripsi berhasil dan hash SHA-256 cocok, berarti kerahasiaan, autentikasi,
integritas, pertukaran kunci, dan steganografi berjalan sesuai rancangan.
"""
    Path(path).write_text(content, encoding="utf-8")


def create_sample_cover(path: str | Path, width: int = 1200, height: int = 800) -> None:
    img = Image.new("RGB", (width, height), (238, 242, 247))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = 210 + (y * 20 // max(1, height - 1))
        g = 225 + (y * 15 // max(1, height - 1))
        b = 245
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=(230, 235, 242))
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(230, 235, 242))
    draw.rectangle([(60, 60), (width - 60, height - 60)], outline=(40, 70, 120), width=4)
    draw.text((90, 90), "Cover Image - Modified LSB", fill=(30, 60, 100))
    draw.text((90, 120), "Raihan Azhari Lubis / 231111619", fill=(30, 60, 100))
    img.save(path, format="PNG")
