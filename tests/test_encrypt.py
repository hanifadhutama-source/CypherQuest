"""
tests/test_encrypt.py - Pengujian Unit untuk Modul Enkripsi
"""

import pytest
from encrypt import encrypt_message


def test_encrypt_aku():
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
    # Huruf kecil ditangani sesuai aturan (case insensitive)
    res = encrypt_message("aku")
    assert res["success"] is True
    assert res["ciphertext"] == "5 25 45"


def test_encrypt_with_spaces():
    # Spasi dipertahankan (sebagai pemisah kata '|')
    res = encrypt_message("AKU DIA")
    assert res["success"] is True
    # D = 4 -> 2(4)+3 = 11
    # I = 9 -> 2(9)+3 = 21
    # A = 1 -> 2(1)+3 = 5
    assert res["ciphertext"] == "5 25 45 | 11 21 5"


def test_encrypt_empty_input():
    # Input kosong ditolak
    res_empty = encrypt_message("")
    assert res_empty["success"] is False
    assert "tidak boleh kosong" in res_empty["error"]

    res_spaces = encrypt_message("   ")
    assert res_spaces["success"] is False
    assert "tidak boleh kosong" in res_spaces["error"]


def test_encrypt_unsupported_characters():
    # Karakter yang tidak didukung ditangani dengan jelas
    res = encrypt_message("AKU 123!")
    assert res["success"] is False
    assert "tidak didukung" in res["error"]
