# Optimización de imágenes bajo demanda

El workflow **Optimize images on demand** (`.github/workflows/optimize-images.yml`) solo tiene `workflow_dispatch`: no se ejecuta por horario, push ni al publicar la web.

## Ejecución en GitHub

1. Subir estos cambios a la rama predeterminada del repositorio.
2. En Settings → Actions → General, permitir a GitHub Actions crear pull requests. El workflow utiliza `GITHUB_TOKEN`; no necesita un secreto adicional.
3. Abrir Actions → Optimize images on demand → Run workflow y seleccionar la rama predeterminada.
4. Dejar `source` vacío para procesar las imágenes referenciadas o indicar un original, por ejemplo `img/calendar/arnold-uk.png`. Dejar `force` desactivado normalmente.
5. Revisar la PR y el artefacto `optimized-website-preview`. Fusionar o cerrar la PR antes de repetir la ejecución para evitar propuestas duplicadas.

La ejecución valida el proyecto, genera una previsualización y abre una PR si hay cambios. No fusiona ni publica directamente. Las ejecuciones desde otras ramas se omiten. Las PR creadas con `GITHUB_TOKEN` no disparan normalmente otros workflows: por eso las pruebas completas se ejecutan dentro de este Action antes de abrir la PR. La fusión humana en main activa el flujo de publicación habitual.

## Uso local

```sh
python -m pip install -r requirements-images.txt
python scripts/optimize_images.py --dry-run
python scripts/optimize_images.py
python scripts/optimize_images.py --source img/calendar/arnold-uk.png
```

`--dry-run` prepara y valida en una carpeta temporal sin instalar los resultados. `--force` regenera incluso las variantes existentes. No ejecutar simultáneamente con otros actualizadores en el mismo checkout.

## Política de generación

- Descubre originales PNG/JPEG/WebP del manifiesto, de los elementos `img` del HTML y de las asociaciones de logos. SVG, favicon, imágenes remotas y archivos sin referencia no se convierten automáticamente. `--source` permite incorporar un original concreto al inventario.
- Conserva los originales, enlaces de galería a tamaño completo y sitemap. No elimina variantes antiguas, evitando romper referencias externas.
- Reutiliza las anchuras existentes. Para nuevas fotos usa 480/960/1440 px; para logos, 160/320/640 px. Nunca amplía un original más pequeño.
- Genera WebP con Lanczos, calidad 82 y método 6; logos de calendario, patrocinadores y nombres con `logo` utilizan compresión sin pérdidas. Conserva transparencia, aplica orientación EXIF y preserva perfiles ICC; convierte perfiles CMYK a sRGB. Las imágenes animadas se rechazan.
- Actualiza dimensiones, bytes, variantes y huellas SHA-256 en `img/image-manifest.json`, atributos `src`/`srcset` y dimensiones del HTML, y rutas en `data/competition-logos.json`. Conserva `sizes` existente; si falta utiliza `100vw`. Los logos del calendario utilizan la primera variante de al menos 320 px, o la mayor disponible.
- Pillow está fijado en `requirements-images.txt`; su versión y la de libwebp quedan registradas con los parámetros de conversión. Un cambio de original, variante o receta provoca regeneración; sin cambios no escribe archivos.
- La primera ejecución adopta las variantes heredadas si coinciden dimensiones y tamaños de archivo, sin recomprimirlas. No puede demostrar que se generaron con el contenido original actual ni recuperar sus parámetros históricos. Se identifican como `adopted-existing`; usar `--force` si se desea reconstruirlas con la receta documentada.

Los resultados se validan en una copia temporal antes de escribir. La instalación reutiliza el mecanismo de respaldos y recuperación de los actualizadores; ante un fallo restaura los archivos anteriores. Las instrucciones de recuperación de `.snapshot-update` están en [Instantáneas](snapshots.md).

Las pruebas de imágenes requieren Pillow; la validación general las omite si no está instalado. El Action manual instala esta dependencia y ejecuta las pruebas, incluidas las regresiones de navegador. La previsualización permite revisar encuadre, color y peso antes de fusionar.

## Nombres y compatibilidad de URLs (AUD-15)

La migración del 02/10/2026 normaliza 173 rutas de originales y variantes sin modificar sus bytes:

| Antes | Nombre canónico |
| --- | --- |
| `img/hall_of_fame/` | `img/hall-of-fame/` |
| `arnold_classic_uk_2026/` y `arnold_classic_usa_2026/` | `arnold-classic-uk-2026/` y `arnold-classic-usa-2026/` |
| `evls_prague_pro_25/` | `evls-prague-pro-2025/` |
| `atlanta_pro_2025/`, `olympia_2025/`, `tupelo_pro_2024/`, `tupelo_pro_2025/` | Los mismos nombres en kebab-case y años de cuatro cifras |
| `web_main_image_raw.png` | `hero-background.png` |
| `web_main_kim.png` | `kim-angel-hero.png` |
| `web_main_kim_logo.png` | `kim-angel-logo.png` |
| `web_main_about_kim.png` | `kim-angel-about.png` |
| `web_main_about_kim_1.jpg` | `kim-angel-about-alternative.jpg` |
| `web_main_rp_strenght_logo.png` | `rp-strength-logo.png` |
| Otros `web_main_*_logo.png` | Nombre del patrocinador en kebab-case seguido de `-logo.png` |

Las variantes de `img/optimized/` siguen los mismos nombres. HTML, `srcset`, enlaces del visor, Open Graph, sitemap e inventario utilizan las rutas canónicas. Los identificadores internos `data-gallery` se conservan: no son rutas de archivos.

`img/image-aliases.json` registra cada URL antigua y su destino. `scripts/image_aliases.py`, invocado por el constructor, genera copias idénticas **solo en `_site/`**. Git conserva una sola imagen por recurso. Esto mantiene enlaces antiguos al publicar mediante el build; un servidor servido directamente desde la raíz del checkout no incluye esos alias. Para previsualizar, servir `_site/` como indica el README.

Los alias no son redirecciones HTTP y aumentan el tamaño del artefacto; no duplican las descargas de la página, que referencia las URLs nuevas. El build rechaza destinos ausentes, rutas fuera de `img/`, cadenas de alias y colisiones con archivos fuente. No añadir las rutas antiguas al inventario de optimización ni mantener copias manuales. Al renombrar otra imagen, actualizar todos sus consumidores y el mapa de compatibilidad.

AUD-16 elimina posteriormente las dos imágenes sin uso por indicación del usuario, junto con el alias de la foto alternativa. Quedan 172 alias; el resto de la compatibilidad de AUD-15 se conserva.

## Inventario de uso y recursos retirados (AUD-16, 02/10/2026)

Se revisaron las 184 imágenes de `img/` contra las referencias del HTML (incluidos metadatos, srcset y visor), CSS, JavaScript, JSON del calendario, sitemap y scripts. Se cruzaron también el manifiesto de optimización y el mapa de alias. No se encontraron duplicados exactos por SHA-256. Tras retirar los dos recursos sin uso quedan **182 imágenes**. Los archivos JSON de inventario no se cuentan como imágenes.

| Grupo | Cantidad | Propósito y referencias | Decisión |
| --- | ---: | --- | --- |
| Originales del manifiesto | 45 | 35 fotos de galerías, 6 logos de patrocinadores y 4 imágenes de portada/biografía. Fuentes de las variantes; algunas también enlazadas desde visor, sitemap o metadatos. | Conservar aunque una fuente no tenga un `src` directo. |
| Variantes WebP del manifiesto | 127 | `src`/`srcset` del HTML y relación original-variante en `img/image-manifest.json`. | Conservar; la optimización reutiliza estas variantes. |
| Logos actuales del calendario | 8 | `data/competition-logos.json`; renderizados en los eventos y utilizados por `js/calendar.js`. | Conservar. |
| Imagen predeterminada del calendario | 1 | `img/calendar/default-championship.png`, respaldo declarado en `js/calendar.js`. | Conservar. |
| Favicon PNG | 1 | `img/favicon-96.png`, enlazado en el head. El favicon ICO de la raíz queda fuera de este recuento. | Conservar. |
| Recursos retirados por falta de uso | 2 eliminados | Detallados a continuación; no incluidos en las 182 imágenes actuales. | Eliminados junto con el alias asociado. |

### Casos que motivaron la auditoría

| Recurso | Evidencia | Estado y tratamiento |
| --- | --- | --- |
| `img/hero-background.png`, antes `web_main_image_raw.png` | Sus cuatro variantes se usan en la portada; la de 960 px figura también en sitemap. | Original necesario para regenerar variantes. El antiguo nombre `raw` no significaba archivo sobrante. |
| `img/kim-angel-about-alternative.jpg`, antes `web_main_about_kim_1.jpg` | Fotografía vertical en blanco y negro, distinta de la foto actual. Sin referencias activas ni entrada en el manifiesto. Tenía un alias desde la URL antigua. | Eliminada junto con `img/web_main_about_kim_1.jpg` del mapa de alias. La foto visible no cambia. |
| `img/calendar/multiple-championships-v2.png` | Silueta utilizada anteriormente para días con varias competiciones. Sin referencias actuales en HTML, CSS, JS, datos, sitemap o scripts. | Eliminado por falta de uso. El calendario usa el primer logo propio disponible y, si no existe, la imagen predeterminada. |
| `img/calendar/multiple-championships.png` | Ausente del checkout y de los mapas de recursos actuales. | Ya retirado antes de esta revisión. No restaurar ni crear una asociación nueva. |

Por indicación del usuario se eliminan los dos archivos sin uso y el alias de la foto alternativa. Se retiran **452.264 bytes** de fuentes y **543.930 bytes** del artefacto, incluida la copia del alias. Sus URLs dejarán de estar disponibles cuando se publiquen los cambios; no se crean redirecciones ni imágenes sustitutas. El calendario y la biografía no los referencian. La revisión general del contenido público sigue en AUD-32.

Huellas SHA-256 de los archivos retirados, conservadas como registro de la auditoría:

- `kim-angel-about-alternative.jpg`: `35fe5e3dabe6e5663ab14a55d8bc97934c1b46b5d0c5fc80ddcd315a1e665a10`.
- `multiple-championships-v2.png`: `9bc83a2a5f59b70ac7ffe7ce9d15370ef4123a5b12899cf5df85993b199ed174`.

Para repetir la revisión, cruzar las rutas de `img/` con los consumidores anteriores, el manifiesto y los destinos de los alias. Las coincidencias en documentación histórica no implican uso visual; la ausencia de un `src` directo no basta para borrar una fuente del optimizador. Comprobar finalmente formato, build y referencias mediante los comandos documentados.
