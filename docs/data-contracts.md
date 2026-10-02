# Contratos de datos y recursos

La construcción valida primero los cinco JSON públicos y después el artefacto completo. Un fallo indica archivo y campo (o línea HTML), detiene la construcción y conserva el _site anterior. No modifica ni corrige automáticamente las fuentes.

```sh
python scripts/validate_data.py
python scripts/build.py
python scripts/validate_resources.py
python scripts/validate.py --browser
```

validate_resources.py inspecciona _site ya generado. build.py ejecuta ambos validadores antes de instalar su salida. validate.py ejecuta también las regresiones y dos construcciones en una copia temporal. Este recorrido es offline.

## JSON

UTF-8 y JSON estricto: se rechazan claves repetidas, NaN e Infinity. Los diagnósticos de campos de redes no imprimen el valor de tokens ni URLs de imágenes.

| Archivo | Contrato |
| --- | --- |
| data/competitions.json | checked_at en YYYY-MM-DD y events como array, que puede estar vacío. Cada evento tiene id entero positivo único, name no vacío, start/end válidos con end >= start y url HTTPS de www.ifbbpro.com/competition/. city, country y description son cadenas opcionales, que pueden estar vacías. image_url, si tiene contenido, debe ser HTTPS. |
| data/competition-participation.json | Objeto indexado por ID existente. Cada valor tiene status pending/confirmed/absent; name es opcional y no vacío si se incluye. Sin decisión editorial, el renderizador usa pending. |
| data/competition-logos.json | Objeto indexado por ID existente, con rutas existentes bajo img/calendar/, sin ../, query ni fragmento. Sin asociación, la interfaz usa su respaldo. |
| data/youtube.json | channelId coincide con el actualizador; videos contiene seis IDs únicos de 11 caracteres válidos, title no vacío y publishedAt ISO con zona. Solo se admiten esos campos públicos en las entradas y channelId/videos y metadata opcional en la raíz. |
| data/instagram.json | username coincide con el actualizador; posts contiene tres IDs numéricos únicos, permalink HTTPS /p/ o /reel/ de www.instagram.com, media_type IMAGE/VIDEO/CAROUSEL_ALBUM y timestamp ISO con zona. media_url/thumbnail_url son opcionales; deben ser HTTPS del CDN de Instagram o Facebook y no incluir credenciales. No se admiten otros campos en las entradas ni en la raíz (username/posts y metadata opcional). |

Se validan todos los eventos antes del filtro Natural. Se rechazan asociaciones huérfanas, pero no se exige una asociación para cada evento. name en participación es una ayuda editorial y no se exige que coincida literalmente con el título importado.

El contrato no confirma la exactitud de fuentes externas ni disponibilidad remota. Las reglas de selección temporal de publicaciones siguen en los actualizadores.

## Recursos del artefacto

- HTML: src, href, srcset, poster, data-full-src, data-logo y og:image; IDs duplicados y fragmentos al mismo documento u otros HTML del artefacto.
- CSS: url(...) e imports entre comillas, relativos al CSS. Se omiten comentarios.
- JavaScript: literales entre comillas que empiezan por img/, css/ o js/, relativos a la portada. Cubre los respaldos actuales; no evalúa rutas calculadas.
- Rutas: existencia, contención dentro del sitio y mayúsculas exactas, también en Windows. Los directorios se resuelven a index.html. Las URLs del propio origen canónico se comprueban localmente.
- img/image-manifest.json: originales y variantes existentes; width/height/bytes enteros positivos; bytes coincide con el archivo; variantes sin rutas duplicadas. No se decodifican imágenes para verificar dimensiones reales ni se exige inventariar todo img/.
- sitemap.xml: XML urlset con namespace esperado, al menos una página, URLs HTTPS sin páginas duplicadas y páginas del origen canónico. Las páginas e imágenes del propio origen deben existir.

Las URLs externas, data: y otros esquemas no se descargan. Los fragmentos SVG, CSS escapado o dinámico, HTML construido por JavaScript y la validez completa de HTML/CSS quedan fuera de este comprobador. El origen se obtiene del único canonical de index.html, actualmente una URL HTTPS de raíz.

## Mantenimiento

Al renombrar una imagen, actualizar sus consumidores, manifiesto y sitemap, y ejecutar el validador. Si cambia un recurso inventariado, regenerar sus metadatos y variantes; no modificar bytes a ciegas para silenciar el error. La optimización reproducible de AUD-11 está implementada en `scripts/optimize_images.py` y su Action manual; comandos y política en [Imágenes](images.md).

## Procedencia de las instantáneas

metadata es opcional por compatibilidad. Si existe, contiene exactamente source y fetched_at. source es el proveedor correspondiente con fetched_at ISO y zona horaria, o legacy-cache con fetched_at null. Política de escritura, comparación y recuperación: [Instantáneas](snapshots.md).

## Actualizaciones IFBB

competitions.json admite metadata con source (endpoint público IFBB), fetched_at (fecha con zona), query_start/query_end (fechas inclusivas), fetched_total (entero positivo) y retained_missing_ids (IDs únicos conocidos conservados para revisión). checked_at coincide con el día de fetched_at. Las instantáneas antiguas sin metadata siguen siendo válidas. El validador puede recibir una instantánea candidata en memoria para comprobarla antes de escribir. Detalles de consulta y conservación en [Calendario](calendar.md).
