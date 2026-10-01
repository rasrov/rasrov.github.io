(() => {
    const site = window.KimSite ||= {};
    const initialized = new WeakSet();
    const defaultLogo = 'img/calendar/default-championship.png';
    site.initCalendar = function () {
        const section = document.querySelector('#calendario');
        if (!section || initialized.has(section)) return;
        const required = ['.calendar-days', '.calendar-agenda', '.calendar-empty', '#calendar-month', '#calendar-prev', '#calendar-next'];
        if (!required.every(selector => section.querySelector(selector))) return;
        initialized.add(section);
        const days = section.querySelector('.calendar-days');
        const events = [...section.querySelectorAll('.calendar-event')];
        const latest = events.map(event => event.dataset.date).sort().at(-1);
        let month = latest ? new Date(Number(latest.slice(0, 4)), Number(latest.slice(5, 7)) - 1, 1) : new Date();
        const format = new Intl.DateTimeFormat('es', { month: 'long', year: 'numeric' });
        const pageSize = 3;
        let agendaPage = 0;
        let monthEvents = [];
        const agenda = section.querySelector('.calendar-agenda');
        const eventList = document.createElement('div');
        eventList.className = 'calendar-event-list';
        if (events.length) events[0].before(eventList);
        else agenda.append(eventList);
        events.forEach(event => eventList.append(event));
        function sizeAgenda() {
            const width = eventList.getBoundingClientRect().width;
            if (!width) return;
            let height = 0;
            // Measure natural content at the current width, including hidden pages.
            for (const event of monthEvents) {
                const sample = event.cloneNode(true);
                sample.removeAttribute('id');
                sample.removeAttribute('tabindex');
                sample.hidden = false;
                sample.setAttribute('aria-hidden', 'true');
                sample.inert = true;
                sample.style.cssText = `position:absolute;visibility:hidden;pointer-events:none;width:${width}px;height:auto;min-height:0;`;
                agenda.append(sample);
                height = Math.max(height, sample.getBoundingClientRect().height);
                sample.remove();
            }
            eventList.style.setProperty('--agenda-card-height', `${Math.ceil(height)}px`);
            eventList.style.minHeight = `${Math.ceil(height) * Math.min(pageSize, monthEvents.length)}px`;
        }
        const pagination = document.createElement('nav');
        pagination.className = 'calendar-pagination';
        pagination.setAttribute('aria-label', 'Páginas de la agenda');
        pagination.innerHTML = '<button type="button" aria-label="Página anterior de eventos" data-nav-direction="previous"></button><span aria-live="polite" aria-atomic="true"></span><button type="button" aria-label="Página siguiente de eventos" data-nav-direction="next"></button>';
        section.querySelector('.calendar-agenda').append(pagination);
        site.enhanceNavigationControls?.(section);
        const [previousPage, nextPage] = pagination.querySelectorAll('button');
        function renderAgenda() {
            const pages = Math.max(1, Math.ceil(monthEvents.length / pageSize));
            agendaPage = Math.min(Math.max(0, agendaPage), pages - 1);
            const shown = monthEvents.slice(agendaPage * pageSize, (agendaPage + 1) * pageSize);
            events.forEach(event => { event.hidden = !shown.includes(event); });
            pagination.hidden = pages <= 1;
            // Keep focus on the pager even at either boundary.
            previousPage.setAttribute('aria-disabled', String(agendaPage === 0));
            nextPage.setAttribute('aria-disabled', String(agendaPage === pages - 1));
            pagination.querySelector('span').textContent = `${agendaPage + 1} / ${pages} · ${monthEvents.length} eventos`;
        }
        previousPage.addEventListener('click', () => { if (agendaPage > 0) { agendaPage--; renderAgenda(); } });
        nextPage.addEventListener('click', () => {
            if ((agendaPage + 1) * pageSize < monthEvents.length) { agendaPage++; renderAgenda(); }
        });

        const popup = document.createElement('div');
        popup.id = 'calendar-day-popup';
        popup.className = 'calendar-day-popup';
        const nativePopover = typeof popup.showPopover === 'function' && typeof popup.hidePopover === 'function';
        if (nativePopover) popup.setAttribute('popover', 'auto');
        else popup.hidden = true;
        popup.setAttribute('role', 'dialog');
        popup.setAttribute('aria-labelledby', 'calendar-popup-title');
        document.body.append(popup);
        let popupTrigger = null;
        function popupIsOpen() {
            return nativePopover ? popup.matches(':popover-open') : !popup.hidden;
        }
        function closePopup() {
            if (nativePopover) {
                if (popupIsOpen()) popup.hidePopover();
            } else popup.hidden = true;
            popupTrigger?.setAttribute('aria-expanded', 'false');
        }
        document.addEventListener('click', event => {
            if (!nativePopover && popupIsOpen() && !popup.contains(event.target) && !popupTrigger?.contains(event.target)) {
                const restoreFocus = popup.contains(document.activeElement);
                closePopup();
                if (restoreFocus) popupTrigger?.focus({ preventScroll: true });
            }
        });
        function selectEvent(event) {
            if (popupIsOpen()) closePopup();
            agendaPage = Math.floor(monthEvents.indexOf(event) / pageSize);
            renderAgenda();
            events.forEach(item => item.classList.toggle('is-selected', item === event));
            event.tabIndex = -1;
            event.focus({ preventScroll: true });
            event.scrollIntoView({ block: 'nearest', behavior: 'auto' });
        }
        function appendEventLogo(tile, event, className) {
        const fallback = defaultLogo;
        const logo = document.createElement('img');
        let usingFallback = !event.dataset.logo;
        logo.alt = ''; logo.className = className;
        tile.classList.toggle('missing-logo', usingFallback);
        logo.addEventListener('error', () => {
            if (usingFallback) { logo.remove(); return; }
            usingFallback = true;
            tile.classList.add('missing-logo');
            logo.src = fallback;
        });
        logo.src = event.dataset.logo || fallback;
        tile.append(logo);
        }
        function eventTile(event, day) {
            const tile = document.createElement('button');
            tile.type = 'button';
            tile.className = `calendar-day has-event ${event.dataset.status}`;
            const label = { confirmed: 'Participa', pending: 'Pendiente', absent: 'No participa' }[event.dataset.status] || 'Pendiente';
            tile.setAttribute('aria-label', `${day} ${format.format(month)}. ${event.querySelector('h3').textContent}. Kim: ${label}. Ver detalles`);
            tile.title = tile.getAttribute('aria-label');
            tile.setAttribute('aria-controls', event.id);
            appendEventLogo(tile, event, 'calendar-day-logo');
            const strip = document.createElement('span'); strip.className = 'calendar-day-status'; strip.setAttribute('aria-hidden', 'true');
            const text = document.createElement('span'); text.className = 'calendar-status-label'; text.textContent = label;
            strip.append(text); tile.append(strip);
            tile.addEventListener('click', () => selectEvent(event));
            return tile;
        }
        function positionPopup() {
            if (!popupTrigger || !popupIsOpen()) return;
            const rect = popupTrigger.getBoundingClientRect();
            const width = popup.offsetWidth, height = popup.offsetHeight;
            popup.style.left = `${Math.max(8, Math.min(innerWidth - width - 8, rect.left + rect.width / 2 - width / 2))}px`;
            popup.style.top = `${Math.max(8, Math.min(innerHeight - height - 8, rect.bottom + height + 8 <= innerHeight ? rect.bottom + 8 : rect.top - height - 8))}px`;
        }
        function showEvents(trigger, matches, day) {
            if (popupIsOpen()) {
                const same = popupTrigger === trigger;
                closePopup();
                if (same) return;
            }
            popupTrigger?.setAttribute('aria-expanded', 'false');
            popupTrigger = trigger;
            popup.replaceChildren();
            const header = document.createElement('div'); header.className = 'calendar-popup-header';
            const title = document.createElement('h3'); title.id = 'calendar-popup-title'; title.textContent = `${day} ${format.format(month)} · ${matches.length} competiciones`;
            const close = document.createElement('button'); close.type = 'button'; close.textContent = '×'; close.setAttribute('aria-label', 'Cerrar competiciones del día');
            close.addEventListener('click', () => { closePopup(); trigger.focus({ preventScroll: true }); });
            header.append(title, close);
            const tiles = document.createElement('div'); tiles.className = 'calendar-popup-tiles';
            matches.forEach(event => tiles.append(eventTile(event, day)));
            popup.append(header, tiles);
            trigger.setAttribute('aria-expanded', 'true');
            if (nativePopover) popup.showPopover();
            else popup.hidden = false;
            positionPopup();
            tiles.querySelector('button').focus({ preventScroll: true });
        }
        popup.addEventListener('toggle', () => {
            if (!popupIsOpen()) popupTrigger?.setAttribute('aria-expanded', 'false');
        });
        document.addEventListener('keydown', event => {
            if (event.key === 'Escape' && popupIsOpen()) { event.preventDefault(); closePopup(); popupTrigger?.focus({ preventScroll: true }); }
        });
        window.addEventListener('resize', positionPopup);
        window.addEventListener('scroll', positionPopup, { passive: true });

        function render() {
            if (popupIsOpen()) closePopup();
            section.querySelector('#calendar-month').textContent = format.format(month);
            days.replaceChildren();
            const prefix = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, '0')}`;
            const monthEnd = `${prefix}-${String(new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()).padStart(2, '0')}`;
            const visible = events.filter(event => event.dataset.date <= monthEnd && (event.dataset.end || event.dataset.date) >= prefix + '-01');
            monthEvents = visible;
            agendaPage = 0;
            events.forEach(event => event.classList.remove('is-selected'));
            sizeAgenda();
            renderAgenda();
            section.querySelector('.calendar-empty').hidden = visible.length > 0;
            const offset = (month.getDay() + 6) % 7;
            const count = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
            for (let i = 0; i < Math.ceil((offset + count) / 7) * 7; i++) {
                const day = i - offset + 1;
                const dateKey = `${prefix}-${String(day).padStart(2, '0')}`;
                const inMonth = day >= 1 && day <= count;
                const matches = inMonth ? visible.filter(event => event.dataset.date <= dateKey && (event.dataset.end || event.dataset.date) >= dateKey) : [];
                const cell = document.createElement(matches.length ? 'button' : 'div');
                cell.className = 'calendar-day';
                if (!inMonth) { cell.classList.add('is-empty'); cell.setAttribute('aria-hidden', 'true'); }
                else {
                    const number = document.createElement('span'); number.className = 'calendar-day-number'; number.textContent = day; cell.append(number);
                    if (matches.length) {
                        if (matches.length === 1) {
                            const tile = eventTile(matches[0], day);
                            days.append(tile);
                            continue;
                        }
                        cell.type = 'button';
                        cell.classList.add('has-event', 'multiple-events');
                        cell.replaceChildren();
                        const previewEvent = matches.find(event => event.dataset.logo && event.dataset.logo !== defaultLogo) || matches[0];
                        appendEventLogo(cell, previewEvent, 'calendar-championship-icon');
                        const countLabel = document.createElement('span'); countLabel.textContent = `+${matches.length}`; cell.append(countLabel);
                        cell.setAttribute('aria-label', `${day} ${format.format(month)}: ${matches.length} competiciones. Mostrar opciones`);
                        cell.setAttribute('aria-haspopup', 'dialog');
                        cell.setAttribute('aria-controls', popup.id);
                        cell.setAttribute('aria-expanded', 'false');
                        cell.addEventListener('click', () => showEvents(cell, matches, day));
                    }
                }
                days.append(cell);
            }
        }
        for (const [id, delta] of [['calendar-prev', -1], ['calendar-next', 1]]) {
            section.querySelector('#' + id).addEventListener('click', () => { month = new Date(month.getFullYear(), month.getMonth() + delta, 1); render(); });
        }
        const agendaHeading = agenda.querySelector('.social-eyebrow');
        if (agendaHeading) agendaHeading.textContent = 'AGENDA DEL MES';
        render();
        section.classList.add('calendar-ready');
        let lastWidth = 0;
        if (window.ResizeObserver) new ResizeObserver(entries => {
            const width = entries[0].contentRect.width;
            if (Math.abs(width - lastWidth) > 0.5) { lastWidth = width; sizeAgenda(); }
        }).observe(eventList);
        else window.addEventListener('resize', sizeAgenda);
        document.fonts?.ready.then(sizeAgenda);
    };
})();
