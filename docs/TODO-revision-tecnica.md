# TODO de revisión técnica

Fecha: 30/09/2026. Proyecto: rasrov.github.io.

## Estado actual — perfil del calendario (02/10/2026)

**AUD-33 avanzado, abierto por medición en teléfono real.** Se mantienen 27 tareas completadas y 7 pendientes. Perfil reproducible con datos y CSS reales en Edge, a 1440/390 px y CPU ×1/×4. Medición de tarjetas agrupada tras confirmar su coste; sin caché ni cambios en el scroll. Resultados completos y límites en `docs/calendar-performance.md`. Sin publicación.

Validación: **110/110 pruebas correctas**, incluidas las regresiones de navegador y la nueva comprobación de alturas, resize, paginación y mes vacío. Dos builds offline idénticos; sintaxis de ambos auxiliares JavaScript verificada.

## Registro — documentación consolidada (02/10/2026)

Completado **AUD-29**: 27 tareas implementadas; 7 pendientes. README como entrada operativa, guías contrastadas con scripts/workflows locales y TODO general consolidado sin tareas de publicación duplicadas. Registro anterior preservado en `docs/todo-history-2026-10-02.md`. Las confirmaciones históricas no certifican el despliegue actual. Última validación funcional: 109 pruebas correctas en AUD-18; este bloque solo modifica documentación.

Validación documental: formato y `git diff --check` correctos; 47 enlaces locales a archivos comprobados. Nombres, disparadores y comandos contrastados con el código local. No se han comprobado enlaces remotos ni el estado de GitHub y no se han repetido pruebas funcionales al no cambiar código.

## Registro — inventario de imágenes antiguas (02/10/2026)

Completado **AUD-16**: 26 tareas implementadas. Auditadas 184 imágenes y sus consumidores; sin duplicados exactos. Eliminadas las dos imágenes sin uso visual actual y el alias de la foto alternativa por indicación del usuario; quedan 182 imágenes y 172 alias. Fondo de portada confirmado como fuente necesaria. Inventario, referencias, pesos, huellas y decisiones en `docs/images.md`. La presentación de la web no cambia; las URLs de las imágenes retiradas dejarán de estar disponibles al publicar.

## Registro — nombres de pruebas (02/10/2026)

Completado **AUD-18**: 25 tareas implementadas. Renombrados `test_youtube.py` y `test_instagram.py` a `test_update_youtube.py` y `test_update_instagram.py`, conservando sus bytes. Convenciones actualizadas; el descubrimiento automático existente no requiere cambios en workflows. Sin publicación.

Validación: **109/109 pruebas correctas**, incluidas las de navegador y ambos módulos renombrados. Formato correcto, sin referencias operativas a los nombres antiguos y dos builds offline idénticos.

## Registro — formato reproducible (02/10/2026)

Completado **AUD-17**: 24 tareas implementadas. Legado Python normalizado con Ruff fijado; comprobación de UTF-8 sin BOM, LF, nueva línea final y espacios integrada en validate.py y los tres workflows. Árboles de sintaxis Python idénticos antes y después del formato. HTML generado y disposición de recursos web conservados. Sin publicación.

Validación: **109/109 pruebas correctas**, incluidas las de navegador. Comprobación de formato correcta para 33 archivos Python; Git no detecta archivos de texto del checkout con CRLF o finales mixtos. Dos builds offline idénticos, sin modificar fuentes durante la validación.

## Registro — nombres de imágenes (02/10/2026)

Completado **AUD-15**: 23 tareas implementadas. Normalizadas 173 rutas de originales y variantes, con años completos, kebab-case y corrección de `strength`. HTML, inventario, sitemap y Open Graph actualizados. Compatibilidad de URLs antiguas generada en el build mediante `img/image-aliases.json`; bytes de todas las imágenes contrastados con Git sin diferencias. Sin publicación.

Validación: **106/106 pruebas correctas**, incluidas las de navegador. Los 173 alias del artefacto coinciden byte a byte con sus destinos; dos builds de validación idénticos y `_site/` reconstruido. Simulación del optimizador con las rutas nuevas correcta, sin aplicar conversiones.

## Registro — optimización manual de imágenes (01/10/2026)

Completado **AUD-11**: 22 tareas implementadas. Script y Action bajo demanda, sin programación horaria. Pruebas de transparencia, orientación, idempotencia, reparación, simulación y recuperación ante fallos. La optimización del checkout no se ha aplicado; solo se ha simulado. Primera ejecución de GitHub pendiente.

Validación: **103/103 pruebas correctas**, incluidas las de navegador. Integración sobre copia temporal del sitio real: 7 originales con variantes nuevas, 45 adoptados sin recomprimir y segunda ejecución sin cambios. Dos builds de validación idénticos.

## Registro — séptima tanda

Completado **AUD-24**: 21 tareas implementadas. **AUD-23 y AUD-25 avanzan, pero siguen abiertos por validación manual real.**

- Navegación y agenda utilizables sin scripts; controles interactivos se muestran tras inicializar. El arranque admite módulos ausentes y el calendario incorpora alternativa a popover y ResizeObserver.
- Estados compactos con símbolos de 14 px y leyenda textual, etiquetas de 12 px en el selector y nombres accesibles completos. Contraste calculado de los tres estados superior a 7:1.
- Regresiones añadidas para ausencia de scripts, módulo ausente, selector alternativo y foco, paginación y estados. Protocolo de teclado, zoom, móvil, lector de pantalla, preferencias y contenido publicado en docs/accessibility.md.
- Capturas y geometría revisadas a 320, 390, 768 y 1440 px sin desbordamiento horizontal en los estados comprobados. No equivale a teléfono real ni lector de pantalla.

Validación: **77/77 pruebas correctas**, incluidas 16 de navegador. Construcción offline e idempotencia correctas, _site reconstruido y git diff --check limpio. Sin publicación.

## Registro — sexta tanda

Completados **AUD-19 y AUD-20**: 20 tareas implementadas.

- css/styles.css se organiza por componentes, con reglas responsive junto a cada sección. Se consolidan declaraciones sobrescritas, especialmente del calendario, y se elimina --navigation-border sin consumidores.
- Se centralizan el fondo y los separadores compartidos del calendario. Se conservan los fallbacks de unidades y el comportamiento existente en los puntos de corte.
- Organización, variables, breakpoints y protocolo de comprobación documentados en docs/styles.md, enlazado desde README.md.

Validación: **72/72 pruebas correctas**, incluidas 11 de navegador; construcción offline e idempotencia correctas, _site reconstruido. Sin diferencias en estilos calculados y geometría muestreados en **110 escenarios** ni en **23 parejas de capturas** de Edge. Se verificaron diez anchuras, incluidos los límites de los breakpoints; las capturas comparan 390 y 1440 px. Recursos externos aislados y animaciones desactivadas; no sustituye la comprobación de tacto real, lectores de pantalla ni todos los estados de interacción de AUD-25. Sin publicación.

## Registro — quinta tanda

Completados **AUD-21 y AUD-22**: 18 tareas implementadas.

- main.js es el punto de arranque. Portada, menú, descuentos e imágenes sociales se separan en hero.js, mobile-navigation.js, discount-codes.js y social-images.js.
- Cada componente encapsula su estado en una IIFE y registra inicializadores en window.KimSite. Galería y calendario inicializan explícitamente los controles que crean; la función compartida admite contenedores o botones individuales.
- Inicialización protegida ante secciones ausentes y llamadas repetidas. El calendario omite estructuras incompletas y las galerías omiten tarjetas sin sus elementos necesarios. No se ha cambiado CSS.
- Se amplía AUD-25 con ocho pruebas de frontend: menú, copia, respaldo de imágenes, controles dinámicos, galería/visor/zoom/foco, ausencia de secciones y HTML completo con CSS real. Sigue abierto por la comprobación de lector de pantalla, tacto real y cobertura restante.

Validación: **72/72 pruebas correctas**, incluidas 11 pruebas de navegador (3 de calendario y 8 de frontend). La comprobación conjunta usa HTML/CSS reales con imágenes sustituidas e iframes externos omitidos; no es una auditoría visual completa ni prueba de servicios externos. Dos construcciones idénticas y _site reconstruido. Sin publicación.

Orden de carga y contratos de inicialización en docs/frontend.md. La consolidación de CSS (AUD-19/AUD-20) se completó en la sexta tanda.

## Registro — cuarta tanda

Completados **AUD-09 y AUD-13**: 16 tareas implementadas.

- Los actualizadores preparan JSON/HTML y respaldos en .snapshot-update antes de sustituir archivos. Los fallos de escritura restauran bytes anteriores; si falla la restauración, se conserva un registro de recuperación y se bloquean nuevas escrituras y builds. No garantiza sustitución simultánea ni durabilidad ante apagado; ejecutar un solo actualizador por checkout.
- Las nuevas consultas registran metadata.source y metadata.fetched_at UTC. --from-cache conserva el JSON byte a byte. Las instantáneas actuales se identifican como legacy-cache con fecha desconocida, sin inventar fechas de obtención.
- snapshot_info.py muestra metadatos y compara hashes de JSON normalizado mediante --compare-dir. Documentación de recuperación e importación de snapshots públicos en docs/snapshots.md; contrato de metadatos integrado en validate_data.py.

Validación: **64/64 pruebas correctas**, incluidas regresiones de fallo de preparación, fallo de segunda escritura, rollback fallido, reintento bloqueado, conservación de cache y actualización simulada de ambos proveedores. Dos builds offline idénticos; _site reconstruido y snapshots coincidentes con data/. Sin consultas reales a APIs ni despliegue.

La separación e inicialización de JavaScript (AUD-21/AUD-22) se completó en la quinta tanda.

## Registro — tercera tanda

Completados **AUD-10 y AUD-12**: 14 tareas implementadas en total.

- scripts/validate_data.py comprueba tipos, fechas, IDs duplicados, asociaciones huérfanas, estados, URLs y campos públicos de redes. Valida también eventos que luego excluye el filtro Natural. El lector JSON rechaza claves duplicadas y números no finitos.
- scripts/validate_resources.py comprueba referencias HTML/CSS, rutas estáticas JavaScript, fragmentos HTML, mayúsculas exactas, inventario de imágenes y sitemap. Alcance y límites documentados en docs/data-contracts.md.
- build.py valida los datos antes del renderizado y el artefacto antes de sustituir _site. Una regresión comprueba que un recurso roto conserva la salida anterior. Estos controles también se ejecutan desde validate.py y el workflow existente.

Validación: **52/52 pruebas correctas**, incluidas tres regresiones de Edge; dos construcciones de comprobación idénticas y _site local reconstruido. Fuentes conservadas, sin consultas a proveedores ni publicación. Sigue pendiente la primera ejecución del workflow en GitHub.

Las escrituras consistentes y metadatos (AUD-09/AUD-13) se completaron en la cuarta tanda.

## Registro — segunda tanda

Resueltos adicionalmente **AUD-07, AUD-08, AUD-14 y AUD-27**; 12 tareas implementadas en total.

- `python scripts/build.py` construye _site/ desde las instantáneas locales y conserva index.html/data del checkout. El workflow utiliza el mismo constructor después de actualizar redes. Las pruebas cubren artefacto completo, ausencia de archivos privados de la raíz, sustitución de archivos obsoletos y conservación/restauración de la salida anterior ante errores.
- Los tres generadores y el validador comparten scripts/generated_regions.py. Se comprueban marcadores ausentes, duplicados e invertidos, idempotencia y conservación exacta del contenido exterior. scripts/ es ahora importable como paquete y conserva sus comandos directos.
- Las pruebas de redes y del constructor fijan el reloj; se prueban publicaciones futuras, igualdad en el instante límite y zonas horarias. Instagram admite now explícito, igual que YouTube.
- Convenciones en docs/conventions.md y uso del constructor en README.md. Añadidos .editorconfig y .gitattributes. **AUD-17 sigue abierto**: no se ha normalizado el legado ni configurado una comprobación automática completa de formato.
- **AUD-09 se completó en la cuarta tanda** para los actualizadores; la segunda tanda protegió inicialmente solo el constructor offline.

Validación: **36/36 pruebas correctas**, incluidas las tres regresiones de Edge. Dos construcciones de validación idénticas, fuentes conservadas byte a byte y construcción real de _site/ completada. Sin consultas a APIs ni despliegue. La primera ejecución remota de Actions sigue pendiente.

Los contratos de datos y la integridad de recursos (AUD-10/AUD-12) se completaron en la tercera tanda.

## Registro — primera tanda

Resueltos en código AUD-01 a AUD-06 y AUD-26. La descripción original de cada hallazgo se conserva como evidencia de la auditoría. README.md contiene el arranque local y el comando de validación.

- scripts/validate.py comprueba sintaxis, ejecuta las pruebas y regenera las tres secciones dos veces en una copia temporal. Comprueba idempotencia y conservación de contenido manual; no reescribe las instantáneas del checkout.
- El workflow incorpora validación previa a las APIs y ejecución para PR sin secretos ni publicación. Pendiente comprobar su primera ejecución real en GitHub Actions; se ha validado localmente el comando que utiliza.
- El calendario soporta cero eventos y ausencia de sección. Cada botón de evento anuncia la fecha de su celda, también en el selector de coincidencias. Se mantiene el diseño visual de las celdas basado en logos; la fecha aparece además en el tooltip. La prueba valida etiquetas y foco en el DOM; queda pendiente la comprobación con lector de pantalla real de AUD-25 y del TODO general.
- El renderizador comprueba IDs duplicados antes del filtro Natural y rechaza marcadores invertidos. La utilidad común para los tres generadores se completó en la segunda tanda (AUD-08).
- AUD-25 tiene cobertura inicial del calendario, pero siguen pendientes el resto de interacciones y el protocolo manual. El constructor de un artefacto utilizable se completó en la segunda tanda (AUD-07).

Validación de esta tanda: **25/25 pruebas correctas**, incluidas 3 regresiones en Edge sin interfaz; sintaxis Python/JavaScript correcta y dos generaciones offline idénticas. No se han consultado APIs, publicado cambios ni realizado una auditoría visual completa.

- [x] **AUD-34 · Evitar botones vacíos en los límites del mes.** La prueba de un evento entre agosto y septiembre detectó celdas de relleno convertidas en botones enfocables y sin etiqueta. Ahora solo se buscan eventos para días válidos del mes; las celdas de relleno son elementos no interactivos. Cubierto por la regresión de navegador.

La segunda tanda completó la construcción, las regiones compartidas, el reloj de pruebas y la documentación de convenciones.

## Diagnóstico y alcance original

La estructura actual es adecuada para una landing estática: css/, js/, img/, data/, scripts/, tests/ y docs/ tienen responsabilidades reconocibles. No hace falta introducir un framework, un bundler o una carpeta src/ para corregir los problemas encontrados. Conviene estabilizar la generación, consolidar estilos y documentar las convenciones antes de reorganizar directorios.

Revisión del árbol local, HTML, CSS, los cuatro JavaScript, los tres generadores Python, el auxiliar PowerShell, JSON, workflow, pruebas y documentación. Incluye cambios locales preexistentes; no representa necesariamente lo publicado. No se han corregido archivos de aplicación ni ejecutado consultas a proveedores o despliegues. No se ha realizado una nueva prueba visual, con lector de pantalla o en móvil real.

Se conserva el TODO.md anterior: sus pendientes de producto, SEO, publicación, S3 y revisión móvil siguen allí. Esta lista incorpora los hallazgos técnicos, sin dar por realizadas aquellas tareas.

Prioridades: P1 = corregir antes del siguiente despliegue o refactor relacionado; P2 = mantenimiento próximo; P3 = mejora opcional. Cada casilla incluye evidencia y criterio de cierre. Las propuestas no son fallos de funcionamiento demostrados.

## P1 — fallos y cobertura que falta

- [x] **AUD-01 · Reparar el error de sintaxis del calendario.** `scripts/render_calendar.py:1` empieza con un comando de terminal y una ruta absoluta de Windows pegados al docstring. El análisis de Python falla con `unicodeescape`. El workflow ejecuta este archivo, por lo que este estado local impediría completar build. Retirar el comando del código y llevar la instrucción de servidor a la documentación. Cierre: sintaxis válida y generación offline correcta en una copia temporal, preservando las otras secciones.

- [x] **AUD-02 · Validar todo el código antes de consultar APIs.** `.github/workflows/pages.yml` ejecuta únicamente las pruebas de redes antes de las llamadas externas. Estas no importan el calendario y pasan aunque AUD-01 exista. Añadir comprobación sintáctica de todos los Python y JavaScript, y una generación offline completa. Cierre: un error en cualquier generador impide avanzar a las llamadas externas.

- [x] **AUD-03 · Añadir validación para pull requests.** El workflow solo declara push a main, schedule y workflow_dispatch. Crear una ejecución de validación para PR sin secretos ni despliegue, reutilizando los controles offline. Cierre: un PR puede detectar AUD-01 antes de entrar en main.

- [x] **AUD-04 · Soportar un calendario sin eventos.** `js/calendar.js:15` ejecuta `events[0].before(eventList)` sin comprobar que haya eventos; también presupone que existe la sección. Con una instantánea vacía se produce una excepción antes de mostrar el estado vacío. Insertar el contenedor desde la agenda y proteger la inicialización cuando la sección no exista. Cierre: cero eventos muestra un mensaje y ningún error JavaScript.

- [x] **AUD-05 · Incluir la fecha en los botones de eventos del calendario.** `eventTile()` en `js/calendar.js:81` solo anuncia campeonato y participación. Al sustituir una celda con un único evento por ese botón, se pierde el número del día que se había creado; los eventos de varios días generan botones con etiquetas idénticas. Pasar la fecha de la celda y añadirla al nombre accesible; decidir también su representación visible. Cierre: se distingue cada día con teclado y lector de pantalla.

## P2 — estructura, generación y datos

- [x] **AUD-06 · Crear README.md de entrada.** No existe una guía central. Documentar propósito, árbol, Python soportado, servidor local con ruta relativa, pruebas, generación offline y publicación; enlazar docs/calendar.md, docs/youtube.md y docs/instagram.md. Cierre: una persona puede levantar y comprobar la web desde un clon sin secretos.

- [x] **AUD-07 · Definir fuente editable y salida generada.** `index.html` mezcla contenido manual con tres regiones generadas, y los scripts reescriben el mismo archivo. Documentar qué se edita en data/ y qué en HTML; añadir un comando único de construcción offline, preferiblemente con salida en _site/. No es necesario migrar ya a plantillas. Cierre: reproducir la web no depende de recordar el orden de tres comandos ni modifica accidentalmente contenido manual.

- [x] **AUD-08 · Centralizar el reemplazo de regiones generadas.** Los tres Python repiten búsqueda de marcadores, separación y escritura. Extraer una utilidad pequeña que compruebe unicidad y orden de los marcadores. Cierre: las pruebas cubren marcadores ausentes, repetidos e invertidos y preservación exacta del resto del documento.

- [x] **AUD-09 · Evitar salidas locales parcialmente actualizadas.** Los actualizadores escriben JSON y después HTML mediante write_text. Un error de escritura del segundo archivo deja el primero actualizado. Preparar ambas salidas antes de sustituirlas y definir recuperación o generar en un directorio temporal publicable. Cierre: una prueba de fallo de escritura verifica la política elegida. El workflow ya evita desplegar cuando falla el job.

- [x] **AUD-10 · Formalizar y validar los contratos JSON.** Hay comprobaciones parciales en los generadores, pero no un validador común de snapshots. Documentar campos obligatorios, tipos, fechas con zona cuando corresponda, estados y relaciones por ID; validar también IDs huérfanos y duplicados antes de filtrar eventos Natural. Cierre: un dato inválido produce un diagnóstico con archivo y campo antes de escribir salidas. No exige incorporar una dependencia de JSON Schema.

- [x] **AUD-11 · Reproducir la optimización de imágenes.** Script reutilizable `scripts/optimize_images.py`, Pillow fijado, tamaños/calidad/transparencia y versiones registradas en el manifiesto. Action exclusivamente manual que valida y abre PR; originales conservados y variantes intactas reutilizadas. Uso en `docs/images.md`. Pendiente subir el workflow y realizar su primera ejecución remota.

- [x] **AUD-12 · Automatizar integridad de recursos.** Añadir validación de src, srcset, data-full-src, referencias CSS, fragmentos internos, inventario y sitemap. Cierre: renombrar o borrar una imagen referenciada hace fallar la validación. La comprobación parcial ejecutada en esta revisión no encontró referencias HTML locales rotas.

- [x] **AUD-13 · Hacer visible la procedencia y frescura de los snapshots.** Los JSON de redes no incluyen fecha de obtención y Actions actualiza el artefacto sin guardar el resultado en Git; docs/instagram.md ya relata diferencias entre local y publicado. Añadir metadatos de obtención y documentar cómo comparar o recuperar un snapshot público validado. Cierre: se distingue cuándo se obtuvo una selección y de dónde procede, sin guardar credenciales.

## P2 — nombres y convenciones

- [x] **AUD-14 · Documentar una convención por lenguaje.** Propuesta: kebab-case en recursos web y carpetas públicas; snake_case para Python; camelCase para funciones/variables JavaScript; MAYUSCULAS para constantes; estados CSS con is-/has-. Mantener anclas públicas existentes salvo migración explícita. Cierre: ejemplos y reglas en docs/conventions.md. Los estilos propios de distintos lenguajes no tienen que ser idénticos.

- [x] **AUD-15 · Normalizar nombres de imágenes y carpetas.** Migradas 173 rutas a kebab-case, años de cuatro cifras y nombres descriptivos; corregido `rp-strength-logo`. Referencias del HTML, variantes, inventario, sitemap y metadatos actualizadas. El build preserva las URLs antiguas mediante alias; imágenes idénticas byte a byte. Mapa completo en `img/image-aliases.json` y política en `docs/images.md`.

- [x] **AUD-16 · Revisar variantes antiguas y nombres v2/raw.** Auditadas 184 imágenes, sin duplicados exactos; `hero-background.png` es una fuente activa. Eliminadas por indicación del usuario `kim-angel-about-alternative.jpg` y `calendar/multiple-championships-v2.png`, sin referencias activas, junto con el alias `img/web_main_about_kim_1.jpg`. Quedan 182 imágenes y 172 alias. `multiple-championships.png` ya estaba ausente. Inventario y registro en `docs/images.md`; revisión general del artefacto pendiente en AUD-32.

- [x] **AUD-17 · Fijar formato y finales de línea.** .editorconfig y .gitattributes aplicados; normalizado el legado Python con Ruff 0.14.0 y corregidos finales de línea/texto. `scripts/check_format.py` comprueba sin escribir o normaliza con `--fix`; validate.py y los tres workflows lo ejecutan. Alcance por lenguaje y comandos en `docs/conventions.md`. Cambios de formato contrastados mediante AST, sin correcciones de lógica.

- [x] **AUD-18 · Alinear nombres de pruebas con sus scripts.** Aplicados `test_update_youtube.py` y `test_update_instagram.py`; `test_update_competitions.py` y `test_render_calendar.py` ya seguían la convención. Contenido de las pruebas conservado y documentación actualizada. Descubrimiento mediante unittest, sin listas de archivos en los workflows.

## P2 — frontend y estilos

- [x] **AUD-19 · Consolidar la cascada CSS.** css/styles.css tiene 1.436 líneas y acumula correcciones al final. `.calendar-day.multiple-events` cambia sucesivamente de fondo en las líneas 1391, 1420 y 1424; `.calendar-day-logo` se redefine varias veces. Consolidar el valor final por componente y breakpoint; retirar propiedades sin consumidor como --navigation-border si se confirma que no se necesitan. Cierre: cascada consolidada y aspecto comparado a anchuras de escritorio/móvil sin diferencias en los escenarios documentados en docs/styles.md.

- [x] **AUD-20 · Ordenar CSS por responsabilidad.** Separar conceptualmente base, layout, componentes y utilidades, con breakpoints documentados (hoy aparecen 540, 767, 900 y 1100 px). Puede mantenerse un solo archivo mientras sea cómodo. Centralizar colores/espaciados repetidos que tengan el mismo significado. Cierre: secciones de componentes y tokens del calendario en css/styles.css; responsabilidades de los breakpoints documentadas en docs/styles.md.

- [x] **AUD-21 · Dividir responsabilidades de main.js.** Mezcla animación de portada, rueda, seguimiento de secciones, portapapeles, respaldo de Instagram y menú móvil. Extraer inicializadores por función y proteger dependencias DOM. Cierre: retirar una sección opcional no impide inicializar las restantes.

- [x] **AUD-22 · Explicitar inicialización y alcance de JavaScript.** main.js y hall-gallery.js declaran estado en el ámbito global; calendar.js utiliza una IIFE; navigation-controls.js depende de ejecutarse después de crear los botones. Unificar encapsulación y llamar al componente de controles desde una inicialización explícita, o usar módulos nativos. Cierre: el orden requerido queda verificable y un botón creado posteriormente también se inicializa.

- [ ] **AUD-23 · Revisar legibilidad del estado en móvil.** Presentación vigente: texto PENDIENTE/NO PARTICIPA/PARTICIPA en mayúsculas, sin símbolos ni leyenda, con tamaño compacto de 6 px en móvil. Pendiente comprobar contraste, zoom y móvil real según `docs/accessibility.md`; las mediciones del diseño anterior no validan este. No se declara un incumplimiento normativo solo por ese tamaño.

- [x] **AUD-24 · Definir comportamiento sin JavaScript y compatibilidad.** index.html entrega navegación con inert y las galerías requieren inicialización; calendar.js utiliza popover sin detección de soporte. Definir navegadores objetivo y un fallback progresivo para navegación/calendario. Cierre: contenido y enlaces principales siguen utilizables si el script no carga o una API de interfaz no está disponible. Alternativa y navegación estática verificadas en Edge; objetivo de compatibilidad y límites documentados en docs/accessibility.md.

- [ ] **AUD-25 · Añadir pruebas de interacción críticas.** Regresiones automatizadas de menú, foco/Escape, galería/zoom, calendario y copia incorporadas. Pendientes lector de pantalla, tacto y comprobaciones reales del protocolo de `docs/accessibility.md`. Las pruebas locales y la emulación no sustituyen estas comprobaciones.

## P2 — pruebas y operación

- [x] **AUD-26 · Añadir pruebas unitarias del calendario.** Cubrir filtrado Natural, estados, orden, duplicados, fechas inválidas, logos, escape HTML y conservación de otras regiones. Cierre: test_render_calendar.py se ejecuta en la suite y detecta entradas inválidas y regresiones de renderizado.

- [x] **AUD-27 · Hacer deterministas las pruebas de fechas.** Los fixtures de redes usan septiembre de 2026 y los selectores consultan el reloj real; YouTube permite now pero las pruebas no lo fijan, e Instagram no lo recibe. Inyectar o simular el reloj. Cierre: los mismos resultados con independencia de la fecha del sistema, incluyendo futuros y zonas horarias.

- [ ] **AUD-28 · Aclarar la política ante fallo de proveedores.** En pages.yml todas las publicaciones dependen de ambas APIs, también un cambio solo de CSS. El comportamiento está documentado y conserva la web publicada, pero bloquea cualquier nueva publicación si caduca Instagram. Decidir si mantenerlo o permitir una publicación explícita desde cache validada, mostrando su antigüedad. Cierre: la política se prueba y no se ignoran fallos silenciosamente.

- [x] **AUD-29 · Actualizar documentación operativa desfasada.** Corregidos nombre/estado del workflow social, dependencias, previsualización con alias, optimización implementada y estados textuales del calendario. README centraliza operación; TODO general reúne pendientes sin duplicados y remite las tareas técnicas a este archivo. Historial anterior conservado por separado; no se afirma publicación ni vigencia de credenciales sin evidencia nueva.

- [ ] **AUD-30 · Documentar y probar el auxiliar PowerShell.** discover_competition_logo.ps1 usa ResponseUri y outerHTML sin declarar versión de PowerShell. Verificar compatibilidad en la versión elegida, documentar argumentos y probar extracción de enlaces con HTML de ejemplo. Cierre: ejecución reproducible y mensaje claro si cambia la estructura remota. No se ejecutó contra sitios externos en esta revisión.

## P3 — mejoras opcionales

- [ ] **AUD-31 · Fijar revisiones de Actions.** checkout, setup-python y las acciones Pages se referencian por etiquetas principales. Valorar SHA de commit revisado y actualización automatizada de esas referencias. Cierre: proceso de actualización documentado; no se afirma que las versiones actuales tengan una vulnerabilidad.

- [ ] **AUD-32 · Revisar el contenido del artefacto público.** El workflow copia img/ y data/ completos, incluido el inventario y todos los originales. Definir qué se necesita públicamente y qué se conserva solo como fuente. Cierre: lista explícita sin romper las imágenes originales del visor ni las URLs del sitemap. Tamaño del artefacto y descarga inicial del navegador son métricas diferentes.

- [ ] **AUD-33 · Medir antes de optimizar el calendario.** Perfil local completado con 90 eventos renderizados y CSS real; comparación secuencial a 1440/390 px y CPU ×1/×4. `sizeAgenda()` agrupa escrituras y lecturas tras medir el coste; baja su mediana, sin mejora global consistente del cambio de mes. Scroll sin cambios: las consultas están en hero.js y la agenda no se vuelve a medir al desplazar. Auxiliar y resultados en `docs/calendar-performance.md`. Pendiente teléfono real; la emulación no cierra esa comprobación.

## Registro — comprobaciones de la auditoría inicial (30/09/2026)

Los hallazgos y recuentos siguientes son históricos; no representan el estado actual.

- 14/14 pruebas unittest correctas. La primera ejecución tuvo un error de permisos en la carpeta temporal del entorno; repetidas con acceso permitido, todas pasan. No es un fallo atribuido al proyecto.
- Sintaxis JavaScript válida en los cuatro archivos mediante node --check.
- Análisis sintáctico Python: update_youtube.py y update_instagram.py correctos; render_calendar.py falla en la primera línea (AUD-01).
- JSON de data/, auditoría IFBB y manifiesto de imágenes parseables.
- 72 eventos; sin IDs duplicados ni claves huérfanas en participación/logos en el snapshot revisado.
- Sin IDs HTML duplicados, fragmentos internos inexistentes ni archivos locales ausentes en src, href, srcset y data-full-src comprobados. Esto no constituye una validación completa de HTML/CSS ni de enlaces remotos.
- Se mantienen los cambios locales preexistentes en TODO.md, data/instagram.json, docs/instagram.md, index.html y los scripts modificados.

## Registro — orden propuesto en la auditoría inicial

1. AUD-01 a AUD-05 y AUD-26: recuperar una generación comprobable y cubrir los fallos concretos.
2. AUD-06 a AUD-13, AUD-17 y AUD-27: documentar y hacer reproducible el mantenimiento.
3. AUD-19 a AUD-25: refactorizar interfaz con comprobaciones visuales y de interacción.
4. Normalizar nombres mediante una migración única de referencias; revisar operación y propuestas P3 según necesidad.

Actualización de diseño solicitada: calendario sin leyenda ni símbolos de estado. El pie de cada imagen muestra PENDIENTE, NO PARTICIPA o PARTICIPA, en mayúsculas y con separación entre letras. Se conserva el tamaño compacto de 6 px en móvil; su comprobación de legibilidad sigue pendiente en AUD-23. Las mejoras de compatibilidad y nombres accesibles se mantienen. Esta decisión sustituye la presentación con símbolos y leyenda descrita en el registro anterior.

## Pendientes vigentes

AUD-23 y AUD-25: revisión real de accesibilidad y móvil. AUD-28: política de fallos de proveedores. AUD-30: auxiliar PowerShell. AUD-31: revisiones de Actions. AUD-32: contenido del artefacto. AUD-33: medición del calendario. Publicación, credenciales, SEO y propuestas futuras se gestionan en [TODO general](../TODO.md).
