"""
tests/test_routes.py - Pengujian Integrasi Route dan Endpoint Flask
"""

import pytest
from app import app
from database import init_db, reset_progress


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_index_page(client):
    # Halaman beranda dapat dibuka
    response = client.get('/')
    assert response.status_code == 200
    assert b"CipherQuest" in response.data
    assert b"Misi Rahasia Menantimu" in response.data


def test_missions_page(client):
    # Halaman misi dapat dibuka
    response = client.get('/missions')
    assert response.status_code == 200
    assert b"Papan Misi" in response.data
    assert b"First Transmission" in response.data


def test_encrypt_page_get(client):
    # Halaman enkripsi dapat dibuka
    response = client.get('/encrypt')
    assert response.status_code == 200
    assert b"Laboratorium Enkripsi" in response.data
    assert b"f(x) = 2x + 1" in response.data


def test_encrypt_page_post_success(client):
    # Form enkripsi menghasilkan output yang benar
    response = client.post('/encrypt', data={'plaintext': 'AKU'})
    assert response.status_code == 200
    assert b"5 25 45" in response.data
    assert b"ENKRIPSI BERHASIL" in response.data


def test_encrypt_page_post_invalid(client):
    # Input tidak valid menampilkan pesan yang sesuai
    response = client.post('/encrypt', data={'plaintext': 'AKU 123!'})
    assert response.status_code == 200
    assert b"Karakter tidak didukung" in response.data


def test_decrypt_page_get(client):
    # Halaman dekripsi dapat dibuka
    response = client.get('/decrypt')
    assert response.status_code == 200
    assert b"Laboratorium Dekripsi" in response.data
    assert b"D(y) = (y - 3) / 2" in response.data


def test_decrypt_page_post_success(client):
    # Form dekripsi menghasilkan output yang benar
    response = client.post('/decrypt', data={'ciphertext': '5 25 45'})
    assert response.status_code == 200
    assert b"AKU" in response.data
    assert b"DEKRIPSI BERHASIL" in response.data


def test_decrypt_page_post_invalid(client):
    # Input tidak valid menampilkan pesan yang sesuai
    response = client.post('/decrypt', data={'ciphertext': '6 25 45'})
    assert response.status_code == 200
    assert b"Kode tidak valid" in response.data


def test_tutorial_page(client):
    # Halaman tutorial dapat dibuka
    response = client.get('/tutorial')
    assert response.status_code == 200
    assert b"Akademi Kriptografi" in response.data
    assert b"Plainteks" in response.data


def test_mission_flow(client):
    # Akses misi 1
    resp_m1 = client.get('/mission/1')
    assert resp_m1.status_code == 200
    assert b"First Transmission" in resp_m1.data

    # Misi 2 harusnya terkunci sebelum misi 1 selesai
    resp_m2_locked = client.get('/mission/2', follow_redirects=True)
    assert b"masih terkunci" in resp_m2_locked.data

    # Submit jawaban salah pada misi 1
    resp_wrong = client.post('/mission/1', data={'answer': '10 20 30', 'used_hint': '0'}, follow_redirects=True)
    assert resp_wrong.status_code == 200
    assert b"BELUM SESUAI" in resp_wrong.data

    # Submit jawaban benar untuk SPY dengan hint aktif (penalti 20 poin -> skor 80)
    resp_correct_hint = client.post('/mission/1', data={'answer': '41 35 53', 'used_hint': '1'}, follow_redirects=True)
    assert resp_correct_hint.status_code == 200
    assert b"BERHASIL DIPECAHKAN" in resp_correct_hint.data
    assert b"+80" in resp_correct_hint.data

    # Sekarang Misi 2 harusnya terbuka
    resp_m2_open = client.get('/mission/2')
    assert resp_m2_open.status_code == 200
    assert b"Double Encryption" in resp_m2_open.data

    # Mainkan ulang Misi 1 dengan skor sempurna (tanpa hint) -> skor update ke 100 tanpa duplikasi
    resp_replay = client.post('/mission/1', data={'answer': '41 35 53', 'used_hint': '0'}, follow_redirects=True)
    assert resp_replay.status_code == 200
    assert b"+100" in resp_replay.data

    # Cek statistik di beranda (skor total harus 100, bukan 180)
    resp_index = client.get('/')
    assert b"100" in resp_index.data


def test_demo_query_params(client):
    # Uji query param ?demo=aku pada enkripsi dan dekripsi
    resp_enc_demo = client.get('/encrypt?demo=aku')
    assert resp_enc_demo.status_code == 200
    assert b"5 25 45" in resp_enc_demo.data

    resp_dec_demo = client.get('/decrypt?demo=aku')
    assert resp_dec_demo.status_code == 200
    assert b"AKU" in resp_dec_demo.data


def test_reset_progress_endpoint(client):
    # Selesaikan misi 1
    client.post('/mission/1', data={'answer': '41 35 53', 'used_hint': '0'}, follow_redirects=True)
    
    # Panggil reset progress
    resp_reset = client.post('/reset-progress', follow_redirects=True)
    assert resp_reset.status_code == 200
    assert b"berhasil direset" in resp_reset.data

    # Misi 2 harus kembali terkunci
    resp_m2 = client.get('/mission/2', follow_redirects=True)
    assert b"masih terkunci" in resp_m2.data


def test_404_page(client):
    # Uji rute yang tidak terdaftar
    response = client.get('/halaman-rahasia-tidak-ada')
    assert response.status_code == 404
    assert b"KOORDINAT TIDAK DITEMUKAN" in response.data
