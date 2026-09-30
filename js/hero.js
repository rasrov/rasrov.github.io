(() => {
    const site = window.KimSite ||= {};
    const initialized = new WeakSet();
    site.initHero = function () {
        const root = document.documentElement;
        const intro = document.querySelector('.hero-section');
        const content = document.querySelector('.about-section');
        const navigation = document.querySelector('.hero-nav');
        if (!intro || !content || initialized.has(intro)) return;
        initialized.add(intro);
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        const sectionLinks = [...document.querySelectorAll('.section-indicator a')];
        let framePending = false;
        let wheelLockedUntil = 0;

        function updateHero() {
            const viewportHeight = intro.offsetHeight;
            const distance = Math.max(1, content.offsetTop);
            const progress = Math.min(1, Math.max(0, window.scrollY / distance));
            const visualProgress = reducedMotion.matches ? (progress >= 0.5 ? 1 : 0) : progress;
            const navHeight = parseFloat(getComputedStyle(root).getPropertyValue('--nav-height')) || 0;
            root.style.setProperty('--hero-height', `${viewportHeight - (viewportHeight - navHeight) * visualProgress}px`);
            root.style.setProperty('--portrait-opacity', String(1 - visualProgress));
            root.style.setProperty('--nav-opacity', String(Math.max(0, (visualProgress - 0.65) / 0.35)));
            if (navigation) navigation.inert = progress < 0.98;
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
        root.classList.add('hero-ready');
        updateHero();
        const main = document.querySelector('main');
        if (main && window.ResizeObserver) new ResizeObserver(scheduleUpdate).observe(main);
    };
})();
