(() => {
    const site = window.KimSite ||= {};
    const initialized = new WeakSet();
    site.initMobileNavigation = function () {
        const root = document.documentElement;
        const navigation = document.querySelector('.hero-nav');
        const navToggle = document.querySelector('.nav-toggle');
        if (!navigation || !navToggle || initialized.has(navigation)) return;
        initialized.add(navigation);
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
        root.classList.add('navigation-ready');
        window.matchMedia('(max-width: 900px)').addEventListener('change', closeMobileNav);
    };
})();
