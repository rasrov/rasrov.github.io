# Usabilidad, compatibilidad y revisión manual

## Comportamiento básico y mejorado

El HTML mantiene enlaces de navegación y la agenda completa sin scripts de aplicación. No incluye inert en la navegación inicial. Sin inicialización del menú se muestran sus enlaces directamente y se oculta el botón desplegable; sin animación de portada esta deja de ser fija y no tapa las secciones siguientes. Sin calendario inicializado se ocultan la cuadrícula vacía y sus botones, pero se conservan las competiciones y sus programas oficiales. El título inicial es «Agenda de competiciones»; pasa a «Agenda del mes» cuando se activa el filtrado.

Cada componente activa sus clases de mejora al inicializarse. El arranque tolera módulos ausentes. La galería ampliable y la copia al portapapeles siguen necesitando JavaScript; permanecen el palmarés textual y los códigos visibles si no carga. No se promete que cualquier excepción arbitraria durante una inicialización permita recuperar todo el estado previo.

El selector de coincidencias utiliza popover si existen showPopover y hidePopover. En caso contrario se muestra un panel no modal con cierre explícito, Escape, cierre al pulsar fuera y gestión de foco. Al elegir una competición el foco pasa a su ficha; al cerrar explícitamente vuelve al activador. Se permite salir del panel mediante Tab, porque no es modal. ResizeObserver tiene alternativa de resize en calendario y es opcional en portada.

Objetivo de compatibilidad: versiones estables recientes de Edge, Chrome, Firefox y Safari, con HTML estático utilizable sin scripts. La validación automatizada disponible se ejecuta en Edge; Firefox y Safari están pendientes de validación real. El fallback de popover se prueba suprimiendo sus métodos en Edge, no se presenta como prueba en navegadores antiguos. El JavaScript utiliza sintaxis moderna; no se pretende soportar Internet Explorer.

## Estados del calendario

Las celdas usan ✓, ? y − para Participa, Pendiente y No participa, con símbolos de 14 px y una leyenda textual de 14 px. Los nombres accesibles siguen incluyendo fecha, competición y estado completo. El selector de coincidencias muestra etiquetas completas de 12 px, y la agenda conserva el estado escrito. El color no es la única señal. El botón de cierre del selector mide 44 × 44 px.

Contraste calculado de primer plano/fondo de los estados: pendiente 7,91:1, participa 7,03:1 y no participa 7,04:1; leyenda 11,37:1. Estas mediciones de colores planos no certifican el contraste de toda la web, fotografías o contenido externo.

## Evidencia local — 30/09/2026

Regresiones de navegador: navegación sin scripts de aplicación y con módulo ausente, selector sin soporte popover, cierre/foco/selección, límites de paginación y los tres estados accesibles. Se conservan las pruebas de menú, Escape, copia fallida, galerías, visor, zoom, calendario vacío y eventos de varios días.

Capturas y comprobaciones geométricas de calendario, selector y menú a 320, 390, 768 y 1440 px: sin desbordamiento horizontal. Se comprobó también la navegación estática a esas anchuras. Los recursos remotos se aislaron y las animaciones se desactivaron. Las anchuras reducidas comprueban reflujo, no equivalen a zoom del navegador ni a un dispositivo táctil real.

## Protocolo pendiente en dispositivos y tecnologías reales

Registrar navegador/versión, sistema, dispositivo, fecha, resultado y pasos para reproducir cada problema. No marcar una prueba como pasada por haber ejecutado otra similar en emulación.

- [ ] Teléfono: Android/Chrome y iPhone/Safari, vertical y horizontal. Recorrer todas las secciones, abrir/cerrar menú, pulsar días individuales y coincidencias, cambiar mes y página y copiar códigos. Comprobar legibilidad de símbolos/leyenda sin ampliar.
- [ ] Tacto: cambiar fotografías, abrir visor, ampliar, arrastrar en ambos ejes y cerrar. Verificar que el desplazamiento de la página se recupera, también después de rotar el teléfono.
- [ ] Zoom real: 200 % y 400 % en navegador de escritorio, además del tamaño de texto del sistema en móvil. No deben perderse enlaces, etiquetas, botones ni el contenido del selector.
- [ ] Teclado: Tab/Shift+Tab desde el enlace de salto, menú, galerías, calendario, selector, páginas y descuentos. Foco visible y orden comprensible; Escape cierra y devuelve el foco; no hay trampas fuera del visor modal.
- [ ] Lector de pantalla: NVDA/Firefox o Edge y VoiceOver/Safari. Revisar landmarks, jerarquía de títulos, nombres de enlaces, fecha/estado de cada día, anuncio del mes y página y contexto del foco al elegir competición. Comprobar que no se duplican las etiquetas de símbolos.
- [ ] Preferencias: movimiento reducido, contraste forzado y texto ampliado. Revisar foco sobre fotografías y estados del calendario.
- [ ] Sin JavaScript: desactivarlo desde el navegador, recargar y recorrer los enlaces y programas de la agenda. Repetir bloqueando un módulo para confirmar la mejora parcial.
- [ ] Servicios publicados: tarjetas de Instagram y reproducción de YouTube, conexión lenta y error de imagen. Comprobar enlaces de respaldo y ausencia de bloqueos.

AUD-23 y AUD-25 permanecen abiertos hasta completar sus verificaciones manuales. Los nuevos cambios locales todavía deben publicarse y validarse en el sitio público.

Actualización de diseño solicitada: calendario sin leyenda ni símbolos de estado. El pie de cada imagen muestra PENDIENTE, NO PARTICIPA o PARTICIPA, en mayúsculas y con separación entre letras. Se conserva el tamaño compacto de 6 px en móvil; su comprobación de legibilidad sigue pendiente en AUD-23. Las mejoras de compatibilidad y nombres accesibles se mantienen. Esta decisión sustituye la presentación con símbolos y leyenda descrita en el registro anterior.
