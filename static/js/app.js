/**
 * app.js - Logika Interaksi Antarmuka Pengguna CipherQuest
 * Dioptimalkan untuk Mobile Touch (Android & iOS/iPhone) dan Desktop.
 * Tidak menggandakan perhitungan matematika backend.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Drawer & Backdrop Controller
    const mobileMenuBtn = document.getElementById('mobile-menu-toggle');
    const mainNav = document.getElementById('main-nav');
    const navBackdrop = document.getElementById('nav-backdrop');

    function openMobileMenu() {
        if (!mainNav || !mobileMenuBtn) return;
        mainNav.classList.add('nav-open');
        mobileMenuBtn.classList.add('is-active');
        mobileMenuBtn.setAttribute('aria-expanded', 'true');
        if (navBackdrop) navBackdrop.classList.add('active');
        document.body.classList.add('menu-open');
    }

    function closeMobileMenu() {
        if (!mainNav || !mobileMenuBtn) return;
        mainNav.classList.remove('nav-open');
        mobileMenuBtn.classList.remove('is-active');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
        if (navBackdrop) navBackdrop.classList.remove('active');
        document.body.classList.remove('menu-open');
    }

    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = mainNav.classList.contains('nav-open');
            if (isOpen) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
        });

        // Klik pada backdrop menutup menu drawer
        if (navBackdrop) {
            navBackdrop.addEventListener('click', () => {
                closeMobileMenu();
            });
        }

        // Klik di luar navigasi menutup menu drawer
        document.addEventListener('click', (e) => {
            if (mainNav.classList.contains('nav-open')) {
                if (!mainNav.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                    closeMobileMenu();
                }
            }
        });

        // Klik pada tautan navigasi otomatis menutup menu
        const navLinks = mainNav.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                closeMobileMenu();
            });
        });

        // Tombol ESC menutup menu
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && mainNav.classList.contains('nav-open')) {
                closeMobileMenu();
            }
        });

        // Reset state jika viewport diubah ke ukuran desktop (> 768px)
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && mainNav.classList.contains('nav-open')) {
                closeMobileMenu();
            }
        });
    }

    // 2. Interaksi Petunjuk Misi (Hint Button)
    const btnToggleHint = document.getElementById('btn-toggle-hint');
    const hintContent = document.getElementById('hint-content');
    const inputUsedHint = document.getElementById('input-used-hint');

    if (btnToggleHint && hintContent && inputUsedHint) {
        btnToggleHint.addEventListener('click', () => {
            const isCurrentlyHidden = hintContent.style.display === 'none' || hintContent.style.display === '';
            
            if (isCurrentlyHidden) {
                const confirmed = confirm("Konfirmasi Intelijen: Membuka petunjuk akan mengurangi skor maksimal misi ini sebesar 20 poin. Lanjutkan?");
                if (confirmed) {
                    hintContent.style.display = 'block';
                    inputUsedHint.value = '1';
                    btnToggleHint.textContent = "Petunjuk Aktif (-20 Poin)";
                    btnToggleHint.classList.remove('btn-warning-outline');
                    btnToggleHint.classList.add('btn-disabled');
                    btnToggleHint.disabled = true;
                }
            }
        });
    }

    // 3. Auto dismiss flash notification setelah 6 detik
    const flashAlerts = document.querySelectorAll('.alert-dismissible');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // 4. Mencegah zoom iOS yang tidak disengaja dan meningkatkan respon sentuh
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        // Scroll ke view saat keyboard virtual muncul jika terpotong
        input.addEventListener('focus', () => {
            setTimeout(() => {
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });
    });
});

/**
 * Fungsi Menyalin Teks ke Clipboard dengan Umpan Balik Visual
 * @param {string} elementId ID elemen yang berisi teks
 * @param {HTMLElement} btnElement Tombol yang memicu penyalinan
 */
function copyToClipboard(elementId, btnElement) {
    const textElement = document.getElementById(elementId);
    if (!textElement) return;

    const textToCopy = textElement.textContent.trim();

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            showCopyFeedback(btnElement);
        }).catch(err => {
            fallbackCopyText(textToCopy, btnElement);
        });
    } else {
        fallbackCopyText(textToCopy, btnElement);
    }
}

function fallbackCopyText(text, btnElement) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    textArea.setAttribute('readonly', '');
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopyFeedback(btnElement);
        }
    } catch (err) {
        console.error('Gagal menyalin:', err);
    }
    document.body.removeChild(textArea);
}

function showCopyFeedback(btnElement) {
    if (!btnElement) return;
    const originalHtml = btnElement.innerHTML;
    btnElement.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <span>Tersalin!</span>
    `;
    btnElement.classList.add('text-success');

    setTimeout(() => {
        btnElement.innerHTML = originalHtml;
        btnElement.classList.remove('text-success');
    }, 2000);
}

/**
 * Toggle Accordion Langkah Perhitungan
 * @param {string} bodyId ID container body accordion
 * @param {HTMLElement} toggleBtn Tombol toggle
 */
function toggleAccordion(bodyId, toggleBtn) {
    const body = document.getElementById(bodyId);
    if (!body) return;

    const isHidden = body.style.display === 'none' || body.style.display === '';
    body.style.display = isHidden ? 'block' : 'none';

    if (toggleBtn) {
        const statusSpan = toggleBtn.querySelector('.accordion-status');
        if (statusSpan) {
            statusSpan.textContent = isHidden ? 'Tutup Rincian' : 'Buka Rincian';
        }
    }
}

/**
 * 5. LocalStorage Game Progress Synchronization
 * Menyimpan progres pemain di browser klien untuk keandalan serverless Vercel
 */
const STORAGE_KEY = 'cipherquest_player_progress_v2';

function saveLocalProgress(data) {
    try {
        const current = getLocalProgress() || {};
        const merged = { ...current, ...data, lastUpdated: new Date().toISOString() };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    } catch (e) {
        console.warn('LocalStorage tidak dapat diakses:', e);
    }
}

function getLocalProgress() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (e) {
        return null;
    }
}

function clearLocalProgress() {
    try {
        localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
        console.warn('Gagal mereset localStorage:', e);
    }
}

// Inisialisasi sinkronisasi progres DOM ke localStorage saat DOM dimuat
document.addEventListener('DOMContentLoaded', () => {
    try {
        const headerScore = document.getElementById('header-score');
        const headerMissions = document.getElementById('header-missions');
        
        if (headerScore && headerMissions) {
            const currentScore = parseInt(headerScore.textContent, 10) || 0;
            const missionsText = headerMissions.textContent.trim();
            
            // Simpan state terkini
            saveLocalProgress({
                score: currentScore,
                missionsText: missionsText
            });
        }

        // Listener untuk form reset progress agar membersihkan localStorage juga
        const resetForms = document.querySelectorAll('form[action*="reset-progress"]');
        resetForms.forEach(form => {
            form.addEventListener('submit', () => {
                clearLocalProgress();
            });
        });
    } catch (err) {
        console.error('Error pada sinkronisasi localStorage:', err);
    }
});

