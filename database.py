"""
database.py - Pengelolaan Database SQLite untuk Progres dan Skor Pemain

Tanggung jawab:
- Menginisialisasi database SQLite di instance/cipherquest.db.
- Menyimpan progres pemain per sesi.
- Mengelola sistem skor: +100 poin jawaban benar, -20 pengurangan jika menggunakan petunjuk.
- Mencegah duplikasi skor saat halaman dimuat ulang (idempotent scoring).
- Mengunci/membuka akses misi berikutnya secara berurutan.
"""

import os
import sqlite3
import tempfile
from typing import Dict, List, Any, Optional

MISSIONS_DATA = [
    {
        "id": 1,
        "code": "MISI-01",
        "title": "First Transmission",
        "difficulty": "Mudah",
        "difficulty_badge": "badge-easy",
        "description": "Agen intelijen mencegat transmisi komunikasi awal berkode 'SPY'. Identifikasi nilai numerik setiap huruf (A=1 ... Z=26) dan lakukan enkripsi menggunakan fungsi linear E(x) = 2x + 3.",
        "learning_objective": "Mengenali konversi huruf menjadi angka A=1 s.d. Z=26 dan memahami proses enkripsi linear dasar.",
        "prompt_question": "Enkripsikan kata 'SPY' menjadi deretan angka cipherteks yang dipisahkan spasi.",
        "target_input": "SPY",
        "correct_answer": "41 35 53",
        "hint": "S=19 \u2192 2(19)+3 = 41; P=16 \u2192 2(16)+3 = 35; Y=25 \u2192 2(25)+3 = 53. Pisahkan angka dengan spasi tunggal.",
        "explanation": "Langkah konversi: S=19, P=16, Y=25. Substitusi E(x) = 2x + 3: E(19) = 2(19)+3 = 41; E(16) = 2(16)+3 = 35; E(25) = 2(25)+3 = 53. Cipherteks: 41 35 53."
    },
    {
        "id": 2,
        "code": "MISI-02",
        "title": "Double Encryption",
        "difficulty": "Menengah",
        "difficulty_badge": "badge-medium",
        "description": "Sindikat musuh menerapkan enkripsi berlapis menggunakan dua fungsi berturut-turut: f(x) = 2x + 1 lalu g(x) = x + 2. Buktikan hasil fungsi komposisi (g \u2218 f)(x) = 2x + 3 dengan mengenkripsi sandi kode 'AGENT'.",
        "learning_objective": "Memahami konsep komposisi fungsi g(f(x)) dan membuktikan keabsahan fungsi enkripsi gabungan (g \u2218 f)(x) = 2x + 3.",
        "prompt_question": "Enkripsikan kata sandi 'AGENT' menggunakan komposisi fungsi g(f(x)).",
        "target_input": "AGENT",
        "correct_answer": "5 17 13 31 43",
        "hint": "Gunakan E(x) = 2x + 3. Nilai: A=1 \u2192 5, G=7 \u2192 17, E=5 \u2192 13, N=14 \u2192 31, T=20 \u2192 43.",
        "explanation": "Komposisi (g \u2218 f)(x) = g(2x + 1) = (2x + 1) + 2 = 2x + 3. Untuk kata AGENT: A(1)\u21925, G(7)\u219217, E(5)\u219213, N(14)\u219231, T(20)\u219243. Hasil: 5 17 13 31 43."
    },
    {
        "id": 3,
        "code": "MISI-03",
        "title": "Reverse the Code",
        "difficulty": "Mahir",
        "difficulty_badge": "badge-hard",
        "description": "Transmisi rahasia markas musuh berhasil disadap dengan cipherteks: '41 13 9 39 13 43'. Gunakan rumus fungsi invers D(y) = (y - 3) / 2 untuk mendekripsi dan mengungkap pesan aslinya!",
        "learning_objective": "Menentukan rumus invers fungsi y = 2x + 3 menjadi D(y) = (y - 3)/2 dan memulihkan cipherteks kembali menjadi plainteks.",
        "prompt_question": "Dekomposisi dan dekripsikan cipherteks '41 13 9 39 13 43' menjadi kata plainteks.",
        "target_input": "41 13 9 39 13 43",
        "correct_answer": "SECRET",
        "hint": "Gunakan rumus invers D(y) = (y - 3) / 2. Contoh: 41 \u2192 (41-3)/2 = 19 (S); 13 \u2192 (13-3)/2 = 5 (E); 9 \u2192 (9-3)/2 = 3 (C).",
        "explanation": "Penerapan D(y) = (y - 3)/2: D(41)=19(S), D(13)=5(E), D(9)=3(C), D(39)=18(R), D(13)=5(E), D(43)=20(T). Pesan terungkap: SECRET."
    }
]


def get_db_path() -> str:
    """Mengembalikan path file database SQLite dengan fallback aman untuk serverless."""
    # 1. Lingkungan serverless Vercel / AWS Lambda
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('LAMBDA_TASK_ROOT'):
        return os.path.join(tempfile.gettempdir(), 'cipherquest.db')

    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    
    # 2. Coba direktori instance lokal jika writable
    try:
        os.makedirs(instance_dir, exist_ok=True)
        test_file = os.path.join(instance_dir, '.write_test')
        with open(test_file, 'w') as f:
            f.write('')
        os.remove(test_file)
        return os.path.join(instance_dir, 'cipherquest.db')
    except (OSError, IOError, PermissionError):
        # Fallback ke temp directory jika direktori proyek read-only
        return os.path.join(tempfile.gettempdir(), 'cipherquest.db')


def _raw_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel database jika belum ada."""
    conn = _raw_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_progress (
            session_id TEXT NOT NULL,
            mission_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'unlocked', -- 'unlocked', 'completed'
            score INTEGER NOT NULL DEFAULT 0,
            hints_used INTEGER NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_answer TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (session_id, mission_id)
        )
    """)
    conn.commit()
    conn.close()


def get_db_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    if not os.path.exists(db_path):
        init_db()
    return _raw_db_connection()


def get_player_stats(session_id: str) -> Dict[str, Any]:
    """
    Mengambil data statistik pemain:
    - Total skor (hanya skor tertinggi misi yang selesai)
    - Jumlah misi selesai
    - Total misi
    - Persentase progres
    - Misi terakhir yang aktif
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mission_id, status, score, hints_used, attempts, updated_at
        FROM player_progress
        WHERE session_id = ?
        ORDER BY mission_id ASC
    """, (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    progress_map = {row['mission_id']: dict(row) for row in rows}
    
    total_score = sum(p['score'] for p in progress_map.values() if p['status'] == 'completed')
    completed_count = sum(1 for p in progress_map.values() if p['status'] == 'completed')
    total_missions = len(MISSIONS_DATA)
    progress_pct = int((completed_count / total_missions) * 100) if total_missions > 0 else 0
    
    last_mission = None
    for m in reversed(MISSIONS_DATA):
        mid = m['id']
        if mid in progress_map and progress_map[mid]['status'] == 'completed':
            last_mission = m['title']
            break
            
    if not last_mission:
        last_mission = "Misi 01 (Belum Dimulai)"
        
    return {
        "total_score": total_score,
        "completed_count": completed_count,
        "total_missions": total_missions,
        "progress_pct": progress_pct,
        "last_mission": last_mission
    }


def get_missions_list(session_id: str) -> List[Dict[str, Any]]:
    """
    Mengembalikan daftar semua misi dengan status terkini pemain:
    Misi 1 terbuka secara default.
    Misi n terbuka jika misi n-1 sudah 'completed'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mission_id, status, score, hints_used, attempts, last_answer
        FROM player_progress
        WHERE session_id = ?
    """, (session_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    progress_map = {row['mission_id']: dict(row) for row in rows}
    
    missions_result = []
    prev_completed = True  # Misi 1 selalu terbuka
    
    for m in MISSIONS_DATA:
        mid = m['id']
        m_copy = dict(m)
        
        user_prog = progress_map.get(mid)
        
        if user_prog and user_prog['status'] == 'completed':
            m_copy['status'] = 'completed'
            m_copy['status_label'] = 'Selesai'
            m_copy['is_unlocked'] = True
            m_copy['score'] = user_prog['score']
            m_copy['hints_used'] = user_prog['hints_used']
            m_copy['attempts'] = user_prog['attempts']
            prev_completed = True
        elif prev_completed:
            m_copy['status'] = 'available'
            m_copy['status_label'] = 'Tersedia'
            m_copy['is_unlocked'] = True
            m_copy['score'] = user_prog['score'] if user_prog else 0
            m_copy['hints_used'] = user_prog['hints_used'] if user_prog else 0
            m_copy['attempts'] = user_prog['attempts'] if user_prog else 0
            prev_completed = False
        else:
            m_copy['status'] = 'locked'
            m_copy['status_label'] = 'Terkunci'
            m_copy['is_unlocked'] = False
            m_copy['score'] = 0
            m_copy['hints_used'] = 0
            m_copy['attempts'] = 0
            prev_completed = False
            
        missions_result.append(m_copy)
        
    return missions_result


def get_mission_by_id(mission_id: int) -> Optional[Dict[str, Any]]:
    """Mengambil definisi misi berdasarkan ID."""
    for m in MISSIONS_DATA:
        if m['id'] == mission_id:
            return dict(m)
    return None


def submit_mission_answer(session_id: str, mission_id: int, user_answer: str, used_hint: bool = False) -> Dict[str, Any]:
    """
    Memvalidasi jawaban misi pemain dan menyimpan progres:
    - Aturan skor:
      - Benar: +100 poin (jika pakai hint, dikurangi 20 menjadi 80 poin)
      - Salah: 0 poin (tidak menambah skor)
    - Anti-duplikasi skor:
      - Jika misi sudah pernah selesai, hanya update jika skor baru lebih tinggi dari skor lama.
    """
    mission = get_mission_by_id(mission_id)
    if not mission:
        return {
            "success": False,
            "error": "Misi tidak ditemukan."
        }
    
    # Normalisasi jawaban
    norm_user = " ".join(user_answer.strip().upper().split())
    norm_correct = " ".join(mission['correct_answer'].strip().upper().split())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT status, score, hints_used, attempts
        FROM player_progress
        WHERE session_id = ? AND mission_id = ?
    """, (session_id, mission_id))
    
    current_record = cursor.fetchone()
    current_score = current_record['score'] if current_record else 0
    current_attempts = current_record['attempts'] if current_record else 0
    was_completed = current_record and current_record['status'] == 'completed'
    
    is_correct = (norm_user == norm_correct)
    
    if is_correct:
        base_score = 100
        penalty = 20 if used_hint else 0
        new_earned_score = max(0, base_score - penalty)
        
        # Skor akhir adalah skor tertinggi yang diperoleh pemain untuk misi ini
        final_score = max(current_score, new_earned_score)
        
        cursor.execute("""
            INSERT INTO player_progress (session_id, mission_id, status, score, hints_used, attempts, last_answer, updated_at)
            VALUES (?, ?, 'completed', ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(session_id, mission_id) DO UPDATE SET
                status = 'completed',
                score = excluded.score,
                hints_used = excluded.hints_used,
                attempts = attempts + 1,
                last_answer = excluded.last_answer,
                updated_at = CURRENT_TIMESTAMP
        """, (session_id, mission_id, final_score, 1 if used_hint else 0, current_attempts + 1, norm_user))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "is_correct": True,
            "earned_score": new_earned_score,
            "total_mission_score": final_score,
            "penalty": penalty,
            "explanation": mission['explanation'],
            "mission": mission
        }
    else:
        # Jawaban salah: update attempts tanpa menambah skor
        cursor.execute("""
            INSERT INTO player_progress (session_id, mission_id, status, score, hints_used, attempts, last_answer, updated_at)
            VALUES (?, ?, 'unlocked', ?, ?, 1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(session_id, mission_id) DO UPDATE SET
                attempts = attempts + 1,
                last_answer = excluded.last_answer,
                updated_at = CURRENT_TIMESTAMP
        """, (session_id, mission_id, current_score, 1 if used_hint else 0, norm_user))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "is_correct": False,
            "earned_score": 0,
            "penalty": 0,
            "explanation": "Jawaban belum tepat. Periksa kembali langkah konversi atau rumus yang digunakan.",
            "mission": mission
        }


def reset_progress(session_id: str):
    """Mereset progres permainan untuk sesi saat ini."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM player_progress WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
