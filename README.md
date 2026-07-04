# 🔐 Program Kriptografi Hibrida + Steganografi

**Nama:** Raihan Azhari Lubis  
**NIM:** 231111619  
**Repository:** https://github.com/raihan-azhari/kripto-hibrida-steganografi

---

## 📌 Deskripsi Program

Program ini merupakan implementasi sistem pengamanan data berbasis **kriptografi hibrida** yang dikombinasikan dengan **steganografi citra**. Sistem dirancang untuk mengamankan isi file plaintext melalui proses enkripsi, tanda tangan digital, hashing, pertukaran kunci, serta penyembunyian data terenkripsi ke dalam gambar menggunakan metode **modified randomized LSB**.

Secara umum, program ini bekerja dengan cara mengenkripsi pesan menggunakan **AES-256-GCM**, mengamankan kunci AES menggunakan **RSA-OAEP-SHA256**, menandatangani paket terenkripsi menggunakan **DSA-SHA256**, menghitung integritas data menggunakan **SHA-256**, menurunkan seed posisi penyisipan menggunakan **Diffie-Hellman + HKDF-SHA256**, lalu menyisipkan paket terenkripsi ke dalam gambar menggunakan teknik **modified LSB**.

Tujuan utama dari program ini adalah menghasilkan sistem pengamanan data yang memiliki unsur:

- Kerahasiaan data melalui enkripsi AES.
- Pengamanan kunci menggunakan algoritma asimetris RSA.
- Autentikasi dan integritas melalui tanda tangan digital DSA.
- Verifikasi hash menggunakan SHA-256.
- Pertukaran kunci menggunakan Diffie-Hellman.
- Penyembunyian data terenkripsi pada citra menggunakan steganografi LSB.

---

## 🧩 Algoritma yang Digunakan

| Komponen | Algoritma | Fungsi |
|---|---|---|
| Enkripsi simetris | AES-256-GCM | Mengenkripsi isi file plaintext |
| Enkripsi kunci | RSA-OAEP-SHA256 | Mengamankan kunci AES |
| Tanda tangan digital | DSA-SHA256 | Menandatangani paket terenkripsi |
| Hashing | SHA-256 | Mengecek integritas plaintext dan material tanda tangan |
| Pertukaran kunci | Diffie-Hellman + HKDF-SHA256 | Menghasilkan seed posisi LSB |
| Steganografi | Modified Randomized LSB | Menyembunyikan payload terenkripsi ke dalam gambar |

---

## ⚙️ Alur Kerja Sistem

### 1. Proses Enkripsi dan Penyisipan

Pada proses enkripsi, program membaca file plaintext yang ingin diamankan. Setelah itu, program membangkitkan kunci AES 256-bit secara acak untuk mengenkripsi isi file menggunakan mode AES-GCM.

Kunci AES tidak disimpan secara langsung, melainkan dienkripsi menggunakan public key RSA penerima dengan padding OAEP berbasis SHA-256. Dengan demikian, hanya penerima yang memiliki private key RSA yang dapat membuka kembali kunci AES tersebut.

Setelah paket terenkripsi dibuat, program menghitung hash SHA-256 dan membuat tanda tangan digital menggunakan private key DSA pengirim. Selanjutnya, Diffie-Hellman digunakan untuk menghasilkan shared secret antara pengirim dan penerima. Shared secret tersebut diproses dengan HKDF-SHA256 untuk menghasilkan seed posisi steganografi.

Payload terenkripsi kemudian disisipkan ke dalam gambar cover menggunakan metode modified randomized LSB. Penyisipan dilakukan pada dua bit terakhir byte RGB dengan urutan posisi pseudo-random.

### 2. Proses Ekstraksi dan Dekripsi

Pada proses dekripsi, program membaca gambar stego dan mengekstrak payload tersembunyi dari posisi LSB yang sama. Posisi tersebut dapat diperoleh kembali menggunakan seed hasil Diffie-Hellman dan HKDF-SHA256.

Setelah payload berhasil diekstrak, program melakukan verifikasi tanda tangan digital menggunakan public key DSA pengirim. Jika tanda tangan valid, program melanjutkan proses dekripsi kunci AES menggunakan private key RSA penerima.

Kunci AES yang berhasil dibuka digunakan untuk mendekripsi ciphertext. Hasil dekripsi kemudian dibandingkan dengan hash SHA-256 plaintext untuk memastikan data yang diterima sama dengan data asli.

---

## 📁 Struktur Folder Project

```text
kripto_hibrida_raihan/
│
├── main.py
├── requirements.txt
├── README.md
├── GITHUB_UPLOAD_GUIDE.md
├── .gitignore
│
├── src/
│   └── hybrid_crypto/
│       ├── __init__.py
│       ├── crypto_engine.py
│       ├── demo_data.py
│       ├── key_exchange.py
│       ├── key_manager.py
│       ├── stego_lsb.py
│       └── utils.py
│
├── samples/
│   ├── pesan_raihan.txt
│   └── cover.png
│
└── docs/
    ├── architecture_flow.png
    ├── lsb_diagram.png
    ├── cover_vs_stego.png
    ├── demo_execution_log.txt
    ├── recovered_pesan_raihan_demo.txt
    ├── console_log_part_1.png
    ├── console_log_part_2.png
    └── console_log_part_3.png
```

---

## 🛠️ Instalasi

Pastikan Python sudah terpasang pada komputer. Program ini disarankan dijalankan menggunakan Python versi 3.10 atau lebih baru.

### 1. Clone repository

```bash
git clone https://github.com/raihan-azhari/kripto-hibrida-steganografi.git
cd kripto-hibrida-steganografi
```

### 2. Buat virtual environment

```bash
python -m venv .venv
```

### 3. Aktifkan virtual environment

Untuk Windows:

```bash
.venv\Scripts\activate
```

Untuk Linux atau Mac:

```bash
source .venv/bin/activate
```

### 4. Install dependency

```bash
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Demo Otomatis

Program menyediakan mode demo otomatis agar seluruh proses dapat dijalankan dengan satu perintah.

```bash
python main.py demo --out demo_run
```

Perintah tersebut akan menjalankan proses berikut:

1. Membuat pasangan kunci RSA, DSA, dan Diffie-Hellman.
2. Membuat file plaintext contoh.
3. Membuat cover image.
4. Mengenkripsi plaintext menggunakan AES-256-GCM.
5. Mengenkripsi kunci AES menggunakan RSA-OAEP-SHA256.
6. Membuat tanda tangan digital menggunakan DSA-SHA256.
7. Menghasilkan seed posisi LSB menggunakan Diffie-Hellman + HKDF-SHA256.
8. Menyisipkan payload terenkripsi ke dalam gambar.
9. Mengekstrak payload dari gambar stego.
10. Memverifikasi tanda tangan digital.
11. Mendekripsi ciphertext.
12. Membandingkan SHA-256 plaintext asli dan hasil dekripsi.

Jika proses berhasil, hasil akhir akan menunjukkan bahwa tanda tangan valid dan isi file hasil dekripsi sama dengan file asli.

---

## 🔑 Generate Key Manual

Untuk membuat seluruh key secara manual, jalankan perintah berikut:

```bash
python main.py gen-keys --out keys
```

Perintah tersebut akan menghasilkan beberapa file kunci, antara lain:

```text
keys/
├── receiver_rsa_private.pem
├── receiver_rsa_public.pem
├── sender_dsa_private.pem
├── sender_dsa_public.pem
├── sender_dh_private.pem
├── sender_dh_public.pem
├── receiver_dh_private.pem
└── receiver_dh_public.pem
```

---

## 🔒 Enkripsi dan Penyisipan ke Gambar

Gunakan perintah berikut untuk mengenkripsi file plaintext dan menyisipkan hasilnya ke dalam gambar cover.

Untuk Windows CMD, gunakan perintah satu baris berikut:

```cmd
python main.py encrypt --input samples/pesan_raihan.txt --cover samples/cover.png --output output/stego_raihan.png --recipient-rsa-public keys/receiver_rsa_public.pem --sender-dsa-private keys/sender_dsa_private.pem --sender-dh-private keys/sender_dh_private.pem --recipient-dh-public keys/receiver_dh_public.pem
```

Untuk Linux, Mac, atau Git Bash, dapat menggunakan format multi-line berikut:

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

Hasil dari proses ini adalah gambar stego yang berisi payload terenkripsi:

```text
output/stego_raihan.png
```

---

## 🔓 Ekstraksi dan Dekripsi

Gunakan perintah berikut untuk mengekstrak payload dari gambar stego dan mendekripsi kembali isi file.

Untuk Windows CMD, gunakan perintah satu baris berikut:

```cmd
python main.py decrypt --stego output/stego_raihan.png --output output/recovered_pesan_raihan.txt --recipient-rsa-private keys/receiver_rsa_private.pem --sender-dsa-public keys/sender_dsa_public.pem --sender-dh-public keys/sender_dh_public.pem --recipient-dh-private keys/receiver_dh_private.pem
```

Untuk Linux, Mac, atau Git Bash, dapat menggunakan format multi-line berikut:

```bash
python main.py decrypt \
  --stego output/stego_raihan.png \
  --output output/recovered_pesan_raihan.txt \
  --recipient-rsa-private keys/receiver_rsa_private.pem \
  --sender-dsa-public keys/sender_dsa_public.pem \
  --sender-dh-public keys/sender_dh_public.pem \
  --recipient-dh-private keys/receiver_dh_private.pem
```

Jika proses berhasil, file hasil dekripsi akan tersimpan pada:

```text
output/recovered_pesan_raihan.txt
```

---

## 🔁 Pengujian Diffie-Hellman

Untuk memeriksa apakah pertukaran kunci Diffie-Hellman menghasilkan shared secret yang sama pada sisi pengirim dan penerima, jalankan perintah berikut.

Untuk Windows CMD:

```cmd
python main.py dh-demo --sender-dh-private keys/sender_dh_private.pem --sender-dh-public keys/sender_dh_public.pem --receiver-dh-private keys/receiver_dh_private.pem --receiver-dh-public keys/receiver_dh_public.pem
```

Untuk Linux, Mac, atau Git Bash:

```bash
python main.py dh-demo \
  --sender-dh-private keys/sender_dh_private.pem \
  --sender-dh-public keys/sender_dh_public.pem \
  --receiver-dh-private keys/receiver_dh_private.pem \
  --receiver-dh-public keys/receiver_dh_public.pem
```

Pengujian ini digunakan untuk memastikan bahwa shared secret yang diperoleh kedua pihak sama dan dapat digunakan sebagai dasar penurunan seed posisi LSB.

---

## 🧪 Contoh Output Demo

Contoh hasil eksekusi demo:

```text
signature_status: valid
same_content: true
plaintext_sha256: valid
recovered_sha256: valid
```

Keterangan:

- `signature_status: valid` berarti tanda tangan digital berhasil diverifikasi.
- `same_content: true` berarti hasil dekripsi sama dengan plaintext asli.
- `plaintext_sha256` dan `recovered_sha256` digunakan untuk membandingkan integritas data.
- Jika hash sama, maka tidak ada perubahan data selama proses enkripsi, penyisipan, ekstraksi, dan dekripsi.

---

## 🖼️ Konsep Modified Randomized LSB

Metode LSB digunakan untuk menyembunyikan data pada bit-bit terakhir dari pixel gambar. Pada program ini, penyisipan tidak dilakukan secara berurutan biasa, melainkan menggunakan urutan posisi pseudo-random.

Seed posisi pseudo-random diperoleh dari hasil pertukaran kunci Diffie-Hellman yang diproses menggunakan HKDF-SHA256. Dengan pendekatan ini, proses penyisipan menjadi lebih sulit ditebak karena posisi bit yang digunakan tidak linear.

Karakteristik metode yang digunakan:

- Menggunakan channel RGB pada gambar.
- Menyisipkan data pada dua bit terakhir setiap byte RGB.
- Menggunakan frame magic untuk mengenali awal payload.
- Menggunakan panjang payload agar proses ekstraksi dapat dilakukan secara tepat.
- Menggunakan posisi pseudo-random agar pola penyisipan tidak mudah dianalisis.

---

## ✅ Fitur Utama

- Enkripsi file plaintext menggunakan AES-256-GCM.
- Pengamanan kunci AES menggunakan RSA-OAEP-SHA256.
- Tanda tangan digital menggunakan DSA-SHA256.
- Hash integritas menggunakan SHA-256.
- Pertukaran kunci menggunakan Diffie-Hellman.
- Penurunan seed menggunakan HKDF-SHA256.
- Steganografi modified randomized LSB.
- Mode demo otomatis.
- Mode generate key.
- Mode encrypt dan decrypt manual.
- Bukti eksekusi tersedia pada folder `docs`.

---

## 📄 File Penting

| File | Keterangan |
|---|---|
| `main.py` | File utama untuk menjalankan perintah CLI |
| `crypto_engine.py` | Modul proses enkripsi, dekripsi, hashing, dan tanda tangan |
| `key_manager.py` | Modul pembuatan dan penyimpanan key |
| `key_exchange.py` | Modul Diffie-Hellman dan HKDF |
| `stego_lsb.py` | Modul penyisipan dan ekstraksi LSB |
| `demo_data.py` | Modul pembuatan data demo |
| `utils.py` | Fungsi pendukung |
| `samples/pesan_raihan.txt` | Contoh plaintext |
| `samples/cover.png` | Contoh gambar cover |
| `docs/demo_execution_log.txt` | Log hasil eksekusi demo |

---

## 🧾 Cara Upload ke GitHub

Jika repository sudah dibuat di GitHub, upload project menggunakan CMD dengan perintah berikut:

```cmd
git init
git add .
git commit -m "Program kriptografi hibrida dan steganografi"
git branch -M main
git remote add origin https://github.com/raihan-azhari/kripto-hibrida-steganografi.git
git push -u origin main
```

Jika remote sudah pernah ditambahkan tetapi salah, gunakan:

```cmd
git remote set-url origin https://github.com/raihan-azhari/kripto-hibrida-steganografi.git
git push -u origin main
```

Jika GitHub menolak akses karena masih login ke akun lama, hapus credential GitHub lama melalui **Windows Credential Manager**, lalu ulangi proses `git push` dan login menggunakan akun GitHub yang benar.

---

## 📌 Catatan

Program ini dibuat untuk memenuhi tugas program Kriptografi Hibrida dan Steganografi. Seluruh proses utama sudah disediakan dalam bentuk perintah CLI agar mudah diuji, dijalankan ulang, dan didokumentasikan.

Pengujian utama dilakukan dengan membandingkan hash SHA-256 plaintext asli dan file hasil dekripsi. Selain itu, tanda tangan digital juga diverifikasi untuk memastikan bahwa payload terenkripsi tidak berubah selama proses pengiriman dan penyembunyian data.

---

## 👤 Identitas

**Raihan Azhari Lubis**  
**NIM:** 231111619  
**Program:** Kriptografi Hibrida + Steganografi  
**Repository:** https://github.com/raihan-azhari/kripto-hibrida-steganografi
