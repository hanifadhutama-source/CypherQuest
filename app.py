"""
app.py - Aplikasi Utama Flask CipherQuest
CipherQuest — Decode the Message, Complete the Mission
Game Edukasi Kriptografi Matematika: Komposisi & Invers Fungsi
"""

import os
import uuid
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort
)

from config import Config
from database import (
    init_db, get_player_stats, get_missions_list,
    get_mission_for_session, regenerate_mission_question,
    submit_mission_answer, reset_progress
)
from cipher import get_formula_metadata, DEFAULT_A, DEFAULT_B
from encrypt import encrypt_message
from decrypt import decrypt_ciphertext

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.filters['chr'] = chr

# Inisialisasi Database saat aplikasi dijalankan
with app.app_context():
    try:
        init_db()
    except Exception as e:
        app.logger.warning("Inisialisasi database awal ditangguhkan: %s", str(e))


@app.before_request
def ensure_session_identity():
    """Memastikan setiap pengunjung memiliki session_id unik untuk progres game."""
    if 'player_id' not in session:
        session['player_id'] = uuid.uuid4().hex


@app.context_processor
def inject_global_game_data():
    """Menyediakan data statistik pemain dan metadata rumus default ke seluruh template."""
    player_id = session.get('player_id', '')
    stats = get_player_stats(player_id)
    return {
        "player_stats": stats,
        "formulas": get_formula_metadata()
    }


# ==========================================
# ROUTES UTAMA
# ==========================================

@app.route('/')
def index():
    """Halaman Beranda dengan Hero Section, Briefing Intelijen, dan Dashboard."""
    player_id = session.get('player_id', '')
    stats = get_player_stats(player_id)
    missions = get_missions_list(player_id)
    return render_template('index.html', stats=stats, missions=missions)


@app.route('/missions')
def missions():
    """Halaman Papan Misi."""
    player_id = session.get('player_id', '')
    missions_list = get_missions_list(player_id)
    stats = get_player_stats(player_id)
    return render_template('missions.html', missions=missions_list, stats=stats)


@app.route('/mission/<int:mission_id>', methods=['GET', 'POST'])
def mission_detail(mission_id: int):
    """Halaman Detail dan Pengerjaan Misi dengan Soal Dinamis Tersimpan."""
    player_id = session.get('player_id', '')
    
    # Ambil misi aktif untuk sesi pemain
    mission = get_mission_for_session(player_id, mission_id)
    if not mission:
        abort(404)

    # Cek status lock/unlock
    missions_list = get_missions_list(player_id)
    is_unlocked = False
    for m in missions_list:
        if m['id'] == mission_id:
            is_unlocked = m['is_unlocked']
            break

    if not is_unlocked:
        flash("Misi ini masih terkunci! Selesaikan misi sebelumnya terlebih dahulu.", "warning")
        return redirect(url_for('missions'))

    if request.method == 'POST':
        user_answer = request.form.get('answer', '')
        used_hint = request.form.get('used_hint', '0') == '1'

        if not user_answer.strip():
            flash("Silakan masukkan jawaban terlebih dahulu.", "danger")
            return redirect(url_for('mission_detail', mission_id=mission_id))

        result = submit_mission_answer(player_id, mission_id, user_answer, used_hint=used_hint)

        session['last_result'] = {
            "mission_id": mission_id,
            "mission_title": mission['title'],
            "mission_code": mission['code'],
            "user_answer": user_answer,
            "is_correct": result['is_correct'],
            "earned_score": result['earned_score'],
            "penalty": result['penalty'],
            "total_mission_score": result.get('total_mission_score', 0),
            "explanation": result['explanation'],
            "next_mission_id": mission_id + 1 if mission_id < 3 else None
        }
        return redirect(url_for('mission_result'))

    return render_template('mission_detail.html', mission=mission)


@app.route('/mission/<int:mission_id>/new-question', methods=['POST'])
def new_mission_question(mission_id: int):
    """Mengacak soal baru secara eksplisit atas permintaan pemain."""
    player_id = session.get('player_id', '')
    regenerate_mission_question(player_id, mission_id)
    flash("Markas Intelijen telah mengirimkan transmisi target baru untuk misi ini!", "info")
    return redirect(url_for('mission_detail', mission_id=mission_id))


@app.route('/mission/result')
def mission_result():
    """Halaman Menampilkan Hasil Evaluasi Misi."""
    result_data = session.get('last_result')
    if not result_data:
        return redirect(url_for('missions'))
    return render_template('result.html', result=result_data)


@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_lab():
    """Halaman Laboratorium Enkripsi Pesan dengan Parameter Kustom."""
    result = None
    input_text = ""
    
    # Ambil parameter kustom a dan b
    raw_a = request.form.get('param_a') or request.args.get('a') or str(DEFAULT_A)
    raw_b = request.form.get('param_b') or request.args.get('b') or str(DEFAULT_B)

    try:
        a_val = int(raw_a)
    except (ValueError, TypeError):
        a_val = DEFAULT_A

    try:
        b_val = int(raw_b)
    except (ValueError, TypeError):
        b_val = DEFAULT_B

    if request.method == 'POST':
        input_text = request.form.get('plaintext', '')
        result = encrypt_message(input_text, a=a_val, b=b_val)

    if request.method == 'GET' and request.args.get('demo') == 'aku':
        input_text = "AKU"
        a_val, b_val = DEFAULT_A, DEFAULT_B
        result = encrypt_message(input_text, a=a_val, b=b_val)

    formula_info = get_formula_metadata(a_val, b_val)
    return render_template(
        'encrypt.html',
        result=result,
        input_text=input_text,
        param_a=a_val,
        param_b=b_val,
        formula_info=formula_info
    )


@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_lab():
    """Halaman Laboratorium Dekripsi Pesan dengan Parameter Kustom dan Langkah Penurunan."""
    result = None
    input_text = ""

    # Ambil parameter kustom a dan b
    raw_a = request.form.get('param_a') or request.args.get('a') or str(DEFAULT_A)
    raw_b = request.form.get('param_b') or request.args.get('b') or str(DEFAULT_B)

    try:
        a_val = int(raw_a)
    except (ValueError, TypeError):
        a_val = DEFAULT_A

    try:
        b_val = int(raw_b)
    except (ValueError, TypeError):
        b_val = DEFAULT_B

    if request.method == 'POST':
        input_text = request.form.get('ciphertext', '')
        result = decrypt_ciphertext(input_text, a=a_val, b=b_val)

    if request.method == 'GET' and request.args.get('demo') == 'aku':
        input_text = "5 25 45"
        a_val, b_val = DEFAULT_A, DEFAULT_B
        result = decrypt_ciphertext(input_text, a=a_val, b=b_val)

    formula_info = get_formula_metadata(a_val, b_val)
    return render_template(
        'decrypt.html',
        result=result,
        input_text=input_text,
        param_a=a_val,
        param_b=b_val,
        formula_info=formula_info
    )


@app.route('/tutorial')
def tutorial():
    """Halaman Tutorial Materi Kriptografi, Komposisi Fungsi, dan Invers."""
    demo_enc = encrypt_message("AKU", a=DEFAULT_A, b=DEFAULT_B)
    demo_dec = decrypt_ciphertext("5 25 45", a=DEFAULT_A, b=DEFAULT_B)
    return render_template('tutorial.html', demo_enc=demo_enc, demo_dec=demo_dec)


@app.route('/reset-progress', methods=['POST'])
def reset_user_progress():
    """Mereset data progres permainan untuk sesi aktif."""
    player_id = session.get('player_id', '')
    reset_progress(player_id)
    if 'last_result' in session:
        session.pop('last_result')
    flash("Progres permainan berhasil direset. Silakan mulai kembali dari Misi 01.", "info")
    return redirect(url_for('missions'))


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('404.html', custom_message="Terjadi gangguan transmisi internal server (500)."), 500


if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', os.environ.get('HOST', '127.0.0.1'))
    port = int(os.environ.get('FLASK_RUN_PORT', os.environ.get('PORT', 5000)))
    debug = os.environ.get('FLASK_DEBUG', '0') in ('1', 'true', 'True')
    app.run(host=host, port=port, debug=debug)
