# TODO — Kim Angel

Estado consolidado: 02/10/2026. Mantener una única landing y su diseño. Las tareas técnicas se gestionan exclusivamente en [TODO técnico](docs/TODO-revision-tecnica.md); no se duplican aquí. Instrucciones operativas en [README](README.md). Las comprobaciones anteriores se conservan en el [registro histórico](docs/todo-history-2026-10-02.md).

## Publicación y operación pendientes

- [ ] Subir los cambios locales y verificar la ejecución del workflow de publicación actualizado y la web resultante: tarjetas de Instagram e imágenes remotas, reproducción de YouTube, calendario, animaciones y correcciones móviles. La activación anterior de redes fue confirmada por el usuario; no confirma la publicación de estos cambios.
- [ ] Activar y comprobar la primera ejecución remota de **Refresh IFBB competitions**: actualización del JSON y posterior publicación de Pages. Procedimiento en [Calendario](docs/calendar.md).
- [ ] Subir **Optimize images on demand** y verificar su primera ejecución manual, previsualización y PR. No programarlo. Procedimiento en [Imágenes](docs/images.md).
- [ ] Registrar la fecha exacta de vencimiento del token de Instagram y renovarlo cuando corresponda, sin guardar el token en documentación. Procedimiento en [Instagram](docs/instagram.md).
- [ ] Comprobar la respuesta pública de robots.txt.
- [ ] Revisar el procesamiento del sitemap y la indexación de la página e imágenes en Search Console. El envío del sitemap y la solicitud de indexación fueron confirmados; no equivalen a indexación efectiva. No reenviar repetidamente.

La validación en teléfono real, zoom, lector de pantalla, contraste y tacto pertenece a **AUD-23/AUD-25**, con un único [protocolo de revisión manual](docs/accessibility.md). Incluye la landing completa, galerías, visor, calendario, menú, copia de descuentos, orientación y desplazamiento. Medir rendimiento del calendario corresponde a **AUD-33**.

## Contenido y SEO — aplazados

- [ ] Revisar presentación, biografía, resultados y descuentos para confirmar exactitud y actualidad; identificar claramente a Kim Angel y Classic Physique.
- [ ] Enriquecer el Hall of Fame con contexto breve y verificado de las competiciones: año, resultado y participación, conservando las tarjetas y galerías.
- [ ] Relacionar consultas relevantes con contenido útil en títulos, texto visible y descripciones, sin repeticiones artificiales ni textos ocultos. El sitemap enumera URLs e imágenes, no palabras clave.
- [ ] Cuando Search Console acumule datos, analizar consultas, impresiones, clics, CTR y posición media para priorizar mejoras.
- [ ] Valorar enlaces auténticos desde perfiles de Kim o patrocinadores si colaboran. No presentar la web como oficial sin autorización ni contactar a terceros sin indicación del usuario.
- [ ] Añadir contacto profesional cuando el usuario facilite un correo autorizado.

No se garantizan posiciones en las búsquedas. Al retomar el contenido, comenzar por la presentación y el contexto del Hall of Fame.

## Propuestas futuras — sin implementación autorizada

- [ ] Valorar S3, CloudFront y dominio de recursos; si se adopta, configurar acceso público de lectura, subir originales/variantes con tipos y caché adecuados, migrar URLs y comprobar referencias.
- [ ] Valorar centralizar datos de campeonatos, patrocinadores y publicaciones manteniendo HTML rastreable.
- [ ] Evaluar un catálogo propio de campeonatos con identidad interna y alias revisados para asociar logos independientemente del ID de IFBB. La asociación por nombre sigue aplazada: comprobar estabilidad de IDs y comparar alternativas ante homónimos, cambios de nombre, ediciones, categorías y ubicaciones. Si se adopta, coincidencias aproximadas solo como sugerencias; casos ambiguos con imagen genérica y revisión manual. Separar campeonato y edición para no trasladar participación entre años; permitir logos por edición y validar con casos reales.
- [ ] Definir métricas de visitas, procedencia, galerías, clics en patrocinadores y copias de descuentos; valorar un backoffice autenticado.
- [ ] Elegir un dominio propio y planificar URLs, metadatos y Search Console.
- [ ] Valorar repositorio privado, alojamiento y organización de futuras webs.

## Confirmaciones previas y alcance

El usuario confirmó anteriormente el despliegue de optimizaciones de imágenes, la activación de YouTube e Instagram, el acceso al sitemap y la configuración de Search Console. Las pruebas locales y los cambios posteriores no demuestran que la versión publicada esté actualizada. El registro histórico conserva fechas, medidas y resultados sin convertirlos en verificaciones nuevas. El estado técnico y la última validación constan en el TODO técnico.
