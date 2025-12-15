// web/static/js/custom.js

// ========== DOCUMENT READY ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('%c🚀 RJUTB Admin Panel ', 'background: #6366f1; color: white; font-size: 20px; padding: 10px; border-radius: 5px;');
    console.log('%c✅ Dashboard loaded successfully! ', 'background: #10b981; color: white; font-size: 14px; padding: 5px;');

    initAnimations();
    initCardInteractions();
    initTooltips();
});

// ========== COUNTER ANIMATION ==========
function animateCounter(element, target, duration = 2000) {
    let current = 0;
    const increment = target / (duration / 16);

    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;

            // Add sparkle effect when done
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    };

    updateCounter();
}

// ========== INITIALIZE ANIMATIONS ==========
function initAnimations() {
    // Animate counters on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                animateCounter(counter, target);
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.counter').forEach(counter => {
        observer.observe(counter);
    });
}

// ========== CARD INTERACTIONS ==========
function initCardInteractions() {
    // Stat cards tilt effect
    const statCards = document.querySelectorAll('.stat-card');

    statCards.forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function(e) {
            this.style.transform = 'translateY(0) scale(1)';
        });

        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            this.style.transform = `
                translateY(-8px) 
                rotateX(${rotateX}deg) 
                rotateY(${rotateY}deg)
                scale(1.02)
            `;
        });
    });

    // Chart cards hover effect
    const chartCards = document.querySelectorAll('.chart-card');

    chartCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 20px 40px rgba(99, 102, 241, 0.3)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    // Action buttons ripple effect
    const actionBtns = document.querySelectorAll('.action-btn');

    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');

            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// ========== TOOLTIPS ==========
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';

            setTimeout(() => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(0)';
            }, 10);
        });

        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.custom-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '0';
                tooltip.style.transform = 'translateY(-10px)';
                setTimeout(() => tooltip.remove(), 200);
            }
        });
    });
}

// ========== SMOOTH SCROLL ==========
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ========== LOADING OVERLAY ==========
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <p>Yuklanmoqda...</p>
        </div>
    `;
    document.body.appendChild(overlay);

    setTimeout(() => {
        overlay.style.opacity = '1';
    }, 10);
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300);
    }
}

// ========== NOTIFICATION SYSTEM ==========
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    notification.innerHTML = `
        <span class="notification-icon">${icons[type] || icons.info}</span>
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);

    if (duration > 0) {
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

// ========== COPY TO CLIPBOARD ==========
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Nusxalandi!', 'success', 2000);
    }).catch(() => {
        showNotification('Xatolik yuz berdi!', 'error', 2000);
    });
}

// ========== EXPORT TABLE TO CSV ==========
function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => {
            return '"' + col.textContent.replace(/"/g, '""') + '"';
        });
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();

    showNotification('Eksport muvaffaqiyatli!', 'success');
}

// ========== CONFIRM DIALOG ==========
function confirmAction(message, callback) {
    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';

    overlay.innerHTML = `
        <div class="confirm-dialog">
            <div class="confirm-icon">❓</div>
            <h3>Tasdiqlang</h3>
            <p>${message}</p>
            <div class="confirm-buttons">
                <button class="btn-cancel">Bekor qilish</button>
                <button class="btn-confirm">Tasdiqlash</button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    setTimeout(() => {
        overlay.style.opacity = '1';
        overlay.querySelector('.confirm-dialog').style.transform = 'scale(1)';
    }, 10);

    overlay.querySelector('.btn-cancel').addEventListener('click', () => {
        closeConfirm(overlay);
    });

    overlay.querySelector('.btn-confirm').addEventListener('click', () => {
        callback();
        closeConfirm(overlay);
    });

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            closeConfirm(overlay);
        }
    });
}

function closeConfirm(overlay) {
    overlay.style.opacity = '0';
    overlay.querySelector('.confirm-dialog').style.transform = 'scale(0.8)';
    setTimeout(() => overlay.remove(), 300);
}

// ========== LIVE SEARCH ==========
function initLiveSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!searchInput || !table) return;

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
                row.style.backgroundColor = searchTerm ? 'rgba(99, 102, 241, 0.05)' : '';
            } else {
                row.style.display = searchTerm ? 'none' : '';
            }
        });
    });
}

// ========== DARK MODE TOGGLE ==========
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
    const isDark = !document.body.classList.contains('light-mode');
    localStorage.setItem('darkMode', isDark);

    showNotification(
        isDark ? 'Dark mode yoqildi' : 'Light mode yoqildi',
        'info',
        2000
    );
}

// Load dark mode preference
if (localStorage.getItem('darkMode') === 'false') {
    document.body.classList.add('light-mode');
}

// ========== AUTO REFRESH STATS ==========
function autoRefreshStats(interval = 60000) {
    setInterval(() => {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                document.querySelectorAll('.counter').forEach((counter, index) => {
                    const keys = ['folder_count', 'file_count', 'accident_count', 'user_count'];
                    const newValue = data[keys[index]];
                    const currentValue = parseInt(counter.textContent);

                    if (newValue !== currentValue) {
                        counter.style.color = '#10b981';
                        animateCounter(counter, newValue, 1000);

                        setTimeout(() => {
                            counter.style.color = '';
                        }, 2000);
                    }
                });
            })
            .catch(error => console.error('Stats refresh error:', error));
    }, interval);
}

// ========== KEYBOARD SHORTCUTS ==========
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K - Search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) searchInput.focus();
    }

    // Ctrl/Cmd + D - Dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        window.location.href = '/dashboard';
    }

    // Esc - Close modals
    if (e.key === 'Escape') {
        const overlay = document.querySelector('.confirm-overlay, .loading-overlay');
        if (overlay) overlay.remove();
    }
});

// ========== RIPPLE EFFECT CSS (add to custom.css) ==========
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .custom-tooltip {
        position: fixed;
        background: rgba(15, 23, 42, 0.95);
        color: #f8fafc;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transform: translateY(-10px);
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(10px);
        color: #f8fafc;
        padding: 16px 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 300px;
        max-width: 500px;
        z-index: 10000;
        opacity: 0;
        transform: translateX(400px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }
    
    .notification-success {
        border-left: 4px solid #10b981;
    }
    
    .notification-error {
        border-left: 4px solid #ef4444;
    }
    
    .notification-warning {
        border-left: 4px solid #f59e0b;
    }
    
    .notification-info {
        border-left: 4px solid #6366f1;
    }
    
    .notification-icon {
        font-size: 1.5rem;
    }
    
    .notification-message {
        flex: 1;
        font-weight: 500;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: #94a3b8;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.2s;
    }
    
    .notification-close:hover {
        color: #f8fafc;
    }
    
    .confirm-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .confirm-dialog {
        background: #1e293b;
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 20px;
        padding: 40px;
        max-width: 400px;
        text-align: center;
        transform: scale(0.8);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .confirm-icon {
        font-size: 3rem;
        margin-bottom: 20px;
    }
    
    .confirm-dialog h3 {
        color: #f8fafc;
        font-size: 1.5rem;
        margin-bottom: 15px;
    }
    
    .confirm-dialog p {
        color: #94a3b8;
        margin-bottom: 30px;
    }
    
    .confirm-buttons {
        display: flex;
        gap: 15px;
        justify-content: center;
    }
    
    .btn-cancel, .btn-confirm {
        padding: 12px 30px;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-cancel {
        background: rgba(148, 163, 184, 0.1);
        color: #94a3b8;
    }
    
    .btn-cancel:hover {
        background: rgba(148, 163, 184, 0.2);
    }
    
    .btn-confirm {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
    }
    
    .btn-confirm:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
    }
    
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(10, 14, 39, 0.9);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .loading-spinner {
        text-align: center;
    }
    
    .spinner-ring {
        width: 80px;
        height: 80px;
        border: 8px solid rgba(99, 102, 241, 0.1);
        border-top-color: #6366f1;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
    }
    
    .spinner-ring:nth-child(2) {
        border-top-color: #8b5cf6;
        animation-delay: 0.2s;
    }
    
    .spinner-ring:nth-child(3) {
        border-top-color: #3b82f6;
        animation-delay: 0.4s;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-spinner p {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 600;
    }
`;
document.head.appendChild(rippleStyle);

// ========== CONSOLE LOG ==========
console.log('%c💡 Keyboard Shortcuts:', 'font-weight: bold; font-size: 14px; color: #6366f1;');
console.log('Ctrl/Cmd + K → Search');
console.log('Ctrl/Cmd + D → Dashboard');
console.log('Esc → Close modals');