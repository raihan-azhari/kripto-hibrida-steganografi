# Program Kriptografi Hibrida + Steganografi

**Nama:** Raihan Azhari Lubis  
**NIM:** 231111619

Program ini menggabungkan AES-256-GCM, RSA-OAEP-SHA256, DSA-SHA256, SHA-256, Diffie-Hellman + HKDF-SHA256, dan steganografi modified randomized LSB.

## Struktur fitur

1. AES-256-GCM untuk enkripsi file plaintext.
2. RSA-OAEP-SHA256 untuk pengamanan kunci AES.
3. DSA-SHA256 untuk tanda tangan digital paket terenkripsi.
4. SHA-256 untuk hash file dan hash material tanda tangan.
5. Diffie-Hellman + HKDF-SHA256 untuk menurunkan seed posisi LSB.
6. Modified LSB menggunakan dua bit terakhir pada byte RGB dan urutan posisi pseudo-random.

## Instalasi

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
```

## Demo otomatis

```bash
python main.py demo --out demo_run
```

Perintah ini akan membuat kunci, membuat file plaintext contoh, membuat cover image, melakukan enkripsi + penyisipan stego, mengekstrak, mendekripsi, lalu membandingkan SHA-256 plaintext dengan hasil dekripsi.

## Perintah manual

Generate keys:

```bash
python main.py gen-keys --out keys
```

Encrypt and embed:

```bash
python main.py encrypt \
  --input samples/pesan_raihan.txt \
  --cover samples/cover.png \
  --output output/stego_raihan.png \
  --recipient-rsa-public keys/receiver_rsa_public.pem \
  --sender-dsa-private keys/sender_dsa_private.pem \
  --sender-dh-private keys/sender_dh_private.pem \
  --recipient-dh-public keys/receiver_dh_public.pem
```

Extract and decrypt:

```bash
python main.py decrypt \
  --stego output/stego_raihan.png \
  --output output/recovered_pesan_raihan.txt \
  --recipient-rsa-private keys/receiver_rsa_private.pem \
  --sender-dsa-public keys/sender_dsa_public.pem \
  --sender-dh-public keys/sender_dh_public.pem \
  --recipient-dh-private keys/receiver_dh_private.pem
```

Check Diffie-Hellman:

```bash
python main.py dh-demo \
  --sender-dh-private keys/sender_dh_private.pem \
  --sender-dh-public keys/sender_dh_public.pem \
  --receiver-dh-private keys/receiver_dh_private.pem \
  --receiver-dh-public keys/receiver_dh_public.pem
```

## Upload ke GitHub

```bash
git init
git add .
git commit -m "Program kriptografi hibrida dan steganografi"
git branch -M main
git remote add origin https://github.com/USERNAME/NAMA_REPOSITORY.git
git push -u origin main
```
