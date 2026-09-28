# TODO — Kim Angel

Mantener una única landing y conservar su diseño, carruseles y ampliación de imágenes. Proyecto actual: C:\Users\rasul\Documents\rasrov.github.io. Web publicada en https://rasrov.github.io/. Estado actualizado según las confirmaciones del usuario.

## Ya realizado

- [x] Renombrar las 35 fotos del Hall of Fame con atleta, competición, año y número, manteniendo las carpetas y actualizando sus referencias.
- [x] Incluir las 35 fotos en el HTML con src, alt contextual, dimensiones y carga diferida; adaptar el carrusel para usar esos elementos.
- [x] Comprobar que las rutas de las fotos existen y que JavaScript tiene sintaxis válida. Comprobación visual y de descargas locales realizada; alcance detallado al final.

## Próximo paso: SEO sin depender de S3

- [x] Revisar encabezados: un H1 que identifique a Kim Angel y Classic Physique, y jerarquía coherente de títulos de las secciones, conservando el diseño.
- [x] Mejorar la descripción y los metadatos de la landing, conservando el título «Kim Angel Pro Athlete».
- [x] Revisar visualmente cada foto y afinar sus textos alt para describir lo que muestra, además del campeonato; evitar descripciones inventadas y repetición artificial de palabras clave.
- [x] Generar localmente copias optimizadas y redimensionadas para móvil sin sobrescribir los originales. Definir tamaños según el uso real y conservar transparencias donde sean necesarias.
- [x] Preparar un inventario que relacione cada original con sus variantes y configurar srcset y sizes, con src de respaldo. Estas tareas pueden hacerse antes de S3.
- [x] Revisar dimensiones y carga diferida del resto de las imágenes; usar una versión adecuada de mayor resolución al ampliar fotografías.
- [x] Comprobar en navegador las siete galerías: apertura, cambio de foto, cierre, ampliación, teclado y controles táctiles; verificar el diseño en móvil y escritorio.
- [x] Medir las descargas locales y confirmar que las fotos inactivas no se descargan antes de abrir la galería; diferir Instagram hasta acercarse a su sección y conservar la carga diferida de YouTube.
- [ ] Comprobar reproducción y carga real de Instagram y YouTube en GitHub Pages; los servicios externos se aislaron en las pruebas locales.
- [x] Revisar foco al abrir/cerrar galerías, navegación con flechas, Escape, gesto táctil y ausencia de desbordamiento a 390 y 1440 px; añadir enlace para saltar al contenido y foco visible.
- [ ] Completar auditoría de accesibilidad con lector de pantalla y contraste sobre fotografías y contenido externo.

## Más adelante: imágenes en S3

- [ ] Crear y configurar un bucket para alojar las imágenes; definir cómo se servirán públicamente sin permitir escrituras públicas. Valorar CloudFront y un dominio para los archivos.
- [ ] Subir originales y variantes con tipos de contenido y caché adecuados.
- [ ] Actualizar las URLs del sitio manteniendo las variantes responsive y comprobar todas las referencias.

## Publicación en https://rasrov.github.io/

- [x] Configurar la URL canónica y completar los metadatos que requieran URLs públicas definitivas.
- [x] Preparar sitemap.xml (una página y sus imágenes, con originales de las galerías) y robots.txt para https://rasrov.github.io/. XML y rutas locales comprobados.
- [x] Publicar sitemap.xml y robots.txt en el repositorio. Acceso público al sitemap confirmado por el usuario.
- [ ] Comprobar expresamente la respuesta pública de robots.txt.
- [x] Verificar la propiedad de prefijo de URL https://rasrov.github.io/ en Google Search Console mediante google7c05621a1821ef9c.html. Conservar el archivo.
- [x] Enviar sitemap.xml a Search Console; envío correcto confirmado por el usuario.
- [x] Probar la URL publicada: Google indica «La URL está disponible para Google».
- [x] Solicitar indexación de la portada; Google confirma que está en la cola de rastreo prioritaria.
- [ ] Revisar posteriormente el procesamiento del sitemap y la indexación de la página y sus imágenes. La solicitud aceptada no confirma indexación ni posiciones. No reenviar repetidamente.

La optimización facilita el descubrimiento y la comprensión del contenido, pero no garantiza posiciones en las búsquedas.

## Validación local — 28 de septiembre de 2026

- 45 originales conservados y 127 variantes WebP en `img/optimized`; inventario en `img/image-manifest.json`.
- 35 descripciones de fotos revisadas visualmente; un H1 accesible que identifica al atleta y H2 para Instagram. Título del navegador conservado.
- Siete carruseles probados con Edge sin interfaz en 1440 y 390 px: todas las fotos, ampliación, cierre, foco, flechas y gesto táctil simulado. Sin errores JavaScript ni desbordamiento horizontal. Capturas revisadas.
- Descarga inicial local: aproximadamente 4,01 → 1,68 MB en escritorio y 3,84 → 1,57 MB en móvil, DPR 1. Excluye contenido externo; no es una medición de Lighthouse ni de la web pública.
- No se descargaron fotos inactivas antes de abrir las galerías. El visor ampliado utiliza los originales.
- Metadatos Open Graph y URL canónica preparados para la dirección indicada por el usuario.
- [x] Subir las optimizaciones y `img/optimized` a GitHub Pages; despliegue confirmado por el usuario. El repositorio actual es C:\Users\rasul\Documents\rasrov.github.io.

## Siguientes mejoras propuestas

- [ ] Priorizar revisión en un móvil real: legibilidad, botones, menú, desplazamiento entre secciones, galerías y velocidad con datos móviles.
- [ ] Completar la revisión de accesibilidad y embeds publicada pendiente arriba.
- [ ] Añadir contacto profesional para colaboraciones o patrocinio cuando el usuario facilite un correo autorizado.
- [x] Preparar sección de seis publicaciones de YouTube, incluidos Shorts, con consulta de uploads mediante API y despliegue cada seis horas. Guía: docs/youtube.md.
- [ ] Activar YouTube Data API v3 y guardar YOUTUBE_API_KEY como secreto de Actions.
- [ ] Subir la implementación, cambiar Settings → Pages → Source a GitHub Actions y ejecutar el workflow; validar la consulta real de API y la reproducción publicada.
- [ ] Revisar después la actualización automática de Instagram (sin cambios en esta tarea).
- [ ] Valorar centralizar datos de campeonatos, patrocinadores y publicaciones para facilitar el mantenimiento sin perder el HTML rastreable.


## YouTube automático — implementación local

- Seis tarjetas precargadas con publicaciones reales recuperadas del feed del canal; última publicación de la selección: 27/09/2026.
- Actualizador con siete pruebas unitarias aprobadas: orden, duplicados, contenido no disponible, Shorts sin filtro de duración, paginación y escape HTML/errores sin secretos.
- Cuadrícula comprobada a 1440, 900 y 390 px (3/2/1 columnas), sin errores JavaScript ni desbordamiento. Servicios externos aislados: reproducción y API real pendientes de activación.
- Workflow genera HTML y JSON durante el despliegue, sin commits automáticos. Un fallo conserva la web publicada. La configuración remota de Pages no se ha modificado.
