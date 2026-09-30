# Instantáneas: procedencia y recuperación

## Metadatos públicos

Cada nueva consulta correcta de YouTube o Instagram guarda metadata con source y fetched_at. Los valores de source son youtube-data-api o meta-business-discovery; fetched_at es el instante UTC registrado tras obtener y seleccionar la respuesta. No es la fecha de publicación de los posts ni la fecha de despliegue.

Las instantáneas anteriores se identifican con source legacy-cache y fetched_at null. No se inventa una fecha histórica. Los snapshots antiguos sin metadata siguen siendo compatibles y se interpretan como de procedencia/fecha desconocidas.

--from-cache regenera solamente HTML y conserva el JSON byte a byte, incluidos metadatos y formato. build.py tampoco modifica los snapshots. Los metadatos forman parte de los JSON públicos que Actions copia a _site; no incluyen claves, tokens, cabeceras ni respuestas completas de las APIs.

```sh
python scripts/snapshot_info.py
python scripts/snapshot_info.py --compare-dir C:/ruta/descargas
```

La carpeta de comparación debe contener youtube.json e instagram.json. El comando no descarga nada ni modifica el proyecto: muestra origen, fecha y una huella SHA-256 del JSON normalizado. Diferencias de indentación no alteran la huella. Una diferencia de huella no significa necesariamente publicaciones distintas: también cuentan los metadatos y las URLs temporales de imágenes.

## Comparar con la web publicada

1. Obtener los JSON públicos de /data/youtube.json y /data/instagram.json del dominio desplegado, guardándolos en una carpeta aparte. No utilizar respuestas de API con credenciales ni URLs de paginación.
2. Ejecutar snapshot_info.py --compare-dir sobre esa carpeta y revisar fecha, procedencia y publicaciones. El comando solo valida metadatos; no certifica la procedencia declarada ni sustituye la validación completa.
3. Para recuperar intencionadamente una versión publicada, conservar una copia de los JSON locales y sustituir los JSON correspondientes por las descargas revisadas. Ejecutar scripts/validate_data.py y scripts/validate.py --browser antes de construir o publicar. Si falla la validación, restaurar los JSON guardados.
4. Ejecutar scripts/build.py para previsualizar. No cambiar fetched_at al importar: describe la obtención original, no la copia local. Un archivo publicado antiguo puede seguir sin metadata.

## Escrituras consistentes

Los actualizadores preparan JSON y HTML completos antes de tocar los destinos. scripts/snapshot_write.py guarda los bytes anteriores y un registro recovery.json en .snapshot-update/, y sustituye cada archivo con os.replace. Si una sustitución falla, restaura los archivos ya cambiados, incluidos sus finales de línea originales.

Si falla también la restauración, conserva el registro y los respaldos y muestra RecoveryRequiredError. Una nueva escritura y la construcción de _site se bloquean mientras exista .snapshot-update/. La carpeta está ignorada por Git y no se publica. No borrarla sin inspección.

No es una transacción de base de datos: las dos sustituciones no son simultáneas y un cierre abrupto o apagado puede interrumpirlas. El workflow no despliega si falla el actualizador. Ejecutar un solo proceso de actualización por checkout; no editar las fuentes ni construir mientras se actualizan. La exclusión protege la fase de escritura, no toda la consulta/renderización previa.

## Recuperación manual de una interrupción

1. Confirmar que no queda ningún actualizador ejecutándose.
2. Copiar .snapshot-update/ a una ubicación segura antes de intervenir.
3. Leer recovery.json. Cada registro indica path, existed y backup. Restaurar cada archivo con existed=true desde el respaldo indicado, conservando los bytes. Para existed=false, retirar solo el archivo nuevo indicado si llegó a crearse.
4. Si falta recovery.json, la preparación no terminó: el código no empieza a sustituir destinos hasta guardar ese registro. Si el registro existe pero falta un respaldo esperado, detenerse y revisar las copias; no asumir una recuperación completa.
5. Tras restaurar y comprobar los archivos, retirar la carpeta .snapshot-update/ y ejecutar validate.py --browser. Solo entonces repetir la actualización.

Si el proceso terminó después de escribir los dos destinos pero antes de limpiar, restaurar los respaldos devuelve ambos a la versión anterior; después puede repetirse la operación. No hay recuperación automática tras reiniciar ni garantía de durabilidad ante fallo físico del disco.
