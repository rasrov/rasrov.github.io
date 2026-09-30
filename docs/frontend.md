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
