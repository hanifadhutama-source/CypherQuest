"""
encrypt.py - Modul Pemrosesan Enkripsi dan Rincian Langkah Matematis

Tanggung jawab:
- Memvalidasi pesan asli (plaintext).
- Mengonversi karakter menjadi angka x (A=1 ... Z=26).
- Menerapkan f(x) = 2x + 1.
- Menerapkan g(f(x)) = f(x) + 2 = 2x + 3.
- Menghasilkan representasi cipherteks yang dipisahkan spasi (dan '|' untuk spasi antar kata).
- Menghasilkan rincian langkah perhitungan matematis dinamis.
"""

from typing import Dict, Any, List
from cipher import char_to_num, f, g, g_comp_f, validate_character_support, get_formula_metadata


def encrypt_message(plaintext: str) -> Dict[str, Any]:
    """
    Mengenkripsi teks asli (plaintext) menggunakan komposisi fungsi E(x) = g(f(x)) = 2x + 3.
    
    Args:
        plaintext: String pesan yang akan dienkripsi.
        
    Returns:
        dict berisi:
        - success (bool)
        - plaintext (str)
        - ciphertext (str)
        - tokens (list)
        - steps (list of dict)
        - formula_info (dict)
        - error (str, jika gagal)
    """
    if not isinstance(plaintext, str):
        return {
            "success": False,
            "error": "Pesan harus berupa teks string."
        }
    
    trimmed = plaintext.strip()
    if not trimmed:
        return {
            "success": False,
            "error": "Pesan asli tidak boleh kosong. Masukkan setidaknya satu kata."
        }
    
    if len(plaintext) > 200:
        return {
            "success": False,
            "error": "Panjang pesan melebihi batas maksimal (200 karakter)."
        }
    
    # Validasi karakter: Hanya huruf alfabet dan spasi
    unsupported_chars = set()
    for char in plaintext:
        if not validate_character_support(char):
            unsupported_chars.add(char)
            
    if unsupported_chars:
        chars_display = ", ".join(f"'{c}'" for c in sorted(unsupported_chars))
        return {
            "success": False,
            "error": f"Karakter tidak didukung ditemukan: {chars_display}. Sistem hanya mendukung huruf alfabet (A-Z) dan spasi."
        }
    
    tokens = []
    steps = []
    
    # Proses enkripsi karakter per karakter
    for idx, char in enumerate(plaintext):
        if char == ' ':
            tokens.append("|")
            steps.append({
                "index": idx + 1,
                "char": "SPASI",
                "is_space": True,
                "x": None,
                "f_calc": "-",
                "f_val": "-",
                "g_calc": "-",
                "g_val": "-",
                "comp_calc": "-",
                "final_val": "|",
                "explanation": "Spasi dipertahankan sebagai pemisah kata '|'."
            })
        else:
            is_upper = char.isupper()
            x = char_to_num(char)
            
            # Langkah f(x)
            f_val = f(x)
            f_calc = f"2({x}) + 1 = {f_val}"
            
            # Langkah g(f(x))
            g_val = g(f_val)
            g_calc = f"{f_val} + 2 = {g_val}"
            
            # Komposisi langsung (g o f)(x) = 2x + 3
            comp_val = g_comp_f(x)
            comp_calc = f"2({x}) + 3 = {comp_val}"
            
            tokens.append(str(comp_val))
            steps.append({
                "index": idx + 1,
                "char": char,
                "is_space": False,
                "is_upper": is_upper,
                "x": x,
                "f_calc": f_calc,
                "f_val": f_val,
                "g_calc": g_calc,
                "g_val": g_val,
                "comp_calc": comp_calc,
                "final_val": comp_val,
                "explanation": (
                    f"Huruf '{char}' \u2192 Nilai x = {x}. "
                    f"Tahap 1: f({x}) = 2({x}) + 1 = {f_val}. "
                    f"Tahap 2: g({f_val}) = {f_val} + 2 = {g_val}. "
                    f"Komposisi: (g \u2218 f)({x}) = 2({x}) + 3 = {comp_val}."
                )
            })
            
    ciphertext = " ".join(tokens)
    
    return {
        "success": True,
        "plaintext": plaintext,
        "ciphertext": ciphertext,
        "tokens": tokens,
        "steps": steps,
        "formula_info": get_formula_metadata()
    }
