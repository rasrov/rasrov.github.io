// Shared visual component. Call enhanceNavigationControls(container) for new controls.
function enhanceNavigationControls(container = document) {
    for (const button of container.querySelectorAll('button[data-nav-direction]')) {
        button.classList.add('navigation-control');
        button.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>';
    }
}
enhanceNavigationControls();
