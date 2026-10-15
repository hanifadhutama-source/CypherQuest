"""
tests/test_decrypt.py - Pengujian Unit untuk Modul Dekripsi
"""

import pytest
from decrypt import decrypt_ciphertext


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


def test_decrypt_with_spaces():
    # Pemisah kata '|' diubah menjadi spasi
    res = decrypt_ciphertext("5 25 45 | 11 21 5")
    assert res["success"] is True
    assert res["plaintext"] == "AKU DIA"


def test_decrypt_out_of_range():
    # Angka di luar rentang ditolak (< 5 atau > 55)
    res_low = decrypt_ciphertext("3")
    assert res_low["success"] is False
    assert "Kode tidak valid" in res_low["error"]

    res_high = decrypt_ciphertext("57")
    assert res_high["success"] is False
    assert "Kode tidak valid" in res_high["error"]


def test_decrypt_even_number():
    # Angka genap ditolak untuk skema 2x+3
    res_even = decrypt_ciphertext("6 25 45")
    assert res_even["success"] is False
    assert "Kode tidak valid" in res_even["error"]


def test_decrypt_noninteger_or_malformed():
    # Noninteger, simbol aneh, atau input kosong ditolak
    res_float = decrypt_ciphertext("5.5 25")
    assert res_float["success"] is False
    assert "Kode tidak valid" in res_float["error"]

    res_str = decrypt_ciphertext("5 halo 45")
    assert res_str["success"] is False
    assert "Kode tidak valid" in res_str["error"]

    res_empty = decrypt_ciphertext("   ")
    assert res_empty["success"] is False
    assert "tidak boleh kosong" in res_empty["error"]
