"""
tests/test_cipher.py - Pengujian Unit untuk Logika Matematika Inti
"""

import pytest
from cipher import char_to_num, num_to_char, f, g, g_comp_f, encrypt_val, inv_comp, decrypt_val


def test_f_function():
    # 1. f(1) menghasilkan 3
    assert f(1) == 3
    assert f(11) == 23
    assert f(21) == 43


def test_g_function():
    # 2. g(3) menghasilkan 5
    assert g(3) == 5
    assert g(23) == 25
    assert g(43) == 45


def test_g_comp_f_examples():
    # 3. g(f(1)) menghasilkan 5
    assert g(f(1)) == 5
    # 4. g(f(11)) menghasilkan 25
    assert g(f(11)) == 25
    # 5. g(f(21)) menghasilkan 45
    assert g(f(21)) == 45


def test_composition_formula():
    # 6. Komposisi menghasilkan 2x + 3 untuk nilai uji
    for x in range(1, 27):
        assert g_comp_f(x) == 2 * x + 3
        assert encrypt_val(x) == 2 * x + 3


def test_inv_comp_examples():
    # 7. Invers dari 5 menghasilkan 1
    assert inv_comp(5) == 1.0
    assert decrypt_val(5) == 1

    # 8. Invers dari 25 menghasilkan 11
    assert inv_comp(25) == 11.0
    assert decrypt_val(25) == 11

    # 9. Invers dari 45 menghasilkan 21
    assert inv_comp(45) == 21.0
    assert decrypt_val(45) == 21


def test_roundtrip_all_alphabet():
    # 10. D(E(x)) = x untuk semua x bilangan bulat dari 1 sampai 26
    for x in range(1, 27):
        y = encrypt_val(x)
        orig_x = decrypt_val(y)
        assert orig_x == x


def test_char_conversion():
    assert char_to_num('A') == 1
    assert char_to_num('K') == 11
    assert char_to_num('U') == 21
    assert char_to_num('Z') == 26
    assert char_to_num('a') == 1
    assert char_to_num('z') == 26

    assert num_to_char(1) == 'A'
    assert num_to_char(11) == 'K'
    assert num_to_char(21) == 'U'
    assert num_to_char(26) == 'Z'

    with pytest.raises(ValueError):
        char_to_num('!')
    with pytest.raises(ValueError):
        num_to_char(0)
    with pytest.raises(ValueError):
        num_to_char(27)
