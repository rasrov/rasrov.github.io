# Convenciones del proyecto

Estas reglas se aplican al código nuevo y a las partes que se modifiquen. Los nombres históricos de imágenes y las zonas de código pendientes de formato se migrarán en cambios separados para poder revisar las referencias y el comportamiento.

## Estructura y fuentes

- index.html contiene el contenido manual y las regiones generadas. Los comentarios `<!-- nombre:generated:start -->` y `<!-- nombre:generated:end -->` son contratos: deben aparecer una sola vez, en ese orden.
- data/ contiene los snapshots y las decisiones editoriales. La participación y los logos se mantienen separados de los eventos importados.
- scripts/ contiene comandos y utilidades Python importables. tests/ contiene sus regresiones; docs/ contiene las instrucciones y auditorías.
- _site/ es una salida descartable, ignorada por Git. No editarla ni guardar archivos manuales en ella: cada construcción sustituye su contenido completo. Las carpetas .site-build-* son temporales de construcción.
- El constructor offline lee las fuentes y genera _site/; los actualizadores de redes son los únicos comandos que consultan proveedores, cuando se ejecutan sin --from-cache. Sin --from-cache, los actualizadores reescriben JSON e index del checkout; con --from-cache, solo index. Usarlos intencionadamente y de forma secuencial.

## Nombres e idioma

| Elemento | Convención | Ejemplo |
| --- | --- | --- |
| Recursos y directorios web nuevos | kebab-case, minúsculas, años de cuatro cifras | arnold-classic-uk-2026 |
| Python: archivos, funciones y variables | snake_case | generated_regions.py, replace_region |
| Python: clases | PascalCase | CalendarTests |
| JavaScript: funciones y variables | camelCase | eventTile, monthEvents |
| Constantes de módulo | MAYUSCULAS_CON_GUIONES | CHANNEL_ID |
| CSS: componentes y estados | kebab-case; is-/has- para estado | calendar-event, is-selected, has-event |
| Pruebas nuevas de un script | test_ + nombre del módulo | test_render_calendar.py |

Código y comentarios técnicos en inglés; interfaz y documentación de uso en español. Conservar los campos de APIs externas tal como los define el proveedor. No renombrar anclas públicas, URLs de imágenes o claves JSON sin actualizar y validar todos sus consumidores.

Los nombres antiguos con guiones bajos, años abreviados o erratas se mantienen hasta la migración de AUD-15. Los módulos de prueba históricos test_youtube.py y test_instagram.py conservan sus nombres hasta AUD-18.

## Formato

UTF-8, LF y nueva línea final. Cuatro espacios para Python, JavaScript, HTML y CSS; dos para JSON y YAML. .editorconfig guía al editor y .gitattributes fija los finales de línea de los archivos de texto. No normalizar todo el repositorio ni mezclar un reformateo masivo con cambios funcionales.

Preferir bloques multilínea a varias sentencias comprimidas. No introducir una dependencia de formato o un framework para resolver un cambio pequeño. La adopción de comprobaciones automáticas de formato y la normalización del legado siguen en AUD-17.

## Generación y validación

Usar generated_regions.replace_region para reemplazar regiones HTML. La función preserva exactamente lo que queda fuera de sus marcadores; cada renderizador decide el formato de su contenido.

Ejecutar desde la raíz:

```sh
python scripts/validate.py --browser
python scripts/build.py
python -m http.server 8081 --bind 127.0.0.1 --directory _site
```

El mismo constructor prepara los archivos públicos en local y en Actions. Incluye los archivos raíz públicos, css/, js/, img/, data/, verificaciones google*.html, CNAME si existe y .nojekyll. No copia scripts/, tests/, docs/, .git ni archivos .env de la raíz. La revisión más fina de img/ y data/ sigue pendiente en AUD-32.

El constructor no admite un destino arbitrario: sustituye únicamente _site/ dentro de la raíz del proyecto. Rechaza enlaces simbólicos y junctions en ese destino. Si falla la instalación restaura la salida anterior; si falla también la restauración, conserva el respaldo en .site-build-*/previous para recuperación manual. Ejecutar una sola construcción a la vez por checkout.

## Pruebas

- Importar los generadores desde scripts como módulos; mantener las entradas de CLI con `if __name__ == '__main__'`.
- Fijar el reloj o pasar now explícitamente al probar selección de publicaciones. Incluir el límite exacto, el futuro y zonas horarias; no depender de la fecha del ordenador.
- Usar directorios temporales para pruebas de escritura y simular fallos de proveedor/disco. Las pruebas offline no consultan APIs.
- Probar resultados observables: HTML preservado, artefacto completo, restauración ante fallos, foco y accesibilidad de controles.
- Documentar por separado qué se probó automáticamente y qué requiere móvil, lector de pantalla o servicios externos.

Los contratos y el alcance de la comprobación offline están en [Contratos de datos y recursos](data-contracts.md). La construcción rechaza entradas inválidas antes de sustituir _site/.

El frontend encapsula cada componente en una IIFE, publica inicializadores en window.KimSite y arranca desde main.js. Orden de carga y controles dinámicos: [Frontend](frontend.md).
