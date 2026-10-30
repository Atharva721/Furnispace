/**
 * FurniSpace Frontend Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Toggle
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }

    // 2. Flash Message Dismissal
    document.querySelectorAll('.flash-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const flashMsg = e.target.closest('.flash-message');
            if (flashMsg) {
                flashMsg.style.opacity = '0';
                flashMsg.style.transform = 'translateY(-10px)';
                flashMsg.style.transition = 'all 0.25s ease';
                setTimeout(() => flashMsg.remove(), 250);
            }
        });
    });

    // Auto-dismiss info/success alerts after 6 seconds
    setTimeout(() => {
        document.querySelectorAll('.flash-success, .flash-info').forEach(msg => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            msg.style.transition = 'all 0.3s ease';
            setTimeout(() => msg.remove(), 300);
        });
    }, 6000);

    // 3. Graceful Image Error Fallback
    const fallbackUrl = "/static/images/fallback-furniture.svg";

    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            if (this.src !== window.location.origin + fallbackUrl && !this.src.endsWith(fallbackUrl)) {
                this.src = fallbackUrl;
            }
        });
    });
});
