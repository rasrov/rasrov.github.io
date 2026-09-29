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
7. Comprueba el paso de Instagram y los tres embeds en la web publicada.

Añade el secreto ANTES de subir el workflow actualizado. Si falta o caduca, el job no despliega; también se aplazan las actualizaciones de YouTube hasta resolver el fallo. La web anterior sigue disponible.

## Funcionamiento

El mismo horario de seis horas consulta 50 publicaciones recientes de Business Discovery y elige tres distintas por timestamp. Incluye imágenes, carruseles y reels; no presupone que el orden visual o una publicación fijada indique la fecha más reciente.

No se descargan medios: se conservan los embeds oficiales y sus enlaces de respaldo. El JSON público solo contiene identificadores de publicaciones, tipo, fecha y permalink; no contiene tokens, respuestas crudas ni enlaces de paginación.

La selección inicial procede de la respuesta válida compartida por el usuario el 29/09/2026. La consulta real desde GitHub queda pendiente hasta guardar el secreto. Como en YouTube, los cambios generados en Actions se publican sin crear commits.

Si la API falla o devuelve menos de tres publicaciones válidas, no se publica una selección parcial. Los mensajes de error no imprimen el token ni las respuestas del proveedor. Revisar caducidad/permisos en Meta y logs de Actions.

## Desarrollo

    python -m unittest discover -s tests -v
    python scripts/update_instagram.py --from-cache

Sin --from-cache se requiere INSTAGRAM_ACCESS_TOKEN en el entorno. La configuración de las otras secciones y la carga diferida del script de Instagram se mantienen.

Referencia: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/business_discovery/
Tokens: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/
