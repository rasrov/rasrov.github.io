(() => {
    const site = window.KimSite ||= {};
    let initialized = false;
    site.initHallGallery = function () {
        if (initialized || !document.querySelector('.hall-result')) return;
        initialized = true;
        const hallViewer = document.createElement('dialog');
        hallViewer.className = 'hall-viewer';
        hallViewer.setAttribute('aria-labelledby', 'hall-viewer-title');
        hallViewer.innerHTML = `
            <header><h2 id="hall-viewer-title"></h2><button type="button" class="viewer-close" aria-label="Cerrar imagen ampliada" autofocus>×</button></header>
            <div class="viewer-stage"><img class="viewer-photo" alt="" draggable="false"></div>
            <div class="viewer-controls"><button type="button" class="viewer-zoom" aria-label="Ampliar imagen al doble" aria-pressed="false">+</button><button type="button" class="viewer-prev" data-nav-direction="previous" aria-label="Foto anterior"></button><span class="viewer-counter" aria-live="polite" aria-atomic="true"></span><button type="button" class="viewer-next" data-nav-direction="next" aria-label="Foto siguiente"></button></div>`;
        document.body.append(hallViewer);
        site.enhanceNavigationControls?.(hallViewer);
        let viewerState = null;
        const viewerStage = hallViewer.querySelector('.viewer-stage');
        const zoomButton = hallViewer.querySelector('.viewer-zoom');
        function resetViewerZoom() {
            viewerStage.classList.remove('is-zoomed');
            viewerStage.scrollTo(0, 0);
            zoomButton.setAttribute('aria-pressed', 'false');
            zoomButton.setAttribute('aria-label', 'Ampliar imagen al doble');
            zoomButton.textContent = '+';
        }
        zoomButton.addEventListener('click', () => {
            if (viewerStage.classList.contains('is-zoomed')) { resetViewerZoom(); return; }
            viewerStage.classList.add('is-zoomed');
            zoomButton.setAttribute('aria-pressed', 'true');
            zoomButton.setAttribute('aria-label', 'Ajustar imagen a la pantalla');
            zoomButton.textContent = '−';
            viewerStage.scrollTo((viewerStage.scrollWidth - viewerStage.clientWidth) / 2,
                (viewerStage.scrollHeight - viewerStage.clientHeight) / 2);
        });
        function renderHallViewer(index) {
            if (!viewerState) return;
            viewerState.index = (index + viewerState.photos.length) % viewerState.photos.length;
            const entry = viewerState.photos[viewerState.index];
            const image = hallViewer.querySelector('.viewer-photo');
            resetViewerZoom();
            image.src = entry.src;
            image.alt = entry.alt;
            hallViewer.querySelector('.viewer-counter').textContent = `${viewerState.index + 1} / ${viewerState.photos.length}`;
            viewerState.onChange(viewerState.index);
        }
        function openHallViewer(photos, index, title, trigger, onChange) {
            viewerState = { photos, index, trigger, onChange };
            hallViewer.querySelector('h2').textContent = title;
            renderHallViewer(index);
            document.documentElement.classList.add('hall-viewer-open');
            hallViewer.showModal();
        }
        hallViewer.querySelector('.viewer-close').addEventListener('click', () => hallViewer.close());
        hallViewer.querySelector('.viewer-prev').addEventListener('click', () => renderHallViewer(viewerState.index - 1));
        hallViewer.querySelector('.viewer-next').addEventListener('click', () => renderHallViewer(viewerState.index + 1));
        hallViewer.addEventListener('keydown', (event) => {
            if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
                event.preventDefault();
                renderHallViewer(viewerState.index + (event.key === 'ArrowRight' ? 1 : -1));
            }
        });
        hallViewer.addEventListener('close', () => {
            document.documentElement.classList.remove('hall-viewer-open');
            viewerState?.trigger.focus({ preventScroll: true });
            viewerState = null;
        });
        let viewerTouch = null;
        hallViewer.addEventListener('pointerdown', (event) => {
            if (viewerStage.classList.contains('is-zoomed') || (window.visualViewport?.scale || 1) > 1 || !event.isPrimary) { viewerTouch = null; return; }
            if (event.pointerType === 'touch' && event.target.matches('.viewer-photo')) viewerTouch = { x: event.clientX, y: event.clientY };
        });
        hallViewer.addEventListener('pointerup', (event) => {
            if (!viewerTouch || !viewerState || viewerStage.classList.contains('is-zoomed') || (window.visualViewport?.scale || 1) > 1) { viewerTouch = null; return; }
            const dx = event.clientX - viewerTouch.x;
            const dy = event.clientY - viewerTouch.y;
            viewerTouch = null;
            if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) renderHallViewer(viewerState.index + (dx < 0 ? 1 : -1));
        });
        hallViewer.addEventListener('pointercancel', () => { viewerTouch = null; });

        let openHallCard = null;

        for (const [cardIndex, card] of [...document.querySelectorAll('.hall-result')].entries()) {
            const heading = card.querySelector('h4');
            const yearLabel = card.querySelector('.hall-top span');
            if (!heading || !yearLabel) continue;
            const title = heading.textContent;
            const year = yearLabel.textContent;
            const galleryTitle = title.includes(year) ? title : `${title} · ${year}`;
            const slides = card.querySelector('.hall-slides');
            const photoElements = [...(slides?.querySelectorAll('img') || [])];
            const photos = photoElements.map(image => ({ src: image.dataset.fullSrc || image.getAttribute('src'), alt: image.alt }));
            if (!photos.length) continue;
            slides.remove();
            const details = document.createElement('div');
            details.className = 'hall-details';
            while (card.firstChild) details.append(card.firstChild);
            card.append(details);

            const preview = document.createElement('button');
            preview.className = 'hall-preview';
            preview.type = 'button';
            preview.setAttribute('aria-label', `Abrir galería de ${galleryTitle}`);
            preview.setAttribute('aria-expanded', 'false');
            preview.setAttribute('aria-controls', `hall-gallery-${cardIndex}`);
            preview.innerHTML = '<span>Ver fotos <span aria-hidden="true">↗</span></span>';
            const previewImage = photoElements[0].cloneNode();
            previewImage.removeAttribute('class');
            previewImage.hidden = false;
            previewImage.alt = '';
            previewImage.sizes = '(max-width: 900px) 40vw, 240px';
            preview.prepend(previewImage);



            const gallery = document.createElement('div');
            gallery.className = 'hall-gallery';
            gallery.id = `hall-gallery-${cardIndex}`;
            gallery.setAttribute('role', 'region');
            gallery.setAttribute('aria-roledescription', 'carrusel');
            gallery.setAttribute('aria-label', `Galería de ${galleryTitle}`);
            gallery.setAttribute('aria-hidden', 'true');
            gallery.inert = true;
            gallery.innerHTML = `

                <div class="hall-gallery-heading"><span></span></div>
                <button class="hall-expand" type="button" aria-label="Ver imágenes en grande" title="Ver en grande"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5M3 3l6 6m12-6-6 6M3 21l6-6m12 6-6-6"/></svg></button><button class="hall-close" type="button" aria-label="Cerrar galería">×</button>
                <div class="hall-gallery-controls">
                    <button class="hall-prev" data-nav-direction="previous" type="button" aria-label="Foto anterior"></button>
                    <span class="hall-counter" aria-live="polite" aria-atomic="true"></span>
                    <button class="hall-next" data-nav-direction="next" type="button" aria-label="Foto siguiente"></button>
                </div>`;
            gallery.querySelector('.hall-gallery-heading span').textContent = galleryTitle;
            gallery.prepend(slides);
            card.append(preview, gallery);
            site.enhanceNavigationControls?.(gallery);

            const counter = gallery.querySelector('.hall-counter');
            const closeButton = gallery.querySelector('.hall-close');
            const expandButton = gallery.querySelector('.hall-expand');
            expandButton.addEventListener('click', () => openHallViewer(photos, current, galleryTitle, expandButton, showPhoto));
            let current = 0;
            let touchStart = null;

            function showPhoto(index) {
                current = (index + photos.length) % photos.length;
                photoElements.forEach((image, photoIndex) => { image.hidden = photoIndex !== current; });
                counter.textContent = `${current + 1} / ${photos.length}`;
            }

            function closeGallery(restoreFocus = true) {
                if (!card.classList.contains('is-gallery-open')) return;
                card.classList.remove('is-gallery-open');
                details.inert = false;
                details.removeAttribute('aria-hidden');
                preview.inert = false;
                preview.setAttribute('aria-expanded', 'false');
                if (restoreFocus) preview.focus({ preventScroll: true });
                slides.hidden = true;
                gallery.inert = true;
                gallery.setAttribute('aria-hidden', 'true');
                openHallCard = null;
            }

            preview.addEventListener('click', () => {
                if (openHallCard) openHallCard();
                slides.hidden = false;
                showPhoto(0);
                gallery.inert = false;
                gallery.removeAttribute('aria-hidden');
                preview.setAttribute('aria-expanded', 'true');
                card.classList.add('is-gallery-open');
                closeButton.focus({ preventScroll: true });
                details.inert = true;
                details.setAttribute('aria-hidden', 'true');
                preview.inert = true;
                openHallCard = () => closeGallery(false);
            });
            closeButton.addEventListener('click', () => closeGallery());
            gallery.querySelector('.hall-prev').addEventListener('click', () => showPhoto(current - 1));
            gallery.querySelector('.hall-next').addEventListener('click', () => showPhoto(current + 1));
            gallery.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') { event.preventDefault(); closeGallery(); }
                if (event.key === 'ArrowLeft') { event.preventDefault(); showPhoto(current - 1); }
                if (event.key === 'ArrowRight') { event.preventDefault(); showPhoto(current + 1); }
            });
            gallery.addEventListener('pointerdown', (event) => {
                if (event.pointerType === 'touch' && !event.target.closest('button')) {
                    touchStart = { x: event.clientX, y: event.clientY };
                }
            });
            gallery.addEventListener('pointerup', (event) => {
                if (!touchStart) return;
                const dx = event.clientX - touchStart.x;
                const dy = event.clientY - touchStart.y;
                touchStart = null;
                if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) showPhoto(current + (dx < 0 ? 1 : -1));
            });
            gallery.addEventListener('pointercancel', () => { touchStart = null; });
            card.classList.add('has-gallery');
        }
    };
})();
