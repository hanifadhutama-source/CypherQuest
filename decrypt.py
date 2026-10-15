"""
decrypt.py - Modul Pemrosesan Dekripsi dan Rincian Langkah Invers Matematis

Tanggung jawab:
- Memvalidasi cipherteks masukan.
- Memeriksa batas nilai (5 - 55), paritas (ganjil), dan integritas matematis.
- Menerapkan fungsi invers D(y) = (y - 3) / 2.
- Mengonversi angka hasil invers menjadi huruf alfabet (1=A ... 26=Z).
- Memulihkan spasi antar kata dari pemisah '|'.
- Menghasilkan rincian langkah perhitungan invers matematis dinamis.
"""

from typing import Dict, Any, List
from cipher import inv_comp, decrypt_val, num_to_char, get_formula_metadata


def decrypt_ciphertext(ciphertext_str: str) -> Dict[str, Any]:
    """
    Mendekripsi pesan cipherteks berupa angka-angka yang dipisahkan spasi
    menggunakan fungsi invers D(y) = (y - 3) / 2.
    
    Args:
        ciphertext_str: String berisi angka cipherteks, contoh: "5 25 45" atau "5 25 45 | 7 19 41 5"
        
    Returns:
        dict berisi:
        - success (bool)
        - ciphertext (str)
        - plaintext (str)
        - steps (list of dict)
        - formula_info (dict)
        - error (str, jika gagal)
    """
    if not isinstance(ciphertext_str, str):
        return {
            "success": False,
            "error": "Cipherteks harus berupa teks string."
        }
    
    trimmed = ciphertext_str.strip()
    if not trimmed:
        return {
            "success": False,
            "error": "Cipherteks tidak boleh kosong. Masukkan angka kode rahasia."
        }
    
    # Normalisasi pemisah: pecah berdasarkan spasi
    raw_tokens = trimmed.split()
    
    steps = []
    plain_chars = []
    
    for idx, token in enumerate(raw_tokens):
        # Penanganan pemisah kata spasi '|'
        if token == '|':
            plain_chars.append(' ')
            steps.append({
                "index": idx + 1,
                "token": "|",
                "is_space": True,
                "y": None,
                "sub_calc": "-",
                "div_calc": "-",
                "inv_result": "-",
                "char": "SPASI",
                "explanation": "Simbol '|' dikenali sebagai spasi pemisah kata."
            })
            continue
            
        # Validasi apakah token merupakan angka bulat
        try:
            # Periksa apakah ada koma/titik desimal tidak valid
            if '.' in token or ',' in token:
                return {
                    "success": False,
                    "error": f"Kode tidak valid. Nilai '{token}' bukan bilangan bulat. Periksa kembali format cipherteks dan kunci yang digunakan."
                }
            y = int(token)
        except ValueError:
            return {
                "success": False,
                "error": f"Kode tidak valid. Nilai '{token}' bukan angka yang valid. Periksa kembali format cipherteks dan kunci yang digunakan."
            }
            
        # Validasi batas rentang dan paritas ganjil
        # E(x) = 2x + 3 untuk x in [1, 26] menghasilkan bilangan ganjil 5 s.d. 55
        if y < 5 or y > 55 or y % 2 == 0:
            return {
                "success": False,
                "error": f"Kode tidak valid. Angka {y} di luar rentang valid atau bukan bilangan ganjil (E(x) = 2x + 3 menghasilkan angka ganjil 5-55). Periksa kembali format cipherteks dan kunci yang digunakan."
            }
            
        # Hitung invers D(y) = (y - 3) / 2
        try:
            sub_step = y - 3
            orig_x = decrypt_val(y)
            char = num_to_char(orig_x, uppercase=True)
            
            sub_calc = f"({y} - 3) = {sub_step}"
            div_calc = f"{sub_step} / 2 = {orig_x}"
            
            plain_chars.append(char)
            steps.append({
                "index": idx + 1,
                "token": str(y),
                "is_space": False,
                "y": y,
                "sub_calc": sub_calc,
                "div_calc": div_calc,
                "inv_result": orig_x,
                "char": char,
                "explanation": (
                    f"Nilai y = {y}. "
                    f"Substitusi invers: D({y}) = ({y} - 3) / 2 = {sub_step} / 2 = {orig_x}. "
                    f"Konversi angka {orig_x} \u2192 Huruf '{char}'."
                )
            })
        except ValueError as ve:
            return {
                "success": False,
                "error": f"Kode tidak valid. Nilai {y} menghasilkan kesalahan dekripsi: {str(ve)}. Periksa kembali format cipherteks dan kunci yang digunakan."
            }
            
    plaintext = "".join(plain_chars)
    
    return {
        "success": True,
        "ciphertext": ciphertext_str,
        "plaintext": plaintext,
        "steps": steps,
        "formula_info": get_formula_metadata()
    }
