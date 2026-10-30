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
    const fallbackSvg = "data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%22600%22%20height%3D%22450%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20600%20450%22%3E%3Crect%20fill%3D%22%23EFECE6%22%20width%3D%22600%22%20height%3D%22450%22%2F%3E%3Cpath%20d%3D%22M250%2C210%20L350%2C210%20L340%2C260%20L260%2C260%20Z%22%20fill%3D%22%2346594A%22%20opacity%3D%220.6%22%2F%3E%3Ccircle%20cx%3D%22300%22%20cy%3D%22180%22%20r%3D%2225%22%20fill%3D%22%23BD6B46%22%20opacity%3D%220.7%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%22310%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20font-family%3D%22sans-serif%22%20font-size%3D%2218%22%20fill%3D%22%236E685E%22%3EFurniSpace%20Living%3C%2Ftext%3E%3C%2Fsvg%3E";

    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            if (this.src !== fallbackSvg) {
                this.src = fallbackSvg;
            }
        });
    });
});
