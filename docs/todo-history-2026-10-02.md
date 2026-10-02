# Registro histórico del TODO general

Copia conservada al consolidar AUD-29 el 02/10/2026. Describe decisiones y comprobaciones de distintas fechas; **no es una lista operativa vigente ni confirma el estado actual de GitHub**. Los pendientes activos están en [TODO general](../TODO.md) y [auditoría técnica](TODO-revision-tecnica.md). Los recuentos y nombres antiguos se mantienen como evidencia histórica.

---

# TODO — Kim Angel

Mantener una única landing y conservar su diseño, carruseles y ampliación de imágenes. Proyecto actual: C:\Users\rasul\Documents\rasrov.github.io. Web publicada en https://rasrov.github.io/. Estado actualizado según las confirmaciones del usuario.

## Ya realizado

- Realizado según el registro: Renombrar las 35 fotos del Hall of Fame con atleta, competición, año y número, manteniendo las carpetas y actualizando sus referencias.
- Realizado según el registro: Incluir las 35 fotos en el HTML con src, alt contextual, dimensiones y carga diferida; adaptar el carrusel para usar esos elementos.
- Realizado según el registro: Comprobar que las rutas de las fotos existen y que JavaScript tiene sintaxis válida. Comprobación visual y de descargas locales realizada; alcance detallado al final.

## Próximo paso: SEO sin depender de S3

- Realizado según el registro: Revisar encabezados: un H1 que identifique a Kim Angel y Classic Physique, y jerarquía coherente de títulos de las secciones, conservando el diseño.
- Realizado según el registro: Mejorar la descripción y los metadatos de la landing, conservando el título «Kim Angel Pro Athlete».
- Realizado según el registro: Revisar visualmente cada foto y afinar sus textos alt para describir lo que muestra, además del campeonato; evitar descripciones inventadas y repetición artificial de palabras clave.
- Realizado según el registro: Generar localmente copias optimizadas y redimensionadas para móvil sin sobrescribir los originales. Definir tamaños según el uso real y conservar transparencias donde sean necesarias.
- Realizado según el registro: Preparar un inventario que relacione cada original con sus variantes y configurar srcset y sizes, con src de respaldo. Estas tareas pueden hacerse antes de S3.
- Realizado según el registro: Revisar dimensiones y carga diferida del resto de las imágenes; usar una versión adecuada de mayor resolución al ampliar fotografías.
- Realizado según el registro: Comprobar en navegador las siete galerías: apertura, cambio de foto, cierre, ampliación, teclado y controles táctiles; verificar el diseño en móvil y escritorio.
- Realizado según el registro: Medir las descargas locales y confirmar que las fotos inactivas no se descargan antes de abrir la galería; usar carga diferida nativa en las imágenes de Instagram y conservar la carga diferida de YouTube.
- Pendiente registrado entonces: Comprobar las nuevas tarjetas de Instagram y la reproducción de YouTube en GitHub Pages tras publicar los últimos cambios; las imágenes de Instagram ya cargan en el navegador local.
- Realizado según el registro: Revisar foco al abrir/cerrar galerías, navegación con flechas, Escape, gesto táctil y ausencia de desbordamiento a 390 y 1440 px; añadir enlace para saltar al contenido y foco visible.
- Pendiente registrado entonces: Completar auditoría de accesibilidad con lector de pantalla y contraste sobre fotografías y contenido externo.

## Más adelante: imágenes en S3

- Pendiente registrado entonces: Crear y configurar un bucket para alojar las imágenes; definir cómo se servirán públicamente sin permitir escrituras públicas. Valorar CloudFront y un dominio para los archivos.
- Pendiente registrado entonces: Subir originales y variantes con tipos de contenido y caché adecuados.
- Pendiente registrado entonces: Actualizar las URLs del sitio manteniendo las variantes responsive y comprobar todas las referencias.

## Publicación en https://rasrov.github.io/

- Realizado según el registro: Configurar la URL canónica y completar los metadatos que requieran URLs públicas definitivas.
- Realizado según el registro: Preparar sitemap.xml (una página y sus imágenes, con originales de las galerías) y robots.txt para https://rasrov.github.io/. XML y rutas locales comprobados.
- Realizado según el registro: Publicar sitemap.xml y robots.txt en el repositorio. Acceso público al sitemap confirmado por el usuario.
- Pendiente registrado entonces: Comprobar expresamente la respuesta pública de robots.txt.
- Realizado según el registro: Verificar la propiedad de prefijo de URL https://rasrov.github.io/ en Google Search Console mediante google7c05621a1821ef9c.html. Conservar el archivo.
- Realizado según el registro: Enviar sitemap.xml a Search Console; envío correcto confirmado por el usuario.
- Realizado según el registro: Probar la URL publicada: Google indica «La URL está disponible para Google».
- Realizado según el registro: Solicitar indexación de la portada; Google confirma que está en la cola de rastreo prioritaria.
- Pendiente registrado entonces: Revisar posteriormente el procesamiento del sitemap y la indexación de la página y sus imágenes. La solicitud aceptada no confirma indexación ni posiciones. No reenviar repetidamente.

La optimización facilita el descubrimiento y la comprensión del contenido, pero no garantiza posiciones en las búsquedas.

## Validación local — 28 de septiembre de 2026

- 45 originales conservados y 127 variantes WebP en `img/optimized`; inventario en `img/image-manifest.json`.
- 35 descripciones de fotos revisadas visualmente; un H1 accesible que identifica al atleta y H2 para Instagram. Título del navegador conservado.
- Siete carruseles probados con Edge sin interfaz en 1440 y 390 px: todas las fotos, ampliación, cierre, foco, flechas y gesto táctil simulado. Sin errores JavaScript ni desbordamiento horizontal. Capturas revisadas.
- Descarga inicial local: aproximadamente 4,01 → 1,68 MB en escritorio y 3,84 → 1,57 MB en móvil, DPR 1. Excluye contenido externo; no es una medición de Lighthouse ni de la web pública.
- No se descargaron fotos inactivas antes de abrir las galerías. El visor ampliado utiliza los originales.
- Metadatos Open Graph y URL canónica preparados para la dirección indicada por el usuario.
- Realizado según el registro: Subir las optimizaciones y `img/optimized` a GitHub Pages; despliegue confirmado por el usuario. El repositorio actual es C:\Users\rasul\Documents\rasrov.github.io.

## Siguientes mejoras propuestas

- Pendiente registrado entonces: Priorizar revisión en un móvil real: legibilidad, botones, menú, desplazamiento entre secciones, galerías y velocidad con datos móviles.
- Pendiente registrado entonces: Completar la revisión de accesibilidad y contenido externo publicado pendiente arriba.
- Pendiente registrado entonces: Añadir contacto profesional para colaboraciones o patrocinio cuando el usuario facilite un correo autorizado.
- Realizado según el registro: Preparar sección de seis publicaciones de YouTube, incluidos Shorts, con consulta de uploads mediante API y despliegue cada seis horas. Guía: docs/youtube.md.
- Realizado según el registro: Activar YouTube Data API v3 y guardar YOUTUBE_API_KEY; funcionamiento confirmado por el usuario.
- Realizado según el registro: Activar la automatización de YouTube en GitHub Actions; el usuario confirmó que funciona.
- Realizado según el registro: Probar Business Discovery para kim_angel con Facebook Login; consulta correcta compartida por el usuario.
- Realizado según el registro: Preparar actualizador de tres publicaciones de Instagram y añadirlo al horario de GitHub Actions. Guía: docs/instagram.md.
- Realizado según el registro: Obtener token de usuario de larga duración y guardar INSTAGRAM_ACCESS_TOKEN en GitHub Secrets; configuración y actualización correcta confirmadas por el usuario.
- Realizado según el registro: Ejecutar el workflow de Instagram: primera actualización correcta confirmada por el usuario.
- Realizado según el registro: Sustituir embeds por tarjetas propias 4:5 con imágenes remotas, iconos por tipo y enlace a Instagram; diseño aprobado por el usuario.
- Pendiente registrado entonces: Publicar y verificar las nuevas tarjetas en GitHub Pages.
- Pendiente registrado entonces: Registrar la fecha exacta de vencimiento del token de Instagram y renovarlo antes de que caduque; duración aproximada indicada por el usuario: dos meses.
- Pendiente registrado entonces: Valorar centralizar datos de campeonatos, patrocinadores y publicaciones para facilitar el mantenimiento sin perder el HTML rastreable.


## YouTube automático — implementación local

- Seis tarjetas precargadas con publicaciones reales recuperadas del feed del canal; última publicación de la selección: 27/09/2026.
- Actualizador con siete pruebas unitarias aprobadas: orden, duplicados, contenido no disponible, Shorts sin filtro de duración, paginación y escape HTML/errores sin secretos.
- Cuadrícula comprobada a 1440, 900 y 390 px (3/2/1 columnas), sin errores JavaScript ni desbordamiento. Servicios externos aislados en aquella prueba local. La API y la automatización se activaron posteriormente y el usuario confirmó su funcionamiento; queda la comprobación de reproducción publicada.
- Workflow genera HTML y JSON durante el despliegue, sin commits automáticos. Un fallo conserva la web publicada. Pages utiliza GitHub Actions; funcionamiento confirmado por el usuario.

## Instagram — 29/09/2026

- Instantánea de tres publicaciones obtenida de la respuesta válida del usuario. No se guardaron tokens ni captions ni medios locales.
- Catorce pruebas de los actualizadores de YouTube e Instagram aprobadas, incluidos fallos sin sobrescritura, selección de miniaturas, respaldo sin imagen y credenciales fuera de las URLs/logs.
- Token configurado y llamada real desde Actions completada correctamente, según confirmación del usuario.
- Tarjetas propias comprobadas con Edge a 1440 y 390 px: las tres imágenes remotas cargan y las tarjetas mantienen dimensiones uniformes. No se carga embed.js.
- Últimos cambios de tarjetas preparados en local; publicación pendiente de confirmar. Las URLs temporales de imágenes se renuevan en cada ejecución del actualizador; si fallan, permanece el enlace a la publicación.

## SEO de contenido y posicionamiento — aplazado

Mantener una única landing y su estilo visual. No añadir frases de búsqueda al sitemap: este enumera URLs e imágenes, no palabras clave. No hay garantía de primeras posiciones.

- Pendiente registrado entonces: Revisar la presentación visible para identificar claramente a Kim Angel y su categoría Classic Physique.
- Pendiente registrado entonces: Enriquecer el Hall of Fame con contexto breve y verificado de cada competición (resultado, año y participación), manteniendo las cards y galerías.
- Pendiente registrado entonces: Relacionar consultas relevantes con contenido útil: Kim Angel, Classic Physique, palmarés, Olympia 2025, Arnold Classic 2026 y códigos de descuento por patrocinador. Usar términos naturales en títulos, texto visible y descripciones, sin repeticiones artificiales ni textos ocultos para posicionar.
- Pendiente registrado entonces: Revisar exactitud y actualidad de resultados, biografía y descuentos antes de ampliar el contenido.
- Pendiente registrado entonces: Valorar enlaces auténticos desde los perfiles de Kim o páginas de patrocinadores, si colaboran. No presentar la web como oficial sin autorización ni contactar a terceros sin indicación del usuario.
- Pendiente registrado entonces: Cuando Search Console acumule datos, analizar consultas, impresiones, clics, CTR y posición media para priorizar mejoras y comparar su evolución.

Primera tarea al retomar: presentación y contexto del Hall of Fame. La actualización automática de redes complementa el contenido propio, pero no lo sustituye.

## Próxima revisión: móvil

- Pendiente registrado entonces: Revisar la landing completa a distintos anchos móviles: portada, navegación, Sobre Kim, Hall of Fame, YouTube, Instagram, patrocinadores y footer.
- Pendiente registrado entonces: Comprobar controles táctiles, apertura y cierre de galerías, ampliación de fotos, copia de descuentos y ausencia de desbordamientos.
- Pendiente registrado entonces: Validar después en un teléfono real, incluyendo orientación y velocidad con datos móviles. La emulación de navegador no sustituye esta prueba.

## Otras ideas aplazadas

- Pendiente registrado entonces: Definir e incorporar métricas: visitas, procedencia del tráfico, uso de galerías, clics en patrocinadores y copias correctas de descuentos.
- Pendiente registrado entonces: Valorar un backoffice bajo autenticación para consultar esas métricas.
- Pendiente registrado entonces: Elegir un dominio propio y planificar el cambio de URLs, metadatos y Search Console.
- Pendiente registrado entonces: Valorar repositorio privado y alojamiento adecuado, además de la organización de futuras webs.

## Correcciones móviles — primera revisión

- Realizado según el registro: Sustituir los enlaces superiores por un menú desplegable en pantallas de hasta 900 px.
- Realizado según el registro: Ocultar el indicador lateral en móvil y dispositivos con puntero táctil.
- Realizado según el registro: Desactivar el ajuste vertical entre secciones y la interceptación de rueda en móvil; usar altura estable en la portada.
- Realizado según el registro: Unificar flechas de galerías y visor con SVG simétricos.
- Realizado según el registro: Permitir movimiento en ambos ejes en el visor y añadir ampliación al doble con botón; reiniciar al cambiar de foto.
- Realizado según el registro: Diagnosticar Instagram: la página pública todavía contiene los embeds antiguos; las tarjetas propias están en local.
- Pendiente registrado entonces: Publicar estos cambios y comprobarlos en un teléfono real, especialmente pellizco, arrastre de la imagen ampliada y fluidez del scroll.

Comprobación en Edge con móvil emulado: menú, cierre al navegar, dimensiones del visor, desplazamiento horizontal/vertical y reinicio del zoom; sin errores JavaScript ni desbordamientos a 320, 390 y 768 px. No sustituye la validación táctil en un dispositivo real.

## Calendario: histórico real
- Realizado según el registro: Retirar eventos ficticios e importar las 72 fichas históricas de Classic Physique de IFBB Pro (hasta 29/09/2026).
- Realizado según el registro: Estados editoriales independientes, todos inicialmente PENDIENTE; logos disponibles y respaldo morado.
- Realizado según el registro: Generar HTML durante el despliegue desde datos locales; instrucciones en docs/calendar.md.
- Realizado según el registro: Incorporar la imagen genérica proporcionada por el usuario, también como respaldo si falla un logo.
- Realizado según el registro: Sustituir el texto de la imagen genérica por PRO CHAMPIONSHIP; imagen actualizada por el usuario y comprobada.
- Realizado según el registro: Implementar consulta periódica de IFBB, validación de cambios y conservación de estados manuales: scripts/update_competitions.py y workflow de los martes a las 07:17 UTC; horizonte anual hasta el siguiente 1 de octubre, inicialmente 2027. Primera actualización local: 102 eventos.
- Pendiente registrado entonces: Subir y activar el workflow Refresh IFBB competitions en la rama predeterminada; comprobar su primera ejecución, commit del JSON y posterior publicación de Pages.
- Pendiente registrado entonces: Evaluar como posible opción un catálogo propio de campeonatos con identidad interna, nombres normalizados y alias revisados para asociar logos locales independientemente del ID de IFBB. **Propuesta aplazada, no elegida ni autorizada para implementar:** las coincidencias por nombre pueden ser frágiles ante cambios de denominación, homónimos, ediciones, categorías y ubicaciones. Antes de decidir, comprobar las garantías reales de los IDs externos y comparar alternativas. Si se adopta, reservar la coincidencia aproximada para sugerencias; los casos desconocidos o ambiguos deben conservar la imagen genérica y requerir revisión manual. Separar la identidad del campeonato de cada edición para no trasladar participación de Kim entre años; admitir logos específicos por edición. Validar la propuesta con casos reales y pruebas antes de automatizar asociaciones.

## Revisión técnica — 30/09/2026

- Pendiente registrado entonces: Resolver el backlog de estructura, naming, convenciones, generación, frontend y pruebas de [TODO de revisión técnica](TODO-revision-tecnica.md). Incluye 34 tareas con evidencia y criterios de cierre. Implementadas siete tandas: AUD-01 a AUD-10, AUD-12 a AUD-14, AUD-19 a AUD-22, AUD-24, AUD-26, AUD-27 y AUD-34; 77 pruebas correctas, frontend organizado, constructor validado y actualizadores con recuperación y metadatos. Pendiente ejecutar el workflow actualizado en GitHub y continuar el resto del backlog.

Protocolo vigente de validación manual: [usabilidad y accesibilidad](accessibility.md). AUD-23 y AUD-25 conservan pendientes reales de móvil, zoom y lector de pantalla.

## Animaciones de entrada — propuesta 01/10/2026

- Realizado según el registro: Definir e implementar un estándar común de entrada para tarjetas de Instagram, vídeos de YouTube y tarjetas de clasificaciones (Hall of Fame). Un único módulo y estilos compartidos: 80 px desde abajo, sin cambios de opacidad, 600 ms y 200 ms entre tarjetas que entran juntas, una sola vez por tarjeta. Reutilización mediante data-entry-group y variables CSS; sin duplicar lógica en generadores. Respeta movimiento reducido y foco, y mantiene el contenido visible sin JavaScript. Pruebas y contrato en docs/frontend.md. Revisado en Edge a 390 y 1440 px; publicación pendiente.

Ajuste de entrada: las tarjetas se preparan con el desplazamiento inicial antes de observar su entrada. Permanecen opacas durante la espera y el movimiento; solo se anima la traslación hasta su posición final. Movimiento reducido, foco e impresión eliminan también el desplazamiento preparado.
