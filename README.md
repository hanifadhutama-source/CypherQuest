# CipherQuest — Decode the Message, Complete the Mission
**Game Edukasi Kriptografi Matematika Berbasis Python Flask**

![Status Pengujian](https://img.shields.io/badge/pytest-30%20passed-10B981?style=for-the-badge&logo=pytest&logoColor=white)
![Python Version](https://img.shields.io/badge/python-3.9+-22D3EE?style=for-the-badge&logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/framework-Flask%203.x-8B5CF6?style=for-the-badge&logo=flask&logoColor=white)
![Classification](https://img.shields.io/badge/classification-CONFIDENTIAL-F59E0B?style=for-the-badge)

---

## 1. Deskripsi Produk

**CipherQuest — Decode the Message, Complete the Mission** adalah sebuah aplikasi web edukasi interaktif bertema investigasi agen rahasia (*secret agent / cyber intelligence division*). Aplikasi ini dikembangkan sebagai proyek akhir semester mata pelajaran Matematika Kelas XI SMK untuk materi:
- **Komposisi Fungsi** $(g \circ f)(x)$
- **Invers Fungsi** $D(y) = f^{-1}(y)$
- **Fungsi Linear**
- **Kriptografi Klasik Sederhana** (Enkripsi & Dekripsi Pesan)

Pemain bertindak sebagai agen intelijen yang mencegat transmisi tersandi musuh, memecahkan kode rahasia, melihat proses perhitungan matematis dinamis langkah demi langkah, dan menyelesaikan rangkaian misi berjenjang.

---

## 2. Tujuan Pembelajaran

1. **Pemahaman Konseptual**: Memahami bahwa enkripsi pesan dapat direpresentasikan sebagai fungsi matematika yang memetakan huruf (domain) ke angka sandi (kodomain).
2. **Komposisi Fungsi**: Membuktikan bagaimana dua operasi linear berurutan $f(x)$ dan $g(x)$ dapat digabung menjadi satu fungsi enkripsi tunggal $(g \circ f)(x)$.
3. **Invers Fungsi**: Memahami mengapa dekripsi membutuhkan fungsi invers $D(y)$, serta membuktikan secara aljabar bahwa $D(E(x)) = x$ mengembalikan nilai pesan asal secara sempurna.
4. **Karakteristik Sifat Bijektif**: Memahami pentingnya pemetaan satu-ke-satu (*one-to-one*) agar pesan tidak mengalami ambiguitas saat didekripsi.

---

## 3. Fitur Utama

- **Hero & Intel Briefing**: Dashboard intelijen dengan kutipan arahan misi, status agen, dan telemetri langsung (*live score & completed missions*).
- **Papan Misi Berjenjang (Campaign)**:
  - **Misi 01 — First Transmission** (Tingkat: Mudah): Pengenalan konversi huruf ke angka dan enkripsi linear dasar kata "SPY".
  - **Misi 02 — Double Encryption** (Tingkat: Menengah): Pembuktian komposisi dua fungsi linear $f$ dan $g$ pada kata "AGENT".
  - **Misi 03 — Reverse the Code** (Tingkat: Mahir): Rekonstruksi cipherteks musuh `"41 13 9 39 13 43"` menjadi kata "SECRET" menggunakan fungsi invers.
- **Sistem Skor & Progres (SQLite)**:
  - Jawaban benar: **+100 poin**.
  - Jawaban salah: **0 poin** (tidak menambah skor).
  - Fitur Bantuan Petunjuk (*Hint*): **Penalti 20 poin** (maksimal 80 poin).
  - **Bebas Duplikasi**: Menggunakan pola *idempotent database upsert* sehingga skor tidak terduplikasi saat halaman dimuat ulang (*reload*).
  - Pembukaan misi bertahap (Misi $n$ terbuka setelah Misi $n-1$ selesai).
  - Tombol **Reset Progres** untuk mengulang simulasi dari awal.
- **Laboratorium Enkripsi (Sandbox)**:
  - Input teks bebas (A-Z dan spasi).
  - Tombol demo cepat **"Gunakan AKU"**.
  - Panel visual $f(x)$, $g(x)$, dan $(g \circ f)(x)$.
  - **Accordion Langkah Perhitungan Dinamis**: Rincian per karakter ($x \to f(x) \to g(f(x)) \to \text{Cipher}$).
  - Tombol Salin Cipherteks ke papan klip (*clipboard*) dan tombol Reset.
- **Laboratorium Dekripsi (Sandbox)**:
  - Input angka cipherteks ganjil.
  - Tombol demo cepat **"Gunakan 5 25 45"**.
  - Validasi ketat (menolak angka genap, angka di luar rentang 5–55, atau input non-numerik).
  - **Accordion Langkah Perhitungan Invers Dinamis**: Menguraikan substitusi ke $D(y) = (y - 3) / 2$.
  - Tombol Salin Plainteks.
- **Akademi Kriptografi (Tutorial)**:
  - Materi lengkap berurutan: plainteks, enkripsi, cipherteks, dekripsi, komposisi fungsi, invers fungsi, dan pembuktian $D(E(x)) = x$.
  - Diagram visual alur transformasi proses enkripsi dan dekripsi.
  - Tabel konversi huruf A=1 s.d. Z=26.
- **Desain UI/UX Agen Rahasia**:
  - Palet warna investigasi cyber (*Dark slate, Cyan glow, Neon purple, Emerald green*).
  - Responsif *mobile-first* (tanpa *horizontal overflow* pada resolusi smartphone 320px hingga desktop 4K).
  - Ikon SVG lokal tanpa ketergantungan CDN eksternal.

---

## 4. Landasan Matematika

### A. Fungsi Linear Pertama
$$f(x) = 2x + 1$$

### B. Fungsi Linear Kedua
$$g(x) = x + 2$$

### C. Komposisi Fungsi Enkripsi: $(g \circ f)(x)$
Komposisi dilakukan dengan memasukkan hasil $f(x)$ ke dalam fungsi $g(x)$:
$$(g \circ f)(x) = g(f(x))$$
$$(g \circ f)(x) = g(2x + 1)$$
Karena $g(x) = x + 2$, maka:
$$(g \circ f)(x) = (2x + 1) + 2$$
$$\mathbf{E(x) = 2x + 3}$$

Fungsi enkripsi gabungan adalah **$E(x) = 2x + 3$**.

### D. Invers Fungsi Dekripsi: $D(y)$
Untuk membalikkan proses sandi, cari invers dari $y = 2x + 3$:
$$y = 2x + 3$$
$$y - 3 = 2x$$
$$2x = y - 3$$
$$\mathbf{x = \frac{y - 3}{2}}$$
$$\mathbf{D(y) = \frac{y - 3}{2}}$$

Fungsi dekripsi invers adalah **$D(y) = \frac{y - 3}{2}$**.

### E. Pembuktian Matematis Pemulihan Pesan
$$D(E(x)) = D(2x + 3) = \frac{(2x + 3) - 3}{2} = \frac{2x}{2} = x$$
Karena $D(E(x)) = x$, pesan asli dijamin kembali 100% tanpa kesalahan aljabar.

---

## 5. Tabel Pemetaan Alfabet

| Huruf | Angka ($x$) | Huruf | Angka ($x$) | Huruf | Angka ($x$) | Huruf | Angka ($x$) |
|:-----:|:-----------:|:-----:|:-----------:|:-----:|:-----------:|:-----:|:-----------:|
| **A** | 1           | **H** | 8           | **O** | 15          | **V** | 22          |
| **B** | 2           | **I** | 9           | **P** | 16          | **W** | 23          |
| **C** | 3           | **J** | 10          | **Q** | 17          | **X** | 24          |
| **D** | 4           | **K** | 11          | **R** | 18          | **Y** | 25          |
| **E** | 5           | **L** | 12          | **S** | 19          | **Z** | 26          |
| **F** | 6           | **M** | 13          | **T** | 20          |       |             |
| **G** | 7           | **N** | 14          | **U** | 21          |       |             |

- Spasi antar kata dipertahankan menggunakan simbol pemisah `|`.

---

## 6. Contoh Wajib: AKU

### Proses Enkripsi
1. **Konversi Huruf ke Angka**:
   - $A = 1$
   - $K = 11$
   - $U = 21$
2. **Substitusi ke $E(x) = 2x + 3$**:
   - $E(1) = 2(1) + 3 = 5$
   - $E(11) = 2(11) + 3 = 25$
   - $E(21) = 2(21) + 3 = 45$
3. **Hasil Cipherteks**: `5 25 45`

### Proses Dekripsi
1. **Cipherteks Masukan**: `5 25 45`
2. **Substitusi ke $D(y) = \frac{y - 3}{2}$**:
   - $D(5) = \frac{5 - 3}{2} = \frac{2}{2} = 1 \implies \mathbf{A}$
   - $D(25) = \frac{25 - 3}{2} = \frac{22}{2} = 11 \implies \mathbf{K}$
   - $D(45) = \frac{45 - 3}{2} = \frac{42}{2} = 21 \implies \mathbf{U}$
3. **Hasil Plainteks**: `AKU`

---

## 7. Struktur Folder Proyek

```
CipherQuest/
├── app.py                     # Inisialisasi Flask, route, session, & error handling
├── cipher.py                  # Logika matematika f(x), g(x), (g o f)(x), dan D(y)
├── encrypt.py                 # Algoritma pemrosesan enkripsi & rincian langkah
├── decrypt.py                 # Algoritma pemrosesan dekripsi & validasi invers
├── database.py                # Database SQLite, manajemen progres misi & skor
├── config.py                  # Konfigurasi aplikasi & secret key
├── requirements.txt           # Daftar dependensi Python
├── Procfile                   # Konfigurasi startup server WSGI produksi (Gunicorn)
├── .gitignore                 # Daftar file/folder yang diabaikan Git
├── README.md                  # Dokumentasi teknis & panduan lengkap
├── instance/
│   ├── .gitkeep
│   └── cipherquest.db         # Database SQLite lokal (dibuat otomatis)
├── templates/
│   ├── base.html              # Layout master Jinja2 dengan navbar agen & footer
│   ├── index.html             # Halaman beranda, briefing intelijen & dashboard
│   ├── missions.html          # Papan misi intelijen berjenjang
│   ├── mission_detail.html    # Halaman pengerjaan misi & input jawaban
│   ├── encrypt.html           # Laboratorium enkripsi pesan
│   ├── decrypt.html           # Laboratorium dekripsi cipherteks
│   ├── tutorial.html          # Modul edukasi matematika & kriptografi
│   ├── result.html            # Hasil evaluasi pengerjaan misi & skor
│   └── 404.html               # Halaman kesalahan rute bertema sinyal terputus
├── static/
│   ├── css/
│   │   └── style.css          # Styling CSS3 lengkap & responsif mobile-first
│   ├── js/
│   │   └── app.js             # Skrip interaksi antarmuka (copy, accordion, hint)
│   └── images/
│       └── .gitkeep
└── tests/
    ├── test_cipher.py         # Unit testing fungsi matematika & rumus
    ├── test_encrypt.py        # Unit testing pemrosesan enkripsi
    ├── test_decrypt.py        # Unit testing pemrosesan dekripsi & validasi
    └── test_routes.py         # Integration testing rute Flask & alur misi
```

---

## 8. Panduan Menjalankan Secara Lokal

### Prasyarat
- Python versi 3.9 atau lebih baru.
- Pip (Python Package Manager).

### Langkah 1: Buat & Aktifkan Virtual Environment
Buka terminal / PowerShell di direktori proyek:

**Di Windows (PowerShell / Command Prompt):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Di Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Langkah 2: Pasang Dependensi
```bash
pip install -r requirements.txt
```

### Langkah 3: Jalankan Aplikasi

**A. Akses di Komputer / Laptop Sendiri (Localhost):**
```bash
python app.py
```
Akses di browser laptop:
```
http://127.0.0.1:5000/
```

**B. Akses Melalui HP (Smartphone Android / iPhone) via Wi-Fi yang Sama:**
Untuk memainkan CipherQuest langsung dari layar HP tanpa harus di-deploy ke internet:
1. Pastikan laptop dan HP terhubung ke **jaringan Wi-Fi yang sama**.
2. Buka terminal baru di laptop dan cari alamat IP lokal laptop:
   - **Di Windows**: Ketik `ipconfig`, lalu cari baris **IPv4 Address** (contoh: `192.168.1.15`).
   - **Di Linux / macOS**: Ketik `ifconfig` atau `ip a`.
3. Jalankan aplikasi Flask dengan mengizinkan binding ke semua antarmuka jaringan (`0.0.0.0`):
   ```bash
   python -m flask --app app run --host=0.0.0.0 --port=5000
   ```
4. Buka peramban di HP (Chrome / Safari / Firefox) dan masukkan alamat:
   ```
   http://<ALAMAT-IP-LAPTOP>:5000
   ```
   *Contoh:* `http://192.168.1.15:5000`
5. **Solusi Kendala Firewall (Troubleshooting):**
   - Jika peramban HP menampilkan pesan *“Situs ini tidak dapat dijangkau”* atau *“Connection timed out”*, Windows Defender Firewall mungkin memblokir port 5000.
   - Buka **Windows Security** &rarr; **Firewall & network protection** &rarr; **Allow an app through firewall**, lalu centang **Python** untuk jaringan **Private**.
   - Atau pastikan koneksi Wi-Fi diatur sebagai *Private Network*, bukan *Public Network*.

---

## 9. Menjalankan Pengujian Otomatis

Proyek ini dilengkapi dengan 33 pengujian otomatis (*automated unit, integration, and mobile responsiveness tests*) menggunakan `pytest`:

Jalankan seluruh tes dengan perintah:
```bash
python -m pytest -v
```

Hasil pengujian yang diharapkan:
```text
tests/test_cipher.py::test_f_function PASSED                             [  3%]
tests/test_cipher.py::test_g_function PASSED                             [  6%]
tests/test_cipher.py::test_g_comp_f_examples PASSED                      [  9%]
tests/test_cipher.py::test_composition_formula PASSED                    [ 12%]
tests/test_cipher.py::test_inv_comp_examples PASSED                      [ 15%]
tests/test_cipher.py::test_roundtrip_all_alphabet PASSED                 [ 18%]
tests/test_cipher.py::test_char_conversion PASSED                        [ 21%]
tests/test_decrypt.py::test_decrypt_aku PASSED                           [ 24%]
tests/test_decrypt.py::test_decrypt_with_spaces PASSED                   [ 27%]
tests/test_decrypt.py::test_decrypt_out_of_range PASSED                  [ 30%]
tests/test_decrypt.py::test_decrypt_even_number PASSED                   [ 33%]
tests/test_decrypt.py::test_decrypt_noninteger_or_malformed PASSED       [ 36%]
tests/test_encrypt.py::test_encrypt_aku PASSED                           [ 39%]
tests/test_encrypt.py::test_encrypt_lowercase PASSED                     [ 42%]
tests/test_encrypt.py::test_encrypt_with_spaces PASSED                   [ 45%]
tests/test_encrypt.py::test_encrypt_empty_input PASSED                   [ 48%]
tests/test_encrypt.py::test_encrypt_unsupported_characters PASSED        [ 51%]
tests/test_mobile_responsiveness.py::test_meta_viewport_and_mobile_tags PASSED [ 54%]
tests/test_mobile_responsiveness.py::test_css_mobile_rules_and_breakpoints PASSED [ 57%]
tests/test_mobile_responsiveness.py::test_js_mobile_events PASSED        [ 60%]
tests/test_routes.py::test_index_page PASSED                             [ 63%]
tests/test_routes.py::test_missions_page PASSED                          [ 66%]
tests/test_routes.py::test_encrypt_page_get PASSED                       [ 69%]
tests/test_routes.py::test_encrypt_page_post_success PASSED              [ 72%]
tests/test_routes.py::test_encrypt_page_post_invalid PASSED              [ 75%]
tests/test_routes.py::test_decrypt_page_get PASSED                       [ 78%]
tests/test_routes.py::test_decrypt_page_post_success PASSED              [ 81%]
tests/test_routes.py::test_decrypt_page_post_invalid PASSED              [ 84%]
tests/test_routes.py::test_tutorial_page PASSED                          [ 87%]
tests/test_routes.py::test_mission_flow PASSED                           [ 90%]
tests/test_routes.py::test_demo_query_params PASSED                      [ 93%]
tests/test_routes.py::test_reset_progress_endpoint PASSED                [ 96%]
tests/test_routes.py::test_404_page PASSED                               [100%]

```

---

## 10. Panduan Deployment ke Layanan Hosting

Aplikasi ini menggunakan standar WSGI yang kompatibel dengan berbagai penyedia hosting cloud gratis maupun berbayar (seperti Render, Railway, PythonAnywhere, atau Heroku).

### A. Deployment ke Render / Railway
1. Unggah kode ke repositori GitHub.
2. Buat Web Service baru di Render / Railway dan hubungkan ke repositori.
3. Atur parameter lingkungan (*Environment*):
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (telah disediakan di `Procfile`)
4. Tambahkan *Environment Variables*:
   - `SECRET_KEY`: `(kunci acak rahasia Anda)`
   - `FLASK_DEBUG`: `0`
5. Klik **Deploy**. Aplikasi akan aktif dan memiliki sertifikat SSL otomatis.

### B. Deployment ke PythonAnywhere
1. Buka akun di [PythonAnywhere](https://www.pythonanywhere.com/).
2. Buat Web App baru dengan konfigurasi Manual Python 3.9 / 3.10.
3. Klon repositori proyek ke direktori akun.
4. Buat virtualenv dan jalankan `pip install -r requirements.txt`.
5. Pada file konfigurasi WSGI PythonAnywhere (`/var/www/..._wsgi.py`), impor aplikasi:
   ```python
   import sys
   path = '/home/username/CipherQuest'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```
6. Simpan dan klik **Reload**.

---

## 11. Batasan Aplikasi & Catatan Keamanan

1. **Simulasi Pembelajaran**: Skema enkripsi linear $E(x) = 2x + 3$ merupakan alat peraga edukasi konsep matematika dan **bukan** algoritma keamanan untuk melindungi data rahasia riil di dunia maya. Sandi linear rentan terhadap serangan analisis frekuensi (*frequency analysis*).
2. **Karakter Masukan**: Sistem memetakan karakter alfabet standar A-Z (huruf besar/kecil diproses seragam) dan spasi kata. Karakter simbol atau angka ditolak dengan pesan validasi ramah pengguna.
3. **Penyimpanan Sesi Anonim**: Progres pemain dikaitkan dengan *Session Cookie* peramban. Jika pemain menghapus cookie peramban, riwayat misi akan dimulai dari awal (disediakan juga tombol Reset manual di aplikasi).

---

## 12. Hak Cipta & Lisensi

Dikembangkan untuk keperluan edukasi mata pelajaran Matematika Kelas XI SMK.  
&copy; 2026 CipherQuest Intelligence Division.
