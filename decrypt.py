"""
decrypt.py - Modul Dekripsi dengan Penurunan Rumus Invers Lengkap

Tanggung jawab:
- Memvalidasi cipherteks dan parameter a, b.
- Menerapkan D(y) = (y - (b+2)) / a untuk setiap token.
- Mengonversi hasil invers (integer) kembali ke karakter.
- Menyediakan data penurunan rumus matematis untuk ditampilkan di UI.
- Membedakan spasi (x=0 → token nilai E(0)) dari angka biasa.
"""

from typing import Dict, Any, List
from cipher import (
    inv_comp, decrypt_val, num_to_char, get_formula_metadata,
    encrypt_val, DEFAULT_A, DEFAULT_B, G_CONST
)


def _validate_params(a, b) -> Dict[str, Any]:
    try:
        a = int(a)
    except (TypeError, ValueError):
        return {"error": "Koefisien a harus berupa bilangan bulat."}
    try:
        b = int(b)
    except (TypeError, ValueError):
        return {"error": "Konstanta b harus berupa bilangan bulat."}
    if a == 0:
        return {"error": "Koefisien a tidak boleh 0 — fungsi tidak dapat dibalikkan."}
    return {"a": a, "b": b}


def get_derivation_steps(a: int, b: int) -> List[Dict[str, str]]:
    """
    Menghasilkan langkah penurunan rumus invers secara matematis.
    Ditampilkan di bagian atas halaman dekripsi.

    Untuk E(x) = ax + (b+2):
      y = ax + (b+2)
      y - (b+2) = ax
      x = (y - (b+2)) / a
      D(y) = (y - (b+2)) / a
    """
    c = b + G_CONST
    sign_b = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    sign_c = f"+ {c}" if c >= 0 else f"- {abs(c)}"

    steps = [
        {
            "step": "1",
            "label": "Fungsi enkripsi akhir",
            "expr": f"E(x) = {a}x {sign_c}",
            "note": f"Dari komposisi: f(x) = {a}x {sign_b}, g(x) = x + 2"
        },
        {
            "step": "2",
            "label": "Misalkan y = E(x)",
            "expr": f"y = {a}x {sign_c}",
            "note": "y adalah nilai cipherteks yang diketahui"
        },
        {
            "step": "3",
            "label": "Isolasi suku ax",
            "expr": f"y {('- ' + str(c)) if c >= 0 else ('+ ' + str(abs(c)))} = {a}x",
            "note": f"Kurangi kedua ruas dengan {c}"
        },
        {
            "step": "4",
            "label": "Selesaikan untuk x",
            "expr": f"x = (y {('- ' + str(c)) if c >= 0 else ('+ ' + str(abs(c)))}) / {a}",
            "note": f"Bagi kedua ruas dengan {a}"
        },
        {
            "step": "5",
            "label": "Fungsi invers D(y)",
            "expr": f"D(y) = (y {('- ' + str(c)) if c >= 0 else ('+ ' + str(abs(c)))}) / {a}",
            "note": "Fungsi pemulih sandi yang digunakan untuk setiap token cipherteks"
        },
    ]
    return steps


def decrypt_ciphertext(ciphertext_str: str,
                       a: int = DEFAULT_A,
                       b: int = DEFAULT_B) -> Dict[str, Any]:
    """
    Mendekripsi token angka cipherteks menggunakan D(y) = (y - (b+2)) / a.

    Format input: angka-angka (positif, negatif, atau nol) dipisahkan spasi.
    Token yang menghasilkan x=0 dikenali sebagai spasi.

    Args:
        ciphertext_str : String token angka, mis. "5 25 45" atau "5 25 45 3 11 21 5"
        a              : Koefisien enkripsi (default 2).
        b              : Konstanta enkripsi (default 1).

    Returns:
        dict berisi success, ciphertext, plaintext, steps, derivation_steps,
        formula_info, a, b, dan error (jika gagal).
    """
    param = _validate_params(a, b)
    if "error" in param:
        return {"success": False, "error": param["error"]}
    a, b = param["a"], param["b"]

    if not isinstance(ciphertext_str, str):
        return {"success": False, "error": "Cipherteks harus berupa teks string."}

    trimmed = ciphertext_str.strip()
    if not trimmed:
        return {"success": False, "error": "Cipherteks tidak boleh kosong."}

    raw_tokens = trimmed.split()
    if len(raw_tokens) > 500:
        return {"success": False, "error": "Cipherteks terlalu panjang (batas 500 token)."}

    c = b + G_CONST
    derivation_steps = get_derivation_steps(a, b)
    formula_info = get_formula_metadata(a, b)

    steps: List[Dict] = []
    plain_chars: List[str] = []

    for idx, token in enumerate(raw_tokens):
        # Dukungan pemisah kata '|'
        if token == '|':
            plain_chars.append(' ')
            steps.append({
                "index": idx + 1,
                "token": "|",
                "is_space": True,
                "y": c,
                "sub_calc": "Pemisah kata '|' → SPASI",
                "div_calc": "x = 0",
                "inv_result": 0,
                "char": "SPASI",
                "explanation": "Simbol '|' dikenali sebagai pemisah kata (SPASI, x=0)."
            })
            continue

        # Validasi format token (bilangan bulat, boleh negatif)
        if '.' in token or ',' in token:
            return {
                "success": False,
                "error": f"Token '{token}' bukan bilangan bulat. Cipherteks harus berisi angka bulat saja."
            }
        try:
            y = int(token)
        except ValueError:
            return {
                "success": False,
                "error": f"Token '{token}' bukan angka yang valid."
            }

        # Dekripsi: D(y) = (y - c) / a
        sub_val = y - c
        raw = sub_val / a

        # Cek apakah hasilnya integer tepat
        if abs(raw - round(raw)) > 1e-9:
            return {
                "success": False,
                "error": (
                    f"Token {y} tidak dapat didekripsi menjadi bilangan bulat "
                    f"dengan parameter a={a}, b={b}: D({y}) = {raw:.4f} (bukan integer). "
                    f"Periksa parameter enkripsi yang digunakan."
                )
            }

        x = int(round(raw))

        # Validasi rentang x
        if not (-26 <= x <= 26):
            return {
                "success": False,
                "error": (
                    f"Token {y} menghasilkan x={x} yang di luar rentang valid (-26..0..26) "
                    f"dengan parameter a={a}, b={b}."
                )
            }

        # Konversi x ke karakter
        try:
            char = num_to_char(x)
        except ValueError as e:
            return {"success": False, "error": str(e)}

        plain_chars.append(char)
        is_space = (x == 0)

        steps.append({
            "index": idx + 1,
            "token": token,
            "is_space": is_space,
            "y": y,
            "sub_calc": f"({y}) - ({c}) = {sub_val}",
            "div_calc": f"{sub_val} / {a} = {x}",
            "inv_result": x,
            "char": "SPASI" if is_space else char,
            "explanation": (
                f"D({y}) = ({y} − {c}) / {a} = {sub_val} / {a} = {x} "
                f"→ {'SPASI' if is_space else repr(char)}."
            )
        })

    plaintext = "".join(plain_chars)

    return {
        "success": True,
        "ciphertext": ciphertext_str,
        "plaintext": plaintext,
        "steps": steps,
        "derivation_steps": derivation_steps,
        "formula_info": formula_info,
        "a": a,
        "b": b,
    }
