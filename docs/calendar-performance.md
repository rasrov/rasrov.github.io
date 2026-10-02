# Perfil del calendario — AUD-33

Medición local del 02/10/2026. Datos completos y huellas de fuentes en [calendar-2026-10-02.json](performance/calendar-2026-10-02.json).

## Alcance y método

Edge 154 headless en Windows; HTML regenerado desde el snapshot real, CSS y scripts reales, 90 eventos renderizados de los 102 del JSON (el filtro excluye naturales). Se recorren los 10 meses entre la primera y última fecha de inicio, con tres pasadas: 30 cambios de mes medidos por ejecución, además de movimientos de preparación no incluidos en los resúmenes. Los meses más cargados contienen 12 eventos. Después se realizan 101 pasos de scroll.

Ventanas de 1440 y 390 px, altura 900 px, DPR 1. Se ejecutan los navegadores secuencialmente; a 390 px se compara también CPU ralentizada ×4 y se repite esa comparación. No es un teléfono: mobile=false, motor de escritorio, sin emulación de red ni calibración a un dispositivo específico. Se bloquean peticiones HTTP/HTTPS externas y se mantienen los huecos de iframes sin cargar reproductores. Se espera a las fuentes disponibles; no se mide la carga completa del sitio ni servicios externos.

El auxiliar inserta marcas temporales exclusivamente en una copia del HTML, dentro de `sizeAgenda()` y `updateHero()`. El tiempo total de cambio mide el manejador síncrono del clic, no el fotograma presentado ni INP. `performance.now()` usa el reloj real mediante el auxiliar CDP existente de las pruebas. Los tiempos incluyen instrumentación y ruido del equipo; los percentiles con 30 muestras son orientativos. No se usa un umbral temporal como test de CI.

## Resultado

Milisegundos; P95 es el percentil 95 de cada ejecución.

| Escenario | Agenda mediana antes → después | Agenda P95 antes → después | Cambio de mes P95 antes → después |
| --- | --- | --- | --- |
| 1440 px, CPU ×1 | 1,5 → 1,2 | 2,1 → 1,9 | 2,6 → 2,9 |
| 390 px, CPU ×1 | 1,6 → 1,0 | 2,0 → 1,3 | 2,9 → 2,0 |
| 390 px, CPU ×4, primera comparación | 7,7 → 5,9 | 21,5 → 17,2 | 27,0 → 22,9 |
| 390 px, CPU ×4, repetición | 8,5 → 5,0 | 12,5 → 10,4 | 15,4 → 22,4 |

La mediana y P95 de la medición de tarjetas bajan en las cuatro comparaciones. El coste total de interacción no mejora de forma consistente; no se afirma una mejora general de fluidez ni de Core Web Vitals. La primera medición de arranque mezcla trabajo de layout inicial y no se usa como comparación aislada.

## Cambio aplicado y decisiones

`sizeAgenda()` insertaba una muestra, consultaba geometría y la retiraba antes de pasar a la siguiente, alternando escrituras y lecturas del DOM. Ahora prepara todas las muestras, las inserta juntas, lee sus alturas y después las retira. Mantiene el ancho actual, la altura máxima de todas las páginas, el ajuste tras cargar fuentes y la respuesta a resize. No añade caché, no cambia fechas, logos, paginación ni diseño.

Se añadió una regresión de navegador con una tarjeta larga situada en una página oculta: compara la altura calculada con la natural, verifica paginación, cambio de ancho, mes vacío y ausencia de clones residuales.

La agenda no ejecutó `sizeAgenda()` durante el scroll en las ocho mediciones. Las consultas de secciones están actualmente en `hero.js`, no en `main.js`; ya se agrupan mediante requestAnimationFrame. El P95 de `updateHero()` fue 1,8–2,3 ms a CPU ×1 y 8,9–13,7 ms a CPU ×4, con variación también en código que no cambió. Se conserva esa implementación: estas muestras no justifican añadir caché de geometrías ni cambiar la navegación.

## Repetir la medición

Desde la raíz, con Node.js 22+ y Edge/Chrome instalado:

```sh
python scripts/profile_calendar.py --browser "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --width 390 --cpu 4
python scripts/profile_calendar.py --browser "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --width 1440 --cpu 1
```

También admite BROWSER_BIN en lugar de --browser. La salida es JSON; guardarla fuera de los archivos públicos si se desean nuevas comparaciones. No cambia el checkout, no consulta IFBB ni redes sociales. Reutiliza `tests/browser_frames.mjs`; el modo habitual de pruebas mantiene su comportamiento anterior. Si dejan de coincidir los puntos de instrumentación, el auxiliar falla para exigir su revisión, en vez de medir silenciosamente otra cosa.

## Pendiente para cerrar AUD-33

Repetir las interacciones en un **teléfono real** con el contenido publicado: registrar modelo, sistema, navegador, red y versión probada, trazar cambios de mes (incluidos los más cargados), paginación, rotación y scroll. Comparar trazas de layout y tareas largas, respuesta táctil y estabilidad de alturas. Las mediciones actuales no sustituyen ese paso. AUD-33 permanece abierto por esta comprobación; no se necesita añadir más optimizaciones sin evidencia nueva.
