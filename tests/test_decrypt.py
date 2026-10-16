"""
tests/test_decrypt.py - Pengujian Unit untuk Modul Dekripsi CipherQuest
"""

import pytest
from decrypt import decrypt_ciphertext, get_derivation_steps


def test_decrypt_aku():
    # 5 25 45 menghasilkan AKU
    res = decrypt_ciphertext("5 25 45")
    assert res["success"] is True
    assert res["plaintext"] == "AKU"
    assert len(res["steps"]) == 3
    assert res["steps"][0]["inv_result"] == 1
    assert res["steps"][0]["char"] == "A"
    assert res["steps"][1]["inv_result"] == 11
    assert res["steps"][1]["char"] == "K"
    assert res["steps"][2]["inv_result"] == 21
    assert res["steps"][2]["char"] == "U"


def test_decrypt_with_spaces_token():
    # 5 25 45 3 11 21 5 menghasilkan "AKU DIA" (3 adalah spasi E(0))
    res = decrypt_ciphertext("5 25 45 3 11 21 5")
    assert res["success"] is True
    assert res["plaintext"] == "AKU DIA"


def test_decrypt_with_pipe_symbol():
    # Kompatibilitas simbol '|' sebagai pemisah kata
    res = decrypt_ciphertext("5 25 45 | 11 21 5")
    assert res["success"] is True
    assert res["plaintext"] == "AKU DIA"


def test_decrypt_lowercase():
    # 1 -19 -39 menghasilkan "aku"
    res = decrypt_ciphertext("1 -19 -39")
    assert res["success"] is True
    assert res["plaintext"] == "aku"


def test_decrypt_custom_parameters():
    # Parameter a=3, b=2 -> D(y) = (y - 4) / 3
    # 7 -> (7-4)/3 = 1 (A)
    # 4 -> (4-4)/3 = 0 (' ')
    # 10 -> (10-4)/3 = 2 (B)
    res = decrypt_ciphertext("7 4 10", a=3, b=2)
    assert res["success"] is True
    assert res["plaintext"] == "A B"


def test_decrypt_invalid_parameter_a_zero():
    res = decrypt_ciphertext("5 25 45", a=0, b=1)
    assert res["success"] is False
    assert "tidak boleh 0" in res["error"]


def test_decrypt_non_integer_result():
    # Nilai 6 dengan a=2, b=1 -> D(6) = (6-3)/2 = 1.5 (pecahan, bukan integer)
    res_even = decrypt_ciphertext("6 25 45")
    assert res_even["success"] is False
    assert "bukan integer" in res_even["error"]


def test_decrypt_out_of_range():
    # Nilai 60 dengan a=2, b=1 -> (60-3)/2 = 28.5 (pecahan)
    # Nilai 57 -> (57-3)/2 = 27 (> 26)
    res_high = decrypt_ciphertext("57")
    assert res_high["success"] is False
    assert "di luar rentang" in res_high["error"]


def test_decrypt_derivation_steps():
    steps = get_derivation_steps(a=2, b=1)
    assert len(steps) == 5
    assert "D(y)" in steps[4]["expr"]
