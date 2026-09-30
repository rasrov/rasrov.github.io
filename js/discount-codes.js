(() => {
    const site = window.KimSite ||= {};
    const initialized = new WeakSet();
    site.initDiscountCodes = function () {
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
            if (initialized.has(button)) continue;
            const feedback = button.nextElementSibling;
            if (!feedback) continue;
            initialized.add(button);
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
    };
})();
