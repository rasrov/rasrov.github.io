const root = document.documentElement;
const intro = document.querySelector('.hero-section');
const content = document.querySelector('.about-section');
const navigation = document.querySelector('.hero-nav');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const sectionLinks = [...document.querySelectorAll('.section-indicator a')];
let framePending = false;
let wheelLockedUntil = 0;

function updateHero() {
    const viewportHeight = intro.offsetHeight;
    const distance = content.offsetTop;
    const progress = Math.min(1, Math.max(0, window.scrollY / distance));
    const visualProgress = reducedMotion.matches ? (progress >= 0.5 ? 1 : 0) : progress;
    const navHeight = parseFloat(getComputedStyle(root).getPropertyValue('--nav-height'));
    root.style.setProperty('--hero-height', `${viewportHeight - (viewportHeight - navHeight) * visualProgress}px`);
    root.style.setProperty('--portrait-opacity', String(1 - visualProgress));
    root.style.setProperty('--nav-opacity', String(Math.max(0, (visualProgress - 0.65) / 0.35)));
    navigation.inert = progress < 0.98;
    let activeSection = '#inicio';
    for (const link of sectionLinks) {
        const section = document.querySelector(link.getAttribute('href'));
        if (section && section.getBoundingClientRect().top <= window.innerHeight * 0.5) {
            activeSection = link.getAttribute('href');
        }
    }
    sectionLinks.forEach((link) => {
        if (link.getAttribute('href') === activeSection) {
            link.setAttribute('aria-current', 'location');
        } else {
            link.removeAttribute('aria-current');
        }
    });
    const footer = document.querySelector('.site-footer');
    root.classList.toggle('footer-in-view', Boolean(footer && footer.getBoundingClientRect().top <= window.innerHeight * 0.5));
    framePending = false;
}

function scheduleUpdate() {
    if (!framePending) {
        framePending = true;
        requestAnimationFrame(updateHero);
    }
}

// One wheel gesture moves between the two full-screen sections.
window.addEventListener('wheel', (event) => {
    if (window.matchMedia('(max-width: 900px), (pointer: coarse)').matches || document.querySelector('dialog[open]')) return;
    if (event.ctrlKey || Math.abs(event.deltaY) <= Math.abs(event.deltaX)) return;
    if (event.target.closest('input, textarea, select, [contenteditable="true"]')) return;
    // Allow normal scrolling inside a section taller than the viewport.
    if (window.scrollY > content.offsetTop + 2) return;
    const now = performance.now();
    if (now < wheelLockedUntil) {
        event.preventDefault();
        wheelLockedUntil = Math.max(wheelLockedUntil, now + 160);
        return;
    }
    const goingDown = event.deltaY > 0;
    const target = goingDown ? content.offsetTop : 0;
    if ((goingDown && window.scrollY >= target - 1) || (!goingDown && window.scrollY <= 1)) return;
    event.preventDefault();
    wheelLockedUntil = now + 1000;
    window.scrollTo({ top: target, behavior: reducedMotion.matches ? 'instant' : 'smooth' });
}, { passive: false });

window.addEventListener('scroll', scheduleUpdate, { passive: true });
window.addEventListener('resize', scheduleUpdate);
window.addEventListener('pageshow', scheduleUpdate);
reducedMotion.addEventListener('change', scheduleUpdate);
updateHero();



async function copyDiscountCode(code) {
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(code);
            return;
        } catch {
            // Try the legacy copy action when clipboard permissions are unavailable.
        }
    }
    const previousFocus = document.activeElement;
    const field = document.createElement('textarea');
    field.value = code;
    field.readOnly = true;
    field.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
    document.body.append(field);
    try {
        field.focus({ preventScroll: true });
        field.select();
        if (!document.execCommand('copy')) throw new Error('Clipboard unavailable');
    } finally {
        field.remove();
        previousFocus?.focus({ preventScroll: true });
    }
}

for (const button of document.querySelectorAll('[data-copy-code]')) {
    let resetTimer;
    let copying = false;
    const feedback = button.nextElementSibling;
    button.addEventListener('click', async () => {
        if (copying) return;
        copying = true;
        clearTimeout(resetTimer);
        feedback.textContent = '';
        delete button.dataset.copied;
        try {
            await copyDiscountCode(button.dataset.copyCode);
            button.dataset.copied = 'true';
            feedback.textContent = 'Copiado';
            resetTimer = setTimeout(() => {
                delete button.dataset.copied;
                feedback.textContent = '';
            }, 2500);
        } catch {
            feedback.textContent = 'No se pudo copiar. Código: ' + button.dataset.copyCode;
        } finally {
            copying = false;
        }
    });
}

new ResizeObserver(scheduleUpdate).observe(document.querySelector('main'));


// Keep the original post accessible if a temporary Instagram image URL expires.
for (const image of document.querySelectorAll('.social-image')) {
    const showFallback = () => image.remove();
    image.addEventListener('error', showFallback, { once: true });
    if (image.complete && image.naturalWidth === 0) showFallback();
}

const navToggle = document.querySelector('.nav-toggle');
function closeMobileNav() {
    navToggle.setAttribute('aria-expanded', 'false');
    root.classList.remove('mobile-nav-open');
}
navToggle.addEventListener('click', () => {
    const open = navToggle.getAttribute('aria-expanded') !== 'true';
    navToggle.setAttribute('aria-expanded', String(open));
    root.classList.toggle('mobile-nav-open', open);
});
navigation.addEventListener('click', event => {
    if (event.target.closest('a')) closeMobileNav();
});
document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && root.classList.contains('mobile-nav-open')) {
        closeMobileNav();
        navToggle.focus();
    }
});
document.addEventListener('click', event => {
    if (!navigation.contains(event.target)) closeMobileNav();
});
window.matchMedia('(max-width: 900px)').addEventListener('change', closeMobileNav);
