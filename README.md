# Kim Angel — web estática

Landing con palmarés, galerías, calendario y selecciones de YouTube e Instagram. HTML, CSS y JavaScript sin framework; generadores Python con biblioteca estándar.

## Requisitos

- Python 3.12 o posterior.
- Node.js 22 o posterior para comprobar la sintaxis JavaScript; no requiere npm install.
- Chrome o Edge para las regresiones del calendario. Si no se detecta, definir BROWSER_BIN con la ruta absoluta del ejecutable.

## Desarrollo local

Desde la raíz del repositorio:

```sh
python -m http.server 8081 --bind 127.0.0.1
```

Abrir http://127.0.0.1:8081. El servidor sirve la instantánea local; no consulta redes sociales.

## Validación antes de publicar

```sh
python scripts/validate.py --browser
```

Comprueba contratos JSON, referencias del artefacto (HTML/CSS, rutas estáticas JS, manifiesto y sitemap), sintaxis Python/JavaScript, pruebas unitarias, regresiones del calendario en navegador y generación completa desde cache dos veces, verificando idempotencia y conservación del HTML manual. Trabaja en una copia temporal y no necesita secretos ni llamadas a las APIs. Sin --browser las regresiones de navegador se omiten, salvo que BROWSER_BIN esté definido.

Para ejecutar solamente las pruebas unitarias:

```sh
python -B -m unittest discover -s tests -v
```

## Estructura y edición

| Ruta | Responsabilidad |
| --- | --- |
| index.html | Contenido manual y regiones generadas delimitadas por comentarios |
| css/ | Estilos de la web |
| js/ | Navegación, galería y calendario |
| img/ | Originales, logos, variantes optimizadas e inventario |
| data/ | Instantáneas públicas y decisiones editoriales del calendario |
| scripts/ | Actualizadores, renderizado y validación |
| tests/ | Pruebas unitarias y regresiones del calendario |
| docs/ | Guías de operación, auditorías y backlog |
| .github/workflows/pages.yml | Validación, actualización de redes y publicación |

Editar los eventos, participaciones y logos en los JSON descritos en [Calendario](docs/calendar.md). Los bloques youtube:generated, instagram:generated y calendar:generated de index.html son salidas generadas: no editar sus tarjetas manualmente. El contenido fuera de esos marcadores se conserva.

## Construcción offline

```sh
python scripts/build.py
python -m http.server 8081 --bind 127.0.0.1 --directory _site
```

El constructor genera las tres regiones y prepara todos los archivos públicos en _site/. No consulta APIs ni modifica index.html o data/ del checkout. Prepara el resultado en una carpeta temporal; si falla, conserva o restaura la salida anterior. _site/ es descartable: no guardar contenido manual allí. Ejecutar una sola construcción a la vez.

Para regenerar las instantáneas del checkout de manera intencionada con los comandos existentes:

```sh
python scripts/update_youtube.py --from-cache
python scripts/update_instagram.py --from-cache
python scripts/render_calendar.py
```

Estos comandos con --from-cache reescriben únicamente index.html y conservan los JSON byte a byte. Sin --from-cache, los actualizadores consultan las APIs y guardan JSON y HTML con respaldo y recuperación ante fallos. Para comprobar o previsualizar cambios, preferir validate.py y build.py; el validador utiliza el mismo constructor en una copia temporal.

## Publicación y secretos

Los pull requests solo validan, sin secretos ni despliegue. En main, ejecuciones manuales y horario programado, primero se valida y después se consultan las APIs y se publica. Si falla una fase, permanece la web publicada anteriormente. El resultado de las APIs de redes sociales se guarda en el artefacto, sin commits automáticos; puede ser más reciente que los JSON del repositorio.

Un workflow independiente actualiza IFBB los martes a las 07:17 UTC y guarda competitions.json mediante commit del bot. El horizonte avanza cada 1 de octubre; logos y participación permanecen manuales. Activación, comandos y política de conservación en [Calendario](docs/calendar.md).

Configurar YOUTUBE_API_KEY e INSTAGRAM_ACCESS_TOKEN en GitHub Actions. Nunca incluir sus valores en archivos o commits. Detalles de configuración y renovación:

- [YouTube](docs/youtube.md)
- [Instagram](docs/instagram.md)
- [Calendario](docs/calendar.md)
- [Convenciones](docs/conventions.md)
- [Organización del frontend](docs/frontend.md)
- [Organización del CSS y breakpoints](docs/styles.md)
- [Usabilidad, compatibilidad y protocolo manual](docs/accessibility.md)
- [Contratos de datos y recursos](docs/data-contracts.md)
- [Instantáneas: procedencia y recuperación](docs/snapshots.md)
- [TODO técnico](docs/TODO-revision-tecnica.md)
- [TODO general](TODO.md)
