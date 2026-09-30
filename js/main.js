// All component scripts are loaded before this entry point at the end of body.
(() => {
    const site = window.KimSite;
    site?.initHero?.();
    site?.initMobileNavigation?.();
    site?.initDiscountCodes?.();
    site?.initSocialImages?.();
    site?.initHallGallery?.();
    site?.initCalendar?.();
    site?.enhanceNavigationControls?.();
})();
