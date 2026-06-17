// XADO Baltic — main JS

// Auto submit language form on button click (already done via button[name=language])

// Sticky navbar shadow on scroll
window.addEventListener('scroll', function() {
    const nav = document.querySelector('.navbar');
    if (nav) {
        nav.classList.toggle('shadow', window.scrollY > 10);
    }
});

// Bootstrap tooltips
document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
});
