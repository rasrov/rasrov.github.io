(() => {
    const site = window.KimSite ||= {};
    const initialized = new WeakSet();
    site.initSocialImages = function () {
        // Keep the original post accessible if a temporary Instagram image URL expires.
        for (const image of document.querySelectorAll('.social-image')) {
            if (initialized.has(image)) continue;
            initialized.add(image);
            const showFallback = () => image.remove();
            image.addEventListener('error', showFallback, { once: true });
            if (image.complete && image.naturalWidth === 0) showFallback();
        }
    };
})();
