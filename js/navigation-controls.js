(() => {
    const site = window.KimSite ||= {};
    const initialized = new WeakSet();
    // Shared visual component. Call enhanceNavigationControls(container) for new controls.
    site.enhanceNavigationControls = function (container = document) {
        const buttons = [...container.querySelectorAll('button[data-nav-direction]')];
        if (container.matches?.('button[data-nav-direction]')) buttons.unshift(container);
        for (const button of buttons) {
            if (initialized.has(button)) continue;
            initialized.add(button);
            button.classList.add('navigation-control');
            button.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>';
        }
    };
})();
