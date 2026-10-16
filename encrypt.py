"""
encrypt.py - Modul Pemrosesan Enkripsi dengan Parameter Kustom

Tanggung jawab:
- Memvalidasi pesan asli (plaintext) dan parameter a, b.
- Mengonversi karakter ke angka x: A–Z → +1..+26, a–z → -1..-26, spasi → 0.
- Menerapkan f(x) = ax + b, lalu g(f(x)) = f(x) + 2.
- Menghasilkan cipherteks bertanda (positif, negatif, nol) dipisahkan spasi.
- Spasi antar kata direpresentasikan sebagai token angka 0.
- Menghasilkan rincian langkah perhitungan matematis dinamis.
"""

from typing import Dict, Any, List
from cipher import (
    char_to_num, f, g, g_comp_f, encrypt_val,
    validate_character_support, get_formula_metadata,
    DEFAULT_A, DEFAULT_B
)

# Batas nilai a dan b yang diizinkan
A_MAX = 1000
B_MIN = -1000
B_MAX = 1000


def _validate_params(a, b) -> Dict[str, Any]:
    """Validasi parameter a dan b. Mengembalikan dict error jika tidak valid."""
    try:
        a = int(a)
    except (TypeError, ValueError):
        return {"error": "Koefisien a harus berupa bilangan bulat."}
    try:
        b = int(b)
    except (TypeError, ValueError):
        return {"error": "Konstanta b harus berupa bilangan bulat."}
    if a == 0:
        return {"error": "Koefisien a tidak boleh 0 — fungsi f(x) = 0·x + b tidak memiliki invers."}
    if abs(a) > A_MAX:
        return {"error": f"Nilai koefisien a terlalu besar (batas: ±{A_MAX})."}
    if not (B_MIN <= b <= B_MAX):
        return {"error": f"Nilai konstanta b di luar batas yang diizinkan ({B_MIN}..{B_MAX})."}
    return {"a": a, "b": b}


def encrypt_message(plaintext: str, a: int = DEFAULT_A, b: int = DEFAULT_B) -> Dict[str, Any]:
    """
    Mengenkripsi teks menggunakan komposisi fungsi E(x) = g(f(x)) = ax + (b+2).

    Pemetaan karakter:
      A–Z → +1..+26  (kapital = positif)
      a–z → -1..-26  (kecil   = negatif)
      spasi → 0      (spasi   = nol, dimunculkan sebagai token '0')

    Args:
        plaintext : String pesan yang akan dienkripsi.
        a         : Koefisien f(x) = ax + b  (default 2).
        b         : Konstanta  f(x) = ax + b  (default 1).

    Returns:
        dict berisi success, plaintext, ciphertext, tokens, steps,
        formula_info, a, b, dan error (jika gagal).
    """
    # Validasi parameter
    param = _validate_params(a, b)
    if "error" in param:
        return {"success": False, "error": param["error"]}
    a, b = param["a"], param["b"]

    if not isinstance(plaintext, str):
        return {"success": False, "error": "Pesan harus berupa teks string."}

    trimmed = plaintext.strip()
    if not trimmed:
        return {"success": False, "error": "Pesan asli tidak boleh kosong. Masukkan setidaknya satu karakter."}

    if len(plaintext) > 200:
        return {"success": False, "error": "Panjang pesan melebihi batas maksimal (200 karakter)."}

    # Validasi karakter
    unsupported = {ch for ch in plaintext if not validate_character_support(ch)}
    if unsupported:
        chars_display = ", ".join(f"'{c}'" for c in sorted(unsupported))
        return {
            "success": False,
            "error": (
                f"Karakter tidak didukung: {chars_display}. "
                "Sistem mendukung huruf A–Z (kapital), a–z (kecil), dan spasi."
            )
        }

    tokens: List[str] = []
    steps: List[Dict] = []
    c = b + 2   # konstanta komposisi: E(x) = ax + c

    for idx, char in enumerate(plaintext):
        if char == ' ':
            # Spasi → x=0 → E(0) = a*0 + c = c
            # Kita simpan sebagai token angka biasa agar bisa dibedakan
            e_space = encrypt_val(0, a, b)
            tokens.append(str(e_space))
            steps.append({
                "index": idx + 1,
                "char": "SPASI",
                "is_space": True,
                "x": 0,
                "f_calc": f"a·0 + {b} = {b}",
                "f_val": b,
                "g_calc": f"{b} + 2 = {c}",
                "g_val": c,
                "comp_calc": f"a·0 + {c} = {e_space}",
                "final_val": e_space,
                "explanation": f"Spasi → x=0. E(0) = {a}·0 + {c} = {e_space}."
            })
        else:
            x = char_to_num(char)
            f_val = f(x, a, b)
            g_val = g(f_val)
            comp_val = g_comp_f(x, a, b)

            f_calc = f"{a}·({x}) + {b} = {f_val}"
            g_calc = f"{f_val} + 2 = {g_val}"
            comp_calc = f"{a}·({x}) + {c} = {comp_val}"

            tokens.append(str(comp_val))
            steps.append({
                "index": idx + 1,
                "char": char,
                "is_space": False,
                "x": x,
                "f_calc": f_calc,
                "f_val": f_val,
                "g_calc": g_calc,
                "g_val": g_val,
                "comp_calc": comp_calc,
                "final_val": comp_val,
                "explanation": (
                    f"'{char}' → x={x}. "
                    f"f({x})={a}·({x})+{b}={f_val}. "
                    f"g({f_val})={f_val}+2={g_val}. "
                    f"E({x})={a}·({x})+{c}={comp_val}."
                )
            })

    ciphertext = " ".join(tokens)
    formula_info = get_formula_metadata(a, b)

    return {
        "success": True,
        "plaintext": plaintext,
        "ciphertext": ciphertext,
        "tokens": tokens,
        "steps": steps,
        "formula_info": formula_info,
        "a": a,
        "b": b,
    }
