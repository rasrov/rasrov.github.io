# YouTube automático

La web muestra seis publicaciones públicas recientes del canal Kim Angel, ordenadas por fecha. La API consulta los uploads sin filtrar por duración: admite vídeos y Shorts. No se etiqueta un vídeo como Short basándose solo en su duración.

Se excluyen privados, no insertables, publicaciones futuras y directos en emisión. La selección inicial procedía del feed público; posteriormente el usuario confirmó el funcionamiento de la API y la automatización. Esto no certifica la disponibilidad actual de cada vídeo ni sustituye la comprobación de reproducción publicada pendiente en el [TODO general](../TODO.md).

## Credencial para una instalación nueva o su renovación

1. En https://console.cloud.google.com/ crea o selecciona un proyecto y activa YouTube Data API v3.
2. En APIs y servicios → Credenciales crea una clave de API. Restringe su uso a YouTube Data API v3. Se utiliza desde GitHub Actions: no uses restricciones por referente HTTP de una web.
3. En el repositorio: Settings → Secrets and variables → Actions → New repository secret. Crea YOUTUBE_API_KEY con esa clave. No la incluyas en archivos ni la envíes por el chat.

La activación de Pages y la ejecución del workflow compartido se describen una sola vez en [Publicación y secretos](../README.md#publicación-y-secretos). Su nombre actual es **Publish website and refresh social feeds**. La configuración anterior ya fue confirmada; no es una nueva tarea pendiente de activación de YouTube.

## Funcionamiento

- Disparadores y horario en la [tabla de workflows](../README.md#publicación-y-secretos); los PR solo validan. Revisar los registros de Actions si no se actualiza la selección.
- Genera HTML estático y data/youtube.json durante el despliegue. No crea commits: la instantánea local puede ser anterior a la publicada. Cada ejecución del job build de Pages consulta YouTube de nuevo.
- Consulta hasta cuatro páginas de uploads, de 50 elementos, cuando necesita saltar contenido no disponible para obtener seis.
- Los iframes conservan youtube-nocookie, carga diferida y referrerpolicy. Cada tarjeta enlaza también a YouTube por si existen restricciones regionales o del reproductor.
- Si falta la clave, falla la API o no hay seis resultados válidos, el job falla antes de publicar y la web anterior permanece disponible. Revisar Actions.
- Construcción y contenido público documentados en [README](../README.md#construcción-offline).
- No requiere acceso a la cuenta del atleta.

## Desarrollo local

El actualizador utiliza la biblioteca estándar de Python 3.12 o posterior. La validación completa requiere las dependencias indicadas en el [README](../README.md#validación-antes-de-publicar). Para probar únicamente este módulo y regenerar desde datos guardados:

    python -B -m unittest discover -s tests -p test_update_youtube.py -v
    python scripts/update_youtube.py --from-cache

Para consultar la API, proporciona YOUTUBE_API_KEY mediante el entorno y ejecuta sin --from-cache. Nunca guardes la clave en el repositorio.

## Referencias

- https://developers.google.com/youtube/v3/docs/channels/list
- https://developers.google.com/youtube/v3/docs/playlistItems/list
- https://developers.google.com/youtube/v3/docs/videos/list
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Procedencia y escritura

Las nuevas consultas guardan metadata.source y metadata.fetched_at UTC. --from-cache conserva el JSON y solo regenera HTML. Los destinos se preparan con respaldos y restauración ante fallos. Comparación con publicado y recuperación de interrupciones: [Instantáneas](snapshots.md).
