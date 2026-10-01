// Shared, progressive entry animation for direct children of marked groups.
(() => {
    const site = window.KimSite ||= {};
    const registered = new WeakSet();
    const revealed = new WeakSet();
    const active = new Set();
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let observer;

    function finish(card) {
        card.classList.remove('is-entry-ready', 'is-entering');
        card.style.removeProperty('--entry-index');
        active.delete(card);
    }

    site.initCardEntrances = function (root = document) {
        if (!window.IntersectionObserver || motion.matches) return;
        if (!observer) {
            observer = new IntersectionObserver(entries => {
                const groups = new Map();
                for (const entry of entries) {
                    const card = entry.target;
                    if (!entry.isIntersecting || revealed.has(card)) continue;
                    revealed.add(card);
                    observer.unobserve(card);
                    const group = card.parentElement;
                    if (!groups.has(group)) groups.set(group, []);
                    groups.get(group).push(card);
                }
                for (const [group, cards] of groups) {
                    const order = [...group.children];
                    cards.sort((a, b) => order.indexOf(a) - order.indexOf(b));
                    cards.forEach((card, index) => {
                        if (motion.matches || card.contains(document.activeElement)) { finish(card); return; }
                        card.style.setProperty('--entry-index', index);
                        active.add(card);
                        card.classList.add('is-entering');
                    });
                }
            }, { threshold: 0.01 });
            motion.addEventListener('change', () => {
                if (motion.matches) [...active].forEach(card => {
                    revealed.add(card);
                    observer.unobserve(card);
                    finish(card);
                });
            });
        }
        const groups = [...root.querySelectorAll('[data-entry-group]')];
        if (root.matches?.('[data-entry-group]')) groups.unshift(root);
        for (const group of groups) {
            for (const card of group.children) {
                if (registered.has(card)) continue;
                registered.add(card);
                card.addEventListener('animationend', event => {
                    if (event.target === card && event.animationName === 'card-entry') finish(card);
                });
                card.addEventListener('animationcancel', event => {
                    if (event.target === card && event.animationName === 'card-entry') finish(card);
                });
                // Keyboard focus immediately restores the final position.
                card.addEventListener('focusin', () => {
                    revealed.add(card);
                    observer.unobserve(card);
                    finish(card);
                });
                // Prepare the starting position before the observer can trigger entry.
                active.add(card);
                card.classList.add('is-entry-ready');
                observer.observe(card);
            }
        }
    };
})();
