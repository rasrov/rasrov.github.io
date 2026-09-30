# YouTube automático

La web muestra seis publicaciones públicas recientes del canal Kim Angel, ordenadas por fecha. La API consulta los uploads sin filtrar por duración: admite vídeos y Shorts. No se etiqueta un vídeo como Short basándose solo en su duración.

Se excluyen privados, no insertables, publicaciones futuras y directos en emisión. Los seis iniciales proceden del feed público real; su disponibilidad no se ha comprobado aún mediante la API.

## Activación (una sola vez)

1. En https://console.cloud.google.com/ crea o selecciona un proyecto y activa YouTube Data API v3.
2. En APIs y servicios → Credenciales crea una clave de API. Restringe su uso a YouTube Data API v3. Se utiliza desde GitHub Actions: no uses restricciones por referente HTTP de una web.
3. En el repositorio: Settings → Secrets and variables → Actions → New repository secret. Crea YOUTUBE_API_KEY con esa clave. No la incluyas en archivos ni la envíes por el chat.
4. Sube los cambios a main, incluido .github/workflows/pages.yml.
5. En Settings → Pages → Build and deployment → Source, cambia Deploy from a branch por GitHub Actions.
6. En Actions → Publish website and refresh YouTube → Run workflow, ejecuta el flujo y comprueba que build y deploy terminan correctamente.

Mantén la publicación actual hasta tener preparada la clave y el workflow. Esta tarea no ha cambiado la configuración remota.

## Funcionamiento

- Cada push a main, manualmente y cada seis horas (00:23, 06:23, 12:23 y 18:23 UTC). GitHub puede retrasar ejecuciones programadas.
- En repositorios públicos GitHub puede desactivar el horario tras 60 días sin actividad; revisar Actions si deja de actualizarse.
- Genera HTML estático y data/youtube.json durante el despliegue. No crea commits: la instantánea local puede ser anterior a la publicada. Cada despliegue consulta YouTube de nuevo.
- Consulta hasta cuatro páginas de uploads, de 50 elementos, cuando necesita saltar contenido no disponible para obtener seis.
- Los iframes conservan youtube-nocookie, carga diferida y referrerpolicy. Cada tarjeta enlaza también a YouTube por si existen restricciones regionales o del reproductor.
- Si falta la clave, falla la API o no hay seis resultados válidos, el job falla antes de publicar y la web anterior permanece disponible. Revisar Actions.
- El paquete público incluye index, css, js, img, data, robots, sitemap, verificación Google y CNAME si existe; excluye scripts, tests y credenciales.
- Utiliza deploy-pages: los commits realizados con GITHUB_TOKEN no disparan por sí solos la publicación clásica de Pages.
- No requiere acceso a la cuenta del atleta.

## Desarrollo local

Python 3.12 o posterior, sin dependencias:

    python -m unittest discover -s tests -v
    python scripts/update_youtube.py --from-cache

Para consultar la API, proporciona YOUTUBE_API_KEY mediante el entorno y ejecuta sin --from-cache. Nunca guardes la clave en el repositorio.

## Referencias

- https://developers.google.com/youtube/v3/docs/channels/list
- https://developers.google.com/youtube/v3/docs/playlistItems/list
- https://developers.google.com/youtube/v3/docs/videos/list
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Procedencia y escritura

Las nuevas consultas guardan metadata.source y metadata.fetched_at UTC. --from-cache conserva el JSON y solo regenera HTML. Los destinos se preparan con respaldos y restauración ante fallos. Comparación con publicado y recuperación de interrupciones: [Instantáneas](snapshots.md).
