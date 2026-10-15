"""
config.py - Konfigurasi Aplikasi CipherQuest
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

class Config:
    """Konfigurasi dasar aplikasi."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cipherquest-agent-secure-key-stem-2026-xyz')
    DATABASE = os.path.join(INSTANCE_DIR, 'cipherquest.db')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') in ('1', 'true', 'True')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
