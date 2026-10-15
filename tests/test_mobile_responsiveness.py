"""
tests/test_mobile_responsiveness.py - Audit Otomatis Kompatibilitas Mobile
Memeriksa meta viewport, aturan CSS responsif, struktur drawer mobile, dan pencegahan overflow.
"""

import os
import re
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_meta_viewport_and_mobile_tags(client):
    """Memastikan meta viewport dengan viewport-fit=cover dan theme-color ada di seluruh halaman."""
    routes = ['/', '/missions', '/encrypt', '/decrypt', '/tutorial']
    for route in routes:
        resp = client.get(route)
        assert resp.status_code == 200
        html = resp.data.decode('utf-8')
        
        # Cek meta viewport
        assert 'name="viewport"' in html
        assert 'width=device-width' in html
        assert 'viewport-fit=cover' in html
        
        # Cek mobile touch navigation elements
        assert 'id="mobile-menu-toggle"' in html
        assert 'id="nav-backdrop"' in html
        assert 'aria-label="Toggle menu navigasi"' in html


def test_css_mobile_rules_and_breakpoints():
    """Memastikan file static/css/style.css memiliki breakpoint mobile yang lengkap."""
    css_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'css', 'style.css')
    assert os.path.exists(css_path)
    
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # Cek iOS Safe Area insets
    assert 'env(safe-area-inset-top' in css
    assert 'env(safe-area-inset-bottom' in css

    # Cek breakpoints utama
    assert '@media (max-width: 992px)' in css
    assert '@media (max-width: 768px)' in css
    assert '@media (max-width: 600px)' in css
    assert '@media (max-width: 480px)' in css
    assert '@media (max-width: 360px)' in css

    # Cek pencegahan horizontal overflow
    assert 'overflow-wrap: anywhere' in css
    assert 'word-break: break-word' in css

    # Cek touch target minimal (44px)
    assert 'min-height: 44px' in css

    # Cek pencegahan auto-zoom iOS (font-size 16px pada form-control)
    assert 'font-size: 16px' in css

    # Cek drawer mobile backdrop
    assert '.nav-backdrop' in css
    assert '.main-nav.nav-open' in css


def test_js_mobile_events():
    """Memastikan static/js/app.js menangani drawer backdrop, tap dismissal, dan keyboard focus."""
    js_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'js', 'app.js')
    assert os.path.exists(js_path)

    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()

    assert 'nav-open' in js
    assert 'navBackdrop' in js
    assert 'closeMobileMenu' in js
    assert 'scrollIntoView' in js
