"""
tests/test_encrypt.py - Pengujian Unit untuk Modul Enkripsi CipherQuest
"""

import pytest
from encrypt import encrypt_message


def test_encrypt_capital_aku():
    # AKU menghasilkan 5 25 45
    res = encrypt_message("AKU")
    assert res["success"] is True
    assert res["ciphertext"] == "5 25 45"
    assert res["tokens"] == ["5", "25", "45"]
    assert len(res["steps"]) == 3
    assert res["steps"][0]["final_val"] == 5
    assert res["steps"][1]["final_val"] == 25
    assert res["steps"][2]["final_val"] == 45


def test_encrypt_lowercase():
    # Huruf kecil: a=-1 -> 2(-1)+3 = 1; k=-11 -> 2(-11)+3 = -19; u=-21 -> 2(-21)+3 = -39
    res = encrypt_message("aku")
    assert res["success"] is True
    assert res["ciphertext"] == "1 -19 -39"


def test_encrypt_with_spaces():
    # Spasi adalah token x=0 -> E(0) = 3
    # AKU DIA -> 5 25 45 3 11 21 5
    res = encrypt_message("AKU DIA")
    assert res["success"] is True
    assert res["ciphertext"] == "5 25 45 3 11 21 5"
    assert res["tokens"][3] == "3"


def test_encrypt_custom_parameters():
    # Parameter a=3, b=2 -> E(x) = 3x + 4
    # A=1 -> 3(1)+4 = 7
    # Spasi=0 -> 3(0)+4 = 4
    # B=2 -> 3(2)+4 = 10
    res = encrypt_message("A B", a=3, b=2)
    assert res["success"] is True
    assert res["ciphertext"] == "7 4 10"


def test_encrypt_invalid_parameter_a_zero():
    # a=0 ditolak karena f(x)=b tidak memiliki invers
    res = encrypt_message("AKU", a=0, b=1)
    assert res["success"] is False
    assert "tidak boleh 0" in res["error"]


def test_encrypt_empty_input():
    res_empty = encrypt_message("")
    assert res_empty["success"] is False
    assert "tidak boleh kosong" in res_empty["error"]

    res_spaces = encrypt_message("   ")
    assert res_spaces["success"] is False
    assert "tidak boleh kosong" in res_spaces["error"]


def test_encrypt_unsupported_characters():
    res = encrypt_message("AKU 123!")
    assert res["success"] is False
    assert "tidak didukung" in res["error"]
