"""
tests/test_cipher.py - Pengujian Unit untuk Logika Matematika Inti CipherQuest
"""

import pytest
from cipher import (
    char_to_num, num_to_char, f, g, g_comp_f, encrypt_val, inv_comp,
    decrypt_val, get_formula_metadata
)


def test_f_function_default():
    # f(x) = 2x + 1
    assert f(1) == 3
    assert f(11) == 23
    assert f(21) == 43
    assert f(0) == 1
    assert f(-1) == -1


def test_f_function_custom_params():
    # f(x) = 3x - 2
    assert f(2, a=3, b=-2) == 4
    assert f(0, a=3, b=-2) == -2


def test_g_function():
    # g(x) = x + 2 (konstanta kurikulum tetap)
    assert g(3) == 5
    assert g(23) == 25
    assert g(43) == 45
    assert g(0) == 2
    assert g(-1) == 1


def test_g_comp_f_examples():
    # g(f(x)) = (2x + 1) + 2 = 2x + 3
    assert g_comp_f(1) == 5
    assert g_comp_f(11) == 25
    assert g_comp_f(21) == 45
    assert g_comp_f(0) == 3       # Spasi
    assert g_comp_f(-1) == 1      # Huruf 'a'


def test_composition_formula():
    for x in range(-26, 27):
        assert g_comp_f(x) == 2 * x + 3
        assert encrypt_val(x) == 2 * x + 3


def test_inv_comp_examples():
    # D(y) = (y - 3) / 2
    assert inv_comp(5) == 1.0
    assert decrypt_val(5) == 1    # 'A'

    assert inv_comp(25) == 11.0
    assert decrypt_val(25) == 11  # 'K'

    assert inv_comp(45) == 21.0
    assert decrypt_val(45) == 21  # 'U'

    assert inv_comp(3) == 0.0
    assert decrypt_val(3) == 0    # ' ' (spasi)

    assert inv_comp(1) == -1.0
    assert decrypt_val(1) == -1   # 'a'


def test_roundtrip_all_characters_range():
    # D(E(x)) = x untuk seluruh rentang x in [-26..0..26]
    for x in range(-26, 27):
        y = encrypt_val(x)
        orig_x = decrypt_val(y)
        assert orig_x == x


def test_roundtrip_custom_params():
    # Uji roundtrip dengan parameter kustom: a=3, b=5 -> E(x) = 3x + 7
    a, b = 3, 5
    for x in range(-26, 27):
        y = encrypt_val(x, a=a, b=b)
        orig_x = decrypt_val(y, a=a, b=b)
        assert orig_x == x


def test_char_conversion():
    # Kapital: A=1 s.d. Z=26
    assert char_to_num('A') == 1
    assert char_to_num('K') == 11
    assert char_to_num('U') == 21
    assert char_to_num('Z') == 26

    # Kecil: a=-1 s.d. z=-26
    assert char_to_num('a') == -1
    assert char_to_num('k') == -11
    assert char_to_num('u') == -21
    assert char_to_num('z') == -26

    # Spasi: 0
    assert char_to_num(' ') == 0

    # Kebalikan num_to_char
    assert num_to_char(1) == 'A'
    assert num_to_char(11) == 'K'
    assert num_to_char(21) == 'U'
    assert num_to_char(26) == 'Z'
    assert num_to_char(-1) == 'a'
    assert num_to_char(-11) == 'k'
    assert num_to_char(-21) == 'u'
    assert num_to_char(-26) == 'z'
    assert num_to_char(0) == ' '

    # Error handling
    with pytest.raises(ValueError):
        char_to_num('!')
    with pytest.raises(ValueError):
        char_to_num('1')
    with pytest.raises(ValueError):
        num_to_char(27)
    with pytest.raises(ValueError):
        num_to_char(-27)


def test_formula_metadata():
    meta = get_formula_metadata(a=2, b=1)
    assert meta["a"] == 2
    assert meta["b"] == 1
    assert meta["c"] == 3
    assert "2x + 1" in meta["f_formula"]
    assert "D(y) = (y - 3) / 2" in meta["inv_formula"]
