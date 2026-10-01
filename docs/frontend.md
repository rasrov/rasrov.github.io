# Organización e inicialización del frontend

JavaScript clásico sin framework ni compilador. Cada archivo encapsula su estado en una IIFE y expone solo sus inicializadores en window.KimSite. No se exportan variables de galería, temporizadores o estado de navegación al ámbito global.

## Orden de carga

Los scripts se cargan al final de body, en este orden:

1. navigation-controls.js: componente compartido de flechas.
2. hero.js: transición de portada, gesto de rueda e indicador de secciones.
3. mobile-navigation.js: menú y cierre por enlace, clic exterior o Escape.
4. discount-codes.js: copia de códigos, mensaje de resultado y restauración del foco.
5. social-images.js: respaldo cuando falla una imagen temporal.
6. hall-gallery.js: galerías y visor ampliado.
7. calendar.js: calendario, agenda y selector de eventos.
8. main.js: punto único que llama a los inicializadores.

Los componentes registran funciones; no arrancan al cargarse. main.js es el arranque explícito. Galería y calendario llaman a KimSite.enhanceNavigationControls al crear sus controles; no dependen de una pasada accidental de otro script al final.

## Componentes opcionales y reinicialización

Los inicializadores no actúan cuando falta su sección. El calendario comprueba su estructura mínima; la galería omite tarjetas incompletas. Una segunda llamada no duplica listeners, visor, agenda ni SVG. No se pretende ofrecer montaje/desmontaje de una SPA: la galería se inicializa una vez por página.

Para un botón de navegación creado después del arranque:

```js
KimSite.enhanceNavigationControls(button);
```

También acepta un contenedor con varios botones. La función conserva el SVG ya inicializado. Mantener data-nav-direction y las etiquetas accesibles del botón.

## Pruebas

```sh
python scripts/validate.py --browser
```

Las regresiones usan Edge/Chrome real y cubren calendario, ausencia de secciones, inicialización repetida, controles dinámicos, menú, éxito/fallo de copia, respaldo de imágenes, apertura/cierre de galería y visor, navegación con flechas, zoom y foco. Las pruebas simulan el portapapeles para obtener resultados deterministas.

Una prueba carga el HTML real con su CSS y el orden real de scripts, sustituyendo las imágenes por un recurso local embebido y omitiendo iframes externos. Comprueba inicialización conjunta; no mide descargas reales ni certifica reproducción externa.

Quedan pendientes en AUD-25 las comprobaciones de accesibilidad con lector de pantalla y tacto en móvil real. Estas pruebas tampoco sustituyen una comparación visual completa ni prueban todos los navegadores. No se ha reorganizado CSS en este bloque.

## Entradas escalonadas de tarjetas

Plan aplicado el 01/10/2026: revisar transiciones existentes, incorporar un comportamiento compartido, conectarlo a los tres grupos y comprobar foco, movimiento reducido y scroll. Las transiciones de hover y apertura de galerías permanecen en sus componentes; la entrada se aplica al contenedor de cada tarjeta.

js/card-entrances.js registra KimSite.initCardEntrances(root = document), llamado desde main.js después de inicializar las galerías. Se carga antes de main.js. Un único IntersectionObserver observa los hijos directos de contenedores con data-entry-group: las listas hall-grid, youtube-grid y social-grid. Los atributos están fuera de las regiones generadas, por lo que no se duplican cambios en los generadores Python.

Cada tarjeta se anima una sola vez al entrar en pantalla. Las que entran en la misma notificación se ordenan por su posición en el DOM y reciben retrasos de 0, 200, 400 ms, etc., independientes para cada grupo. Las que entran más tarde empiezan una nueva secuencia: no acumulan retrasos por tarjetas que siguen fuera de pantalla.

El estilo compartido usa un desplazamiento de 80 px, opacidad constante, sin fundido, duración de 600 ms y cubic-bezier(0, 0, 0.2, 1). Variables en el grupo: --entry-distance, --entry-duration, --entry-stagger y --entry-easing. No añadir nuevas animaciones por red social; para reutilizar, marcar el contenedor con data-entry-group. Si se insertan tarjetas dinámicamente, llamar de nuevo a KimSite.initCardEntrances(contenedor); la inicialización es idempotente.

El contenido es visible por defecto, incluso sin scripts o sin IntersectionObserver. prefers-reduced-motion evita la animación y cancela las activas si cambia durante la sesión. El foco dentro de una tarjeta cancela su entrada y CSS garantiza visibilidad inmediata incluso antes de procesar el evento. Al terminar se retiran la clase y el índice temporal, evitando dejar transformaciones que interfieran con galerías. La impresión tampoco anima.

Pruebas en tests/test_card_entrances.py: orden/retrasos, inicialización repetida y nuevas tarjetas, foco, ausencia de API, movimiento reducido y scroll real sin repetición. tests/browser_frames.mjs es un ejecutor reutilizable mediante CDP para páginas con runFrameChecks(); usa tiempo real porque el reloj virtual de dump-dom puede avanzar sin entregar fotogramas de IntersectionObserver. Requiere Node y BROWSER_BIN, proporcionados por validate.py --browser.

Revisión visual en Edge a 390 y 1440 px: Hall of Fame, YouTube e Instagram, durante y después de la entrada; sin desbordamiento horizontal ni clases de animación restantes tras finalizar. Instagram muestra los retrasos 0/200/400 ms. Imágenes externas y reproductores aislados para la prueba; no es una prueba de servicios externos ni de tacto real.

Ajuste de entrada: las tarjetas se preparan con el desplazamiento inicial antes de observar su entrada. Permanecen opacas durante la espera y el movimiento; solo se anima la traslación hasta su posición final. Movimiento reducido, foco e impresión eliminan también el desplazamiento preparado.

Referencia de movimiento: [Material Design, duración y curvas](https://m1.material.io/motion/duration-easing.html), usando desaceleración al entrar. El recorrido de 80 px es una decisión visual del proyecto y los 600 ms corresponden a la duración solicitada, no a valores prescritos por esa guía.

Desplazamiento libre: hero.js observa el scroll de forma pasiva para actualizar la portada, sin interceptar la rueda ni aplicar bloqueos temporales. Se conserva el ajuste nativo a secciones mediante scroll-snap en escritorio; sigue desactivado hasta 900 px o con puntero táctil. Las entradas de tarjetas se mantienen independientes del desplazamiento.

Ajuste de scroll: Sobre Kim queda excluido de los puntos de scroll-snap para evitar que los movimientos cortos vuelvan a anclar la página en esa sección. Las demás secciones mantienen sus puntos de ajuste, sin scroll-snap-stop obligatorio. El enlace #sobre-kim continúa funcionando.
