"""
cipher.py - Modul Logika Matematika Inti CipherQuest

Materi:
- Fungsi linear f(x) = ax + b  (default: a=2, b=1)
- Fungsi linear g(x) = x + 2   (tetap, konstanta materi kelas)
- Komposisi fungsi (g o f)(x)  = g(f(x)) = ax + (b + 2)
- Invers fungsi D(y) = (y - (b+2)) / a
- Pemetaan karakter diperluas:
    Huruf kapital A–Z  → x =  1 ..  26  (positif)
    Huruf kecil   a–z  → x = -1 .. -26  (negatif)
    Spasi              → x = 0

Catatan matematis:
  E(x) = ax + (b+2) selalu invertibel jika a ≠ 0.
  D(E(x)) = (ax+(b+2)-(b+2))/a = x  → selalu tepat, tidak ada pembulatan.
  Tidak ada tabrakan kode karena E bijektif (satu-ke-satu).
  Untuk a=2, b=1:  E(x) = 2x+3, D(y) = (y-3)/2.
  Setiap output E adalah ganjil → validasi paritas membantu mendeteksi input rusak.
"""

from typing import Union, Tuple, Optional, Dict, Any


# ─── Konstanta Default (Materi Kelas) ────────────────────────────────────────
DEFAULT_A = 2   # koefisien f(x) = ax + b
DEFAULT_B = 1   # konstanta  f(x) = ax + b
G_CONST = 2     # g(x) = x + G_CONST  (tetap, sesuai kurikulum)


# ─── Pemetaan Karakter ────────────────────────────────────────────────────────

def char_to_num(char: str) -> int:
    """
    Pemetaan karakter ke bilangan bulat (diperluas).

    Kapital A–Z  →  1 ..  26   (positif)
    Kecil   a–z  → -1 .. -26   (negatif)
    Spasi        →  0

    Raises:
        ValueError: jika karakter tidak didukung.
    """
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError("Input harus berupa satu karakter string.")
    if char == ' ':
        return 0
    if char.isupper() and char.isalpha():
        return ord(char) - ord('A') + 1   #  1..26
    if char.islower() and char.isalpha():
        return -(ord(char) - ord('a') + 1)  # -1..-26
    raise ValueError(
        f"Karakter '{char}' tidak didukung. "
        "Sistem mendukung A–Z (kapital → positif), a–z (kecil → negatif), dan spasi (→ 0)."
    )


def num_to_char(num: int) -> str:
    """
    Konversi bilangan bulat ke karakter (kebalikan char_to_num).

     1..26 → A..Z
    -1..-26 → a..z
    0 → ' ' (spasi)

    Raises:
        ValueError: jika num di luar rentang.
    """
    if not isinstance(num, int):
        raise ValueError("Input harus berupa bilangan bulat (integer).")
    if num == 0:
        return ' '
    if 1 <= num <= 26:
        return chr(ord('A') + num - 1)
    if -26 <= num <= -1:
        return chr(ord('a') + (-num) - 1)
    raise ValueError(f"Nilai {num} di luar rentang pemetaan yang valid (-26..0..26).")


# ─── Fungsi Matematika ────────────────────────────────────────────────────────

def f(x: int, a: int = DEFAULT_A, b: int = DEFAULT_B) -> int:
    """
    Fungsi linear pertama:  f(x) = ax + b
    Default: a=2, b=1  →  f(x) = 2x + 1
    """
    if not isinstance(x, (int, float)):
        raise TypeError("Input x harus berupa bilangan.")
    return a * x + b


def g(x: int) -> int:
    """
    Fungsi linear kedua (tetap sesuai kurikulum):
    g(x) = x + 2
    """
    if not isinstance(x, (int, float)):
        raise TypeError("Input x harus berupa bilangan.")
    return x + G_CONST


def g_comp_f(x: int, a: int = DEFAULT_A, b: int = DEFAULT_B) -> int:
    """
    Fungsi komposisi (g o f)(x) = g(f(x)):
    g(f(x)) = g(ax + b) = (ax + b) + 2 = ax + (b + 2)
    """
    return g(f(x, a, b))


def encrypt_val(x: int, a: int = DEFAULT_A, b: int = DEFAULT_B) -> int:
    """
    Fungsi enkripsi gabungan:
    E(x) = (g o f)(x) = ax + (b + 2)
    """
    return g_comp_f(x, a, b)


def inv_comp(y: Union[int, float], a: int = DEFAULT_A, b: int = DEFAULT_B) -> float:
    """
    Fungsi invers dari komposisi E(x) = ax + (b+2):
    y = ax + (b+2)  →  x = (y - (b+2)) / a
    D(y) = (y - (b+2)) / a

    Raises:
        ValueError: jika a = 0 (tidak dapat dibalikkan).
    """
    if a == 0:
        raise ValueError("Koefisien a tidak boleh 0 — fungsi tidak dapat dibalikkan.")
    if not isinstance(y, (int, float)):
        raise TypeError("Input y harus berupa bilangan.")
    return (y - (b + G_CONST)) / a


def decrypt_val(y: int, a: int = DEFAULT_A, b: int = DEFAULT_B) -> int:
    """
    Mendekripsi nilai cipherteks y dengan parameter (a, b).
    Mengembalikan nilai integer x yang terpeta ke karakter.

    Validasi:
    - D(y) harus menghasilkan bilangan bulat tepat (bukan pecahan).
    - Hasil x harus dalam rentang valid (-26..0..26).

    Raises:
        ValueError: jika y tidak dapat didekripsi menjadi simbol valid.
    """
    if a == 0:
        raise ValueError("Koefisien a tidak boleh 0.")
    raw = inv_comp(y, a, b)
    if abs(raw - round(raw)) > 1e-9:
        raise ValueError(
            f"Nilai cipherteks {y} tidak menghasilkan bilangan bulat "
            f"dengan parameter a={a}, b={b}: D({y}) = {raw}."
        )
    x = int(round(raw))
    if not (-26 <= x <= 26):
        raise ValueError(
            f"Hasil invers x = {x} di luar rentang pemetaan yang valid (-26..0..26)."
        )
    return x


# ─── Utilitas ────────────────────────────────────────────────────────────────

def validate_character_support(char: str) -> bool:
    """
    Memeriksa apakah karakter didukung oleh sistem:
    A–Z, a–z, dan spasi.
    """
    return (char.isalpha() and char.isascii()) or char == ' '


def get_formula_metadata(a: int = DEFAULT_A, b: int = DEFAULT_B) -> Dict[str, Any]:
    """
    Mengembalikan metadata rumus matematis berdasarkan parameter a dan b.

    Args:
        a: Koefisien f(x) = ax + b.
        b: Konstanta f(x) = ax + b.

    Returns:
        dict berisi string rumus untuk ditampilkan di UI.
    """
    c = b + G_CONST   # konstanta komposisi: E(x) = ax + c
    f_str = f"f(x) = {a}x + {b}" if b >= 0 else f"f(x) = {a}x - {abs(b)}"
    g_str = f"g(x) = x + {G_CONST}"
    comp_str = (
        f"(g ∘ f)(x) = g({a}x + {b}) = ({a}x + {b}) + {G_CONST} = {a}x + {c}"
        if c >= 0
        else f"(g ∘ f)(x) = g({a}x + {b}) = ({a}x + {b}) + {G_CONST} = {a}x - {abs(c)}"
    )
    enc_str = f"E(x) = {a}x + {c}" if c >= 0 else f"E(x) = {a}x - {abs(c)}"
    inv_str = f"D(y) = (y - {c}) / {a}" if c >= 0 else f"D(y) = (y + {abs(c)}) / {a}"
    return {
        "a": a,
        "b": b,
        "c": c,
        "g_const": G_CONST,
        "f_formula": f_str,
        "g_formula": g_str,
        "comp_formula": comp_str,
        "encrypt_formula": enc_str,
        "inv_formula": inv_str,
        "valid_range": "x ∈ {-26..0..26} → kapital, kecil, spasi",
    }
