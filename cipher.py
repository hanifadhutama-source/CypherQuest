"""
cipher.py - Modul Logika Matematika Inti CipherQuest

Materi:
- Fungsi linear f(x) = 2x + 1
- Fungsi linear g(x) = x + 2
- Komposisi fungsi (g o f)(x) = g(f(x)) = 2x + 3
- Invers fungsi D(x) = (x - 3) / 2
- Konversi A=1 ... Z=26
"""

from typing import Union, Tuple, Optional


def char_to_num(char: str) -> int:
    """
    Mengonversi satu huruf alfabet (A-Z atau a-z) menjadi angka (1-26).
    A/a = 1, B/b = 2, ..., Z/z = 26.
    Jika bukan alfabet, memunculkan ValueError.
    """
    if not isinstance(char, str) or len(char) != 1:
        raise ValueError("Input harus berupa satu karakter string.")
    
    char_upper = char.upper()
    if 'A' <= char_upper <= 'Z':
        return ord(char_upper) - ord('A') + 1
    raise ValueError(f"Karakter '{char}' tidak valid. Hanya alfabet A-Z yang didukung.")


def num_to_char(num: int, uppercase: bool = True) -> str:
    """
    Mengonversi angka 1-26 menjadi huruf alfabet.
    1 -> 'A', 26 -> 'Z'.
    Jika angka di luar rentang 1-26, memunculkan ValueError.
    """
    if not isinstance(num, int):
        raise ValueError("Input harus berupa bilangan bulat (integer).")
    if not (1 <= num <= 26):
        raise ValueError(f"Nilai {num} di luar rentang alfabet (1-26).")
    
    base_char = 'A' if uppercase else 'a'
    return chr(ord(base_char) + (num - 1))


def f(x: int) -> int:
    """
    Fungsi linear pertama:
    f(x) = 2x + 1
    """
    if not isinstance(x, (int, float)):
        raise TypeError("Input x harus berupa bilangan.")
    return 2 * x + 1


def g(x: int) -> int:
    """
    Fungsi linear kedua:
    g(x) = x + 2
    """
    if not isinstance(x, (int, float)):
        raise TypeError("Input x harus berupa bilangan.")
    return x + 2


def g_comp_f(x: int) -> int:
    """
    Fungsi komposisi (g o f)(x) = g(f(x)):
    g(f(x)) = g(2x + 1) = (2x + 1) + 2 = 2x + 3
    """
    return g(f(x))


def encrypt_val(x: int) -> int:
    """
    Fungsi enkripsi gabungan E(x) = (g o f)(x) = 2x + 3.
    Menggunakan komposisi g(f(x)) secara eksplisit.
    """
    return g_comp_f(x)


def inv_comp(y: Union[int, float]) -> float:
    """
    Fungsi invers dari komposisi E(x) = 2x + 3:
    y = 2x + 3
    x = 2y + 3
    x - 3 = 2y
    y = (x - 3) / 2
    D(x) = (x - 3) / 2
    """
    if not isinstance(y, (int, float)):
        raise TypeError("Input y harus berupa bilangan.")
    return (y - 3) / 2


def decrypt_val(y: int) -> int:
    """
    Mendekripsi nilai cipherteks y menggunakan fungsi invers D(y) = (y - 3) / 2.
    Melakukan validasi ketat:
    - y harus bilangan bulat
    - y harus bernilai ganjil
    - y harus berada dalam rentang [5, 55] (karena x dalam 1-26)
    - Hasil invers harus bilangan bulat 1-26
    """
    if not isinstance(y, int):
        raise ValueError(f"Nilai cipherteks '{y}' harus berupa bilangan bulat.")
    
    # Validasi rentang nilai enkripsi untuk x in [1, 26]: E(1)=5 s.d. E(26)=55
    if y < 5 or y > 55:
        raise ValueError(f"Nilai cipherteks {y} berada di luar batas valid (5 - 55).")
    
    # Validasi paritas ganjil karena E(x) = 2x + 3 selalu ganjil
    if y % 2 == 0:
        raise ValueError(f"Nilai cipherteks {y} tidak valid (bilangan genap tidak mungkin dihasilkan oleh 2x+3).")
    
    inv_result = inv_comp(y)
    
    # Periksa apakah hasil merupakan bilangan bulat murni
    if inv_result != int(inv_result):
        raise ValueError(f"Hasil invers {inv_result} bukan bilangan bulat.")
    
    orig_x = int(inv_result)
    if not (1 <= orig_x <= 26):
        raise ValueError(f"Hasil invers {orig_x} di luar rentang alfabet (1-26).")
    
    return orig_x


def validate_character_support(char: str) -> bool:
    """
    Memeriksa apakah karakter didukung oleh sistem (A-Z, a-z, spasi).
    """
    return char.isalpha() or char == ' '


def get_formula_metadata() -> dict:
    """
    Mengembalikan metadata informasi rumus untuk ditampilkan di UI.
    """
    return {
        "f_formula": "f(x) = 2x + 1",
        "g_formula": "g(x) = x + 2",
        "comp_formula": "(g \u2218 f)(x) = g(f(x)) = (2x + 1) + 2 = 2x + 3",
        "encrypt_formula": "E(x) = 2x + 3",
        "inv_formula": "D(x) = (x - 3) / 2",
        "valid_range": "x \u2208 [1, 26] \u2192 E(x) \u2208 [5, 55] (ganjil)"
    }
