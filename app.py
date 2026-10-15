"""
app.py - Aplikasi Utama Flask CipherQuest
CipherQuest — Decode the Message, Complete the Mission
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
    get_mission_by_id, submit_mission_answer, reset_progress
)
from cipher import get_formula_metadata
from encrypt import encrypt_message
from decrypt import decrypt_ciphertext

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.filters['chr'] = chr

# Inisialisasi Database saat aplikasi dijalankan
with app.app_context():
    init_db()


@app.before_request
def ensure_session_identity():
    """Memastikan setiap pengunjung memiliki session_id unik untuk progres game."""
    if 'player_id' not in session:
        session['player_id'] = uuid.uuid4().hex


@app.context_processor
def inject_global_game_data():
    """Menyediakan data statistik pemain dan metadata rumus ke seluruh template."""
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
    """Halaman Detail dan Pengerjaan Misi."""
    player_id = session.get('player_id', '')
    missions_list = get_missions_list(player_id)
    
    # Cari misi yang sesuai
    mission = None
    for m in missions_list:
        if m['id'] == mission_id:
            mission = m
            break
            
    if not mission:
        abort(404)
        
    if not mission['is_unlocked']:
        flash("Misi ini masih terkunci! Selesaikan misi sebelumnya terlebih dahulu.", "warning")
        return redirect(url_for('missions'))
        
    if request.method == 'POST':
        user_answer = request.form.get('answer', '')
        used_hint = request.form.get('used_hint', '0') == '1'
        
        if not user_answer.strip():
            flash("Silakan masukkan jawaban terlebih dahulu.", "danger")
            return redirect(url_for('mission_detail', mission_id=mission_id))
            
        result = submit_mission_answer(player_id, mission_id, user_answer, used_hint=used_hint)
        
        # Simpan hasil sementara di sesi untuk ditampilkan di halaman hasil (PRG Pattern)
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


@app.route('/mission/result')
def mission_result():
    """Halaman Menampilkan Hasil Evaluasi Misi."""
    result_data = session.get('last_result')
    if not result_data:
        return redirect(url_for('missions'))
    return render_template('result.html', result=result_data)


@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_lab():
    """Halaman Laboratorium Enkripsi Pesan."""
    result = None
    input_text = ""
    
    if request.method == 'POST':
        input_text = request.form.get('plaintext', '')
        result = encrypt_message(input_text)
        
    # Dukungan demo query param ?demo=aku
    if request.method == 'GET' and request.args.get('demo') == 'aku':
        input_text = "AKU"
        result = encrypt_message(input_text)
        
    return render_template('encrypt.html', result=result, input_text=input_text)


@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_lab():
    """Halaman Laboratorium Dekripsi Pesan."""
    result = None
    input_text = ""
    
    if request.method == 'POST':
        input_text = request.form.get('ciphertext', '')
        result = decrypt_ciphertext(input_text)
        
    # Dukungan demo query param ?demo=aku
    if request.method == 'GET' and request.args.get('demo') == 'aku':
        input_text = "5 25 45"
        result = decrypt_ciphertext(input_text)
        
    return render_template('decrypt.html', result=result, input_text=input_text)


@app.route('/tutorial')
def tutorial():
    """Halaman Tutorial Materi Kriptografi, Komposisi Fungsi, dan Invers."""
    # Sediakan contoh live "AKU"
    demo_enc = encrypt_message("AKU")
    demo_dec = decrypt_ciphertext("5 25 45")
    return render_template('tutorial.html', demo_enc=demo_enc, demo_dec=demo_dec)


@app.route('/reset-progress', methods=['POST'])
def reset_user_progress():
    """Mereset data progres pemain pada sesi aktif."""
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
    # Memungkinkan binding host (misal 0.0.0.0 untuk HP pada Wi-Fi lokal) dan port melalui environment variable
    host = os.environ.get('FLASK_RUN_HOST', os.environ.get('HOST', '127.0.0.1'))
    port = int(os.environ.get('FLASK_RUN_PORT', os.environ.get('PORT', 5000)))
    debug = os.environ.get('FLASK_DEBUG', '0') in ('1', 'true', 'True')
    app.run(host=host, port=port, debug=debug)
