# Instagram automático

## Acceso comprobado

El usuario confirmó una consulta correcta de Business Discovery con Facebook Login:
- Aplicación: Kim Angel Web.
- Instagram propio autorizado: 17841401870042081.
- Perfil consultado: kim_angel.
- Permisos: instagram_basic, instagram_manage_insights, pages_show_list y pages_read_engagement.
- Graph API: v26.0.

La cuenta propia y la de Kim tienen funciones diferentes: la propia autoriza el acceso; Business Discovery consulta las publicaciones públicas de Kim. No se almacena ninguna clave en el código.

## Activación

1. Revisa el token de usuario en https://developers.facebook.com/tools/debug/accesstoken/.
2. Comprueba su validez, permisos y caducidad. Si aparece «Ampliar token de acceso / Extend Access Token», obtén el token de larga duración y comprueba de nuevo sus permisos y vencimiento.
3. Si esa opción no aparece, queda pendiente realizar el intercambio oficial de token de Facebook en un entorno privado. No pegues la clave secreta de la aplicación en consultas públicas ni en el repositorio.
4. En GitHub → Settings → Secrets and variables → Actions, crea INSTAGRAM_ACCESS_TOKEN con el token de usuario que haya superado la consulta. Es un secreto diferente de YOUTUBE_API_KEY.
5. Guarda la fecha de vencimiento para renovar la autorización antes de que caduque. Un token de larga duración tampoco es permanente; puede revocarse.
6. Sube los cambios y ejecuta Actions → Publish website and refresh social feeds → Run workflow.
7. Comprueba el paso de Instagram y las tres tarjetas en la web publicada.

Añade el secreto ANTES de subir el workflow actualizado. Si falta o caduca, el job no despliega; también se aplazan las actualizaciones de YouTube hasta resolver el fallo. La web anterior sigue disponible.

## Funcionamiento

El mismo horario de seis horas consulta 50 publicaciones recientes de Business Discovery y elige tres distintas por timestamp. Incluye imágenes, carruseles y reels; no presupone que el orden visual o una publicación fijada indique la fecha más reciente.

Las tarjetas propias muestran imágenes remotas en proporción 4:5 con recorte centrado. Para vídeos se usa thumbnail_url; para fotos y carruseles, media_url. El clic abre la publicación en Instagram. No se descargan imágenes al repositorio ni se reproduce el reel dentro de la tarjeta.

El JSON público conserva identificadores, tipo, fecha, permalink y la URL de imagen validada; nunca tokens ni paginación. Las URLs del CDN son temporales y se renuevan en cada ejecución de Actions. Si faltan o fallan, permanece una tarjeta con enlace a la publicación. La automatización ya se ha probado en GitHub; las ejecuciones publican sin crear commits.

Si la API falla o devuelve menos de tres publicaciones válidas, no se publica una selección parcial. Los mensajes de error no imprimen el token ni las respuestas del proveedor. Revisar caducidad/permisos en Meta y logs de Actions.

## Desarrollo

    python -m unittest discover -s tests -v
    python scripts/update_instagram.py --from-cache

Sin --from-cache se requiere INSTAGRAM_ACCESS_TOKEN en el entorno. Las imágenes usan carga diferida nativa; ya no se carga embed.js de Instagram.

Referencia: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/business_discovery/
Tokens: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/
