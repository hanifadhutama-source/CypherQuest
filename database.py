"""
database.py - Pengelolaan Database SQLite untuk Progres, Skor, dan Soal Misi Dinamis

Tanggung jawab:
- Menginisialisasi database SQLite di instance/cipherquest.db atau fallback /tmp untuk Vercel.
- Menghasilkan soal misi secara dinamis (2-3 kata untuk umum, 4 kata untuk soal langka).
- Menyimpan soal yang sedang dikerjakan per sesi pemain sehingga tidak berubah saat refresh atau retry.
- Menyimpan progres pemain per sesi dan skor (idempotent, tanpa duplikasi).
- Mengunci/membuka akses misi berikutnya secara berurutan.
"""

import os
import random
import sqlite3
import tempfile
from typing import Dict, List, Any, Optional, Tuple

from encrypt import encrypt_message
from cipher import DEFAULT_A, DEFAULT_B

# ─── Bank Kata Intelijen Kriptografi ──────────────────────────────────────────
WORD_BANK_1 = [
    "KODE", "AGEN", "MISI", "SANDI", "KUNCI", "SINYAL", "DATA", "RADAR",
    "TARGET", "BERKAS", "KAPAL", "SATELIT", "VEKTOR", "MATRIX", "LOGIKA",
    "OPERASI", "PATROLI", "INTEL", "CYBER", "SISTEM", "PASUKAN", "JALUR"
]

WORD_BANK_2 = [
    "RAHASIA", "AKTIF", "AMAN", "GELAP", "CEPAT", "SENYAP", "VALID", "TEPAT",
    "UTAMA", "SIAGA", "FOKUS", "LINEAR", "INVERS", "DIGITAL", "KOREKSI",
    "TERKUNCI", "TERBUKA", "KHUSUS", "TAKTIK", "STRATEGIS", "OPTIMAL"
]

WORD_BANK_3 = [
    "KITA", "KOTA", "BUMI", "PUNCAK", "MALAM", "SUBUH", "SIANG", "BARAT",
    "TIMUR", "PUSAT", "ALPHA", "BETA", "DELTA", "OMEGA", "GARIS", "TITIK"
]

WORD_BANK_4 = [
    "SEKARANG", "SEGERA", "BERSAMA", "SELAMAT", "SEMPURNA", "TERAKHIR", "MUTLAK", "BERHASIL"
]


def generate_random_message() -> Tuple[str, int, bool]:
    """
    Menghasilkan kalimat sandi secara dinamis dengan aturan:
    - 2 kata: peluang ~44% (soal biasa)
    - 3 kata: peluang ~44% (soal biasa)
    - 4 kata: peluang ~12% (soal langka / rare intel mission)
    Mengembalikan (pesan_teks, jumlah_kata, is_rare).
    """
    r = random.random()
    w1 = random.choice(WORD_BANK_1)
    w2 = random.choice(WORD_BANK_2)

    if r < 0.12:
        # Soal langka 4 kata
        w3 = random.choice(WORD_BANK_3)
        w4 = random.choice(WORD_BANK_4)
        words = [w1, w2, w3, w4]
        is_rare = True
    elif r < 0.56:
        # Soal biasa 2 kata
        words = [w1, w2]
        is_rare = False
    else:
        # Soal biasa 3 kata
        w3 = random.choice(WORD_BANK_3)
        words = [w1, w2, w3]
        is_rare = False

    return " ".join(words), len(words), is_rare


def generate_mission_data(mission_id: int) -> Dict[str, Any]:
    """
    Membuat soal baru secara matematis untuk misi tertentu.
    - Misi 1: Enkripsi linear dasar E(x) = 2x + 3
    - Misi 2: Komposisi fungsi (g o f)(x) = 2x + 3
    - Misi 3: Dekripsi invers D(y) = (y - 3) / 2
    """
    message, word_count, is_rare = generate_random_message()
    a, b = DEFAULT_A, DEFAULT_B  # a=2, b=1 -> E(x) = 2x+3

    enc_res = encrypt_message(message, a=a, b=b)
    ciphertext = enc_res["ciphertext"]

    rare_tag = " [SOAL LANGKA // 4 KATA]" if is_rare else ""

    if mission_id == 1:
        # Enkripsi Pesan Linear
        prompt_q = f"Enkripsikan pesan rahasia '{message}' menjadi deretan angka cipherteks yang dipisahkan spasi."
        hint = (
            f"Setiap huruf dikonversi: A=1 s.d. Z=26, dan SPASI = 0. "
            f"Gunakan rumus E(x) = 2x + 3. Contoh: SPASI bernilai x=0 sehingga E(0) = 2(0)+3 = 3."
        )
        explanation = (
            f"Langkah enkripsi untuk '{message}':\n"
            f"1. Konversi karakter ke nilai x (A-Z = 1..26, spasi = 0).\n"
            f"2. Terapkan E(x) = 2x + 3 ke setiap nilai x.\n"
            f"3. Hasil cipherteks yang benar: {ciphertext}."
        )
        return {
            "target_input": message,
            "correct_answer": ciphertext,
            "prompt_question": prompt_q,
            "hint": hint,
            "explanation": explanation,
            "param_a": a,
            "param_b": b,
            "word_count": word_count,
            "is_rare": is_rare,
            "rare_tag": rare_tag
        }

    elif mission_id == 2:
        # Komposisi Fungsi (g o f)(x)
        prompt_q = f"Enkripsikan pesan rahasia '{message}' menggunakan komposisi fungsi f(x) = 2x + 1 dan g(x) = x + 2."
        hint = (
            f"Komposisi: (g ∘ f)(x) = g(2x + 1) = (2x + 1) + 2 = 2x + 3. "
            f"Spasi bernilai x = 0 → E(0) = 3. Setiap huruf kapital A=1 s.d. Z=26."
        )
        explanation = (
            f"Tahapan komposisi fungsi untuk '{message}':\n"
            f"1. Tahap 1: f(x) = 2x + 1.\n"
            f"2. Tahap 2: g(f(x)) = (2x + 1) + 2 = 2x + 3.\n"
            f"3. Substitusi setiap karakter (spasi = 0) menghasilkan cipherteks: {ciphertext}."
        )
        return {
            "target_input": message,
            "correct_answer": ciphertext,
            "prompt_question": prompt_q,
            "hint": hint,
            "explanation": explanation,
            "param_a": a,
            "param_b": b,
            "word_count": word_count,
            "is_rare": is_rare,
            "rare_tag": rare_tag
        }

    else:
        # Misi 3: Dekripsi Invers D(y) = (y - 3) / 2
        prompt_q = f"Dekomposisi dan dekripsikan deretan angka cipherteks '{ciphertext}' menjadi kalimat plainteks aslinya."
        hint = (
            f"Gunakan fungsi invers D(y) = (y - 3) / 2. "
            f"Token dengan nilai 3 menghasilkan D(3) = 0 yang merupakan SPASI pemisah kata."
        )
        explanation = (
            f"Langkah dekripsi cipherteks '{ciphertext}':\n"
            f"1. Kurangi setiap token y dengan 3: (y - 3).\n"
            f"2. Bagi hasilnya dengan 2: x = (y - 3) / 2.\n"
            f"3. Petakan x ke huruf (1..26 → A..Z, 0 → spasi).\n"
            f"Pesan asli terungkap: '{message}'."
        )
        return {
            "target_input": ciphertext,
            "correct_answer": message,
            "prompt_question": prompt_q,
            "hint": hint,
            "explanation": explanation,
            "param_a": a,
            "param_b": b,
            "word_count": word_count,
            "is_rare": is_rare,
            "rare_tag": rare_tag
        }


MISSIONS_DATA = [
    {
        "id": 1,
        "code": "MISI-01",
        "title": "First Transmission",
        "difficulty": "Mudah",
        "difficulty_badge": "badge-easy",
        "description": "Agen intelijen mencegat transmisi komunikasi yang perlu diamankan. Identifikasi nilai numerik setiap huruf (A=1 ... Z=26, spasi=0) dan lakukan enkripsi menggunakan fungsi linear E(x) = 2x + 3.",
        "learning_objective": "Mengenali konversi huruf menjadi angka A=1 s.d. Z=26, pemetaan spasi=0, dan memahami proses enkripsi linear dasar.",
        "prompt_question": "Enkripsikan pesan rahasia menjadi deretan angka cipherteks yang dipisahkan spasi.",
        "target_input": "KODE RAHASIA",
        "correct_answer": "23 33 11 13 3 39 5 19 5 41 21 5",
        "hint": "Gunakan E(x) = 2x + 3. SPASI bernilai x=0 sehingga E(0)=3. Pisahkan angka dengan spasi tunggal.",
        "explanation": "Substitusi nilai karakter ke E(x) = 2x + 3."
    },
    {
        "id": 2,
        "code": "MISI-02",
        "title": "Double Encryption",
        "difficulty": "Menengah",
        "difficulty_badge": "badge-medium",
        "description": "Sindikat musuh menerapkan enkripsi berlapis menggunakan dua fungsi berturut-turut: f(x) = 2x + 1 lalu g(x) = x + 2. Buktikan hasil fungsi komposisi (g ∘ f)(x) = 2x + 3 dengan mengenkripsi sandi kode target.",
        "learning_objective": "Memahami konsep komposisi fungsi g(f(x)) dan membuktikan keabsahan fungsi enkripsi gabungan (g ∘ f)(x) = 2x + 3.",
        "prompt_question": "Enkripsikan kata sandi menggunakan komposisi fungsi g(f(x)).",
        "target_input": "AGEN SIAGA MALAM",
        "correct_answer": "5 17 13 31 3 41 21 5 17 5 3 29 5 27 5 29",
        "hint": "Komposisi (g ∘ f)(x) = 2x + 3. Spasi memiliki nilai x=0 sehingga E(0)=3.",
        "explanation": "Komposisi (g ∘ f)(x) = g(2x + 1) = (2x + 1) + 2 = 2x + 3."
    },
    {
        "id": 3,
        "code": "MISI-03",
        "title": "Reverse the Code",
        "difficulty": "Mahir",
        "difficulty_badge": "badge-hard",
        "description": "Transmisi rahasia markas musuh berhasil disadap berupa deretan angka cipherteks. Gunakan rumus fungsi invers D(y) = (y - 3) / 2 untuk mendekripsi dan mengungkap pesan aslinya!",
        "learning_objective": "Menentukan rumus invers fungsi y = 2x + 3 menjadi D(y) = (y - 3)/2 dan memulihkan cipherteks kembali menjadi plainteks.",
        "prompt_question": "Dekomposisi dan dekripsikan cipherteks menjadi kalimat plainteks.",
        "target_input": "25 45 31 9 21 3 35 45 41 5 43",
        "correct_answer": "KUNCI PUSAT",
        "hint": "Gunakan rumus invers D(y) = (y - 3) / 2. Token bernilai 3 adalah spasi.",
        "explanation": "Penerapan D(y) = (y - 3) / 2 memulihkan setiap token ke karakter asli."
    }
]


def get_db_path() -> str:
    """Mengembalikan path file database SQLite dengan fallback aman untuk serverless."""
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('LAMBDA_TASK_ROOT'):
        return os.path.join(tempfile.gettempdir(), 'cipherquest.db')

    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')

    try:
        os.makedirs(instance_dir, exist_ok=True)
        test_file = os.path.join(instance_dir, '.write_test')
        with open(test_file, 'w') as f:
            f.write('')
        os.remove(test_file)
        return os.path.join(instance_dir, 'cipherquest.db')
    except (OSError, IOError, PermissionError):
        return os.path.join(tempfile.gettempdir(), 'cipherquest.db')


def _raw_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel database dan memastikan kolom-kolom soal dinamis tersedia."""
    conn = _raw_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_progress (
            session_id TEXT NOT NULL,
            mission_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'unlocked',
            score INTEGER NOT NULL DEFAULT 0,
            hints_used INTEGER NOT NULL DEFAULT 0,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_answer TEXT,
            target_input TEXT,
            correct_answer TEXT,
            hint_text TEXT,
            explanation_text TEXT,
            param_a INTEGER DEFAULT 2,
            param_b INTEGER DEFAULT 1,
            word_count INTEGER DEFAULT 2,
            is_rare INTEGER DEFAULT 0,
            question_prompt TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (session_id, mission_id)
        )
    """)

    cursor.execute("PRAGMA table_info(player_progress)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    new_cols = [
        ("target_input", "TEXT"),
        ("correct_answer", "TEXT"),
        ("hint_text", "TEXT"),
        ("explanation_text", "TEXT"),
        ("param_a", "INTEGER DEFAULT 2"),
        ("param_b", "INTEGER DEFAULT 1"),
        ("word_count", "INTEGER DEFAULT 2"),
        ("is_rare", "INTEGER DEFAULT 0"),
        ("question_prompt", "TEXT"),
    ]
    for col_name, col_type in new_cols:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE player_progress ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

    conn.commit()
    conn.close()


def get_db_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    if not os.path.exists(db_path):
        init_db()
    return _raw_db_connection()


def get_mission_by_id(mission_id: int) -> Optional[Dict[str, Any]]:
    """Mengambil definisi dasar template misi berdasarkan ID."""
    for m in MISSIONS_DATA:
        if m['id'] == mission_id:
            return dict(m)
    return None


def get_mission_for_session(session_id: str, mission_id: int, force_new: bool = False) -> Optional[Dict[str, Any]]:
    """
    Mengambil misi aktif untuk sesi pemain.
    Jika soal belum ada di database, dibuatkan soal dinamis baru.
    Jika soal sudah ada, TIDAK BERUBAH saat halaman di-refresh atau ketika menjawab salah.
    """
    base_mission = get_mission_by_id(mission_id)
    if not base_mission:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status, score, hints_used, attempts, last_answer,
               target_input, correct_answer, hint_text, explanation_text,
               param_a, param_b, word_count, is_rare, question_prompt
        FROM player_progress
        WHERE session_id = ? AND mission_id = ?
    """, (session_id, mission_id))

    row = cursor.fetchone()

    # Jika soal sudah ada dan tidak diminta force_new, gunakan soal tersimpan
    if row and row['target_input'] and not force_new:
        m_dict = dict(base_mission)
        m_dict['target_input'] = row['target_input']
        m_dict['correct_answer'] = row['correct_answer']
        if row['hint_text']:
            m_dict['hint'] = row['hint_text']
        if row['explanation_text']:
            m_dict['explanation'] = row['explanation_text']
        if row['question_prompt']:
            m_dict['prompt_question'] = row['question_prompt']
        m_dict['param_a'] = row['param_a'] or 2
        m_dict['param_b'] = row['param_b'] or 1
        m_dict['word_count'] = row['word_count'] or 2
        m_dict['is_rare'] = bool(row['is_rare'])
        m_dict['status'] = row['status']
        m_dict['score'] = row['score']
        m_dict['hints_used'] = row['hints_used']
        m_dict['attempts'] = row['attempts']
        m_dict['last_answer'] = row['last_answer']
        conn.close()
        return m_dict

    # Buat soal baru secara dinamis
    new_data = generate_mission_data(mission_id)
    current_status = row['status'] if row else ('unlocked' if mission_id == 1 else 'locked')
    current_score = row['score'] if row else 0
    hints_used = row['hints_used'] if row else 0
    attempts = row['attempts'] if row else 0

    cursor.execute("""
        INSERT INTO player_progress (
            session_id, mission_id, status, score, hints_used, attempts,
            target_input, correct_answer, hint_text, explanation_text,
            param_a, param_b, word_count, is_rare, question_prompt, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id, mission_id) DO UPDATE SET
            target_input = excluded.target_input,
            correct_answer = excluded.correct_answer,
            hint_text = excluded.hint_text,
            explanation_text = excluded.explanation_text,
            param_a = excluded.param_a,
            param_b = excluded.param_b,
            word_count = excluded.word_count,
            is_rare = excluded.is_rare,
            question_prompt = excluded.question_prompt,
            updated_at = CURRENT_TIMESTAMP
    """, (
        session_id, mission_id, current_status, current_score, hints_used, attempts,
        new_data['target_input'], new_data['correct_answer'], new_data['hint'],
        new_data['explanation'], new_data['param_a'], new_data['param_b'],
        new_data['word_count'], 1 if new_data['is_rare'] else 0,
        new_data['prompt_question']
    ))
    conn.commit()
    conn.close()

    m_dict = dict(base_mission)
    m_dict.update(new_data)
    m_dict['status'] = current_status
    m_dict['score'] = current_score
    m_dict['hints_used'] = hints_used
    m_dict['attempts'] = attempts
    return m_dict


def get_player_stats(session_id: str) -> Dict[str, Any]:
    """Mengambil data statistik pemain untuk dashboard dan header."""
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
    Mengembalikan daftar semua misi dengan status dan soal aktif pemain:
    - Misi 1 terbuka secara default.
    - Misi n terbuka jika misi n-1 sudah 'completed'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mission_id, status, score, hints_used, attempts, last_answer,
               target_input, correct_answer, hint_text, explanation_text,
               param_a, param_b, word_count, is_rare, question_prompt
        FROM player_progress
        WHERE session_id = ?
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()

    progress_map = {row['mission_id']: dict(row) for row in rows}

    missions_result = []
    prev_completed = True

    for m in MISSIONS_DATA:
        mid = m['id']
        m_copy = dict(m)
        user_prog = progress_map.get(mid)

        # Jika sudah ada soal tersimpan di DB, gunakan data tersebut
        if user_prog and user_prog['target_input']:
            m_copy['target_input'] = user_prog['target_input']
            m_copy['correct_answer'] = user_prog['correct_answer']
            if user_prog['hint_text']:
                m_copy['hint'] = user_prog['hint_text']
            if user_prog['explanation_text']:
                m_copy['explanation'] = user_prog['explanation_text']
            if user_prog['question_prompt']:
                m_copy['prompt_question'] = user_prog['question_prompt']
            m_copy['is_rare'] = bool(user_prog['is_rare'])
            m_copy['word_count'] = user_prog['word_count'] or 2

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


def submit_mission_answer(session_id: str, mission_id: int, user_answer: str, used_hint: bool = False) -> Dict[str, Any]:
    """
    Memvalidasi jawaban misi pemain dan menyimpan progres:
    - Jawaban diverifikasi terhadap soal aktif sesi yang tersimpan.
    - Soal TIDAK berubah saat jawaban salah.
    - Aturan skor:
      - Benar: +100 poin (jika pakai hint: 80 poin).
      - Salah: 0 poin (hanya menambah attempts).
    - Idempotent scoring: jika replay, skor diambil yang tertinggi.
    """
    mission = get_mission_for_session(session_id, mission_id)
    if not mission:
        return {"success": False, "error": "Misi tidak ditemukan."}

    user_clean = user_answer.strip()
    correct_clean = mission['correct_answer'].strip()

    if mission_id in (1, 2):
        # Misi 1 & 2: Jawaban berupa deretan token angka dipisah spasi
        norm_user = " ".join(user_clean.split())
        norm_correct = " ".join(correct_clean.split())
        is_correct = (norm_user == norm_correct)
    else:
        # Misi 3: Jawaban berupa plainteks (case-insensitive)
        norm_user = " ".join(user_clean.upper().split())
        norm_correct = " ".join(correct_clean.upper().split())
        is_correct = (norm_user == norm_correct)

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

    if is_correct:
        base_score = 100
        penalty = 20 if used_hint else 0
        new_earned_score = max(0, base_score - penalty)
        final_score = max(current_score, new_earned_score)

        cursor.execute("""
            UPDATE player_progress
            SET status = 'completed',
                score = ?,
                hints_used = ?,
                attempts = attempts + 1,
                last_answer = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ? AND mission_id = ?
        """, (final_score, 1 if used_hint else 0, user_clean, session_id, mission_id))

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
        # Jawaban salah: update attempts dan last_answer tanpa mengubah soal
        cursor.execute("""
            UPDATE player_progress
            SET attempts = attempts + 1,
                last_answer = ?,
                hints_used = CASE WHEN ? = 1 THEN 1 ELSE hints_used END,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ? AND mission_id = ?
        """, (user_clean, 1 if used_hint else 0, session_id, mission_id))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "is_correct": False,
            "earned_score": 0,
            "penalty": 0,
            "explanation": "Jawaban belum sesuai dengan target operasi. Periksa kembali konversi huruf dan perhitungan matematis Anda.",
            "mission": mission
        }


def regenerate_mission_question(session_id: str, mission_id: int) -> Optional[Dict[str, Any]]:
    """Membuat soal baru untuk misi yang diminta secara eksplisit."""
    return get_mission_for_session(session_id, mission_id, force_new=True)


def reset_progress(session_id: str):
    """Mereset seluruh progres permainan untuk sesi saat ini."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM player_progress WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
