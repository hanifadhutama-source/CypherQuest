"""
tests/test_routes.py - Pengujian Integrasi Route, Endpoint Flask, dan Soal Dinamis
"""

import pytest
from app import app
from database import init_db, reset_progress, get_mission_for_session


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"CipherQuest" in response.data
    assert b"Misi Rahasia Menantimu" in response.data


def test_missions_page(client):
    response = client.get('/missions')
    assert response.status_code == 200
    assert b"Papan Misi" in response.data
    assert b"First Transmission" in response.data


def test_encrypt_page_get(client):
    response = client.get('/encrypt')
    assert response.status_code == 200
    assert b"Laboratorium Enkripsi" in response.data
    assert b"PARAMETER FUNGSI" in response.data


def test_encrypt_page_post_success(client):
    response = client.post('/encrypt', data={'plaintext': 'AKU', 'param_a': '2', 'param_b': '1'})
    assert response.status_code == 200
    assert b"5 25 45" in response.data
    assert b"ENKRIPSI BERHASIL" in response.data


def test_encrypt_page_post_custom_params(client):
    # a=3, b=2 -> A=1 -> 3(1)+4 = 7
    response = client.post('/encrypt', data={'plaintext': 'A', 'param_a': '3', 'param_b': '2'})
    assert response.status_code == 200
    assert b"7" in response.data


def test_encrypt_page_post_invalid(client):
    response = client.post('/encrypt', data={'plaintext': 'AKU 123!'})
    assert response.status_code == 200
    assert b"Karakter tidak didukung" in response.data


def test_decrypt_page_get(client):
    response = client.get('/decrypt')
    assert response.status_code == 200
    assert b"Laboratorium Dekripsi" in response.data
    assert b"FUNGSI INVERS" in response.data


def test_decrypt_page_post_success(client):
    response = client.post('/decrypt', data={'ciphertext': '5 25 45', 'param_a': '2', 'param_b': '1'})
    assert response.status_code == 200
    assert b"AKU" in response.data
    assert b"DEKRIPSI BERHASIL" in response.data
    assert b"URUTAN PENURUNAN MATEMATIS" in response.data


def test_decrypt_page_post_invalid(client):
    response = client.post('/decrypt', data={'ciphertext': '6 25 45'})
    assert response.status_code == 200
    assert b"Gagal Melakukan Dekripsi" in response.data


def test_tutorial_page(client):
    response = client.get('/tutorial')
    assert response.status_code == 200
    assert b"Akademi Kriptografi" in response.data
    assert b"Plainteks" in response.data


def test_mission_dynamic_persistence_and_flow(client):
    # Buat session identity
    with client.session_transaction() as sess:
        sess['player_id'] = 'test_agent_007'
    reset_progress('test_agent_007')

    # Akses misi 1
    resp_m1 = client.get('/mission/1')
    assert resp_m1.status_code == 200
    assert b"First Transmission" in resp_m1.data

    # Ambil soal yang tersimpan untuk sesi pemain ini
    m1_data = get_mission_for_session('test_agent_007', 1)
    assert m1_data is not None
    target_q = m1_data['target_input']
    correct_ans = m1_data['correct_answer']

    # Refresh misi 1: Soal HARUS TETAP SAMA (tidak berubah karena refresh)
    resp_refresh = client.get('/mission/1')
    assert target_q.encode() in resp_refresh.data

    # Misi 2 harus terkunci
    resp_m2_locked = client.get('/mission/2', follow_redirects=True)
    assert b"masih terkunci" in resp_m2_locked.data

    # Submit jawaban salah: Soal HARUS TETAP SAMA
    resp_wrong = client.post('/mission/1', data={'answer': '999 888', 'used_hint': '0'}, follow_redirects=True)
    assert resp_wrong.status_code == 200
    assert b"BELUM SESUAI" in resp_wrong.data

    resp_m1_after_wrong = client.get('/mission/1')
    assert target_q.encode() in resp_m1_after_wrong.data

    # Submit jawaban benar sesuai soal dinamis aktif
    resp_correct = client.post('/mission/1', data={'answer': correct_ans, 'used_hint': '0'}, follow_redirects=True)
    assert resp_correct.status_code == 200
    assert b"BERHASIL DIPECAHKAN" in resp_correct.data
    assert b"+100" in resp_correct.data

    # Sekarang Misi 2 harus terbuka
    resp_m2_open = client.get('/mission/2')
    assert resp_m2_open.status_code == 200
    assert b"Double Encryption" in resp_m2_open.data


def test_mission_new_question_generator(client):
    with client.session_transaction() as sess:
        sess['player_id'] = 'test_agent_regenerate'

    client.get('/mission/1')
    m1_first = get_mission_for_session('test_agent_regenerate', 1)
    
    # Request soal baru eksplisit
    resp_new = client.post('/mission/1/new-question', follow_redirects=True)
    assert resp_new.status_code == 200
    assert b"target baru" in resp_new.data


def test_demo_query_params(client):
    resp_enc_demo = client.get('/encrypt?demo=aku')
    assert resp_enc_demo.status_code == 200
    assert b"5 25 45" in resp_enc_demo.data

    resp_dec_demo = client.get('/decrypt?demo=aku')
    assert resp_dec_demo.status_code == 200
    assert b"AKU" in resp_dec_demo.data


def test_reset_progress_endpoint(client):
    with client.session_transaction() as sess:
        sess['player_id'] = 'test_agent_reset'

    m1 = get_mission_for_session('test_agent_reset', 1)
    client.post('/mission/1', data={'answer': m1['correct_answer'], 'used_hint': '0'}, follow_redirects=True)

    resp_reset = client.post('/reset-progress', follow_redirects=True)
    assert resp_reset.status_code == 200
    assert b"berhasil direset" in resp_reset.data

    # Misi 2 harus kembali terkunci
    resp_m2 = client.get('/mission/2', follow_redirects=True)
    assert b"masih terkunci" in resp_m2.data


def test_404_page(client):
    response = client.get('/halaman-rahasia-tidak-ada')
    assert response.status_code == 404
    assert b"KOORDINAT TIDAK DITEMUKAN" in response.data
