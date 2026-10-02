# Kim Angel — web estática

Landing con palmarés, galerías, calendario y selecciones de YouTube e Instagram. HTML, CSS y JavaScript sin framework; actualizadores y constructor Python con biblioteca estándar. El formato usa Ruff y la optimización de imágenes usa Pillow, con versiones fijadas.

## Requisitos

- Python 3.12 o posterior.
- Node.js 22 o posterior para comprobar la sintaxis JavaScript; no requiere npm install.
- Instalar `requirements-dev.txt` para la validación y `requirements-images.txt` para optimizar imágenes o ejecutar sus pruebas. Sin Pillow, las pruebas específicas de imágenes se omiten.
- Chrome o Edge para las regresiones de navegador. Si no se detecta, definir BROWSER_BIN con la ruta absoluta del ejecutable.

## Desarrollo local

Desde la raíz del repositorio:

```sh
python scripts/build.py
python -m http.server 8081 --bind 127.0.0.1 --directory _site
```

Abrir http://127.0.0.1:8081. El servidor sirve el artefacto construido desde las instantáneas locales, incluidos los alias de imágenes; no consulta redes sociales. Servir directamente la raíz del checkout no reproduce esos alias.

## Validación antes de publicar

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate.py --browser
```

Para incluir las pruebas de imágenes, instalar también `python -m pip install -r requirements-images.txt`.

Comprueba formato Python y convenciones de texto (UTF-8, LF y espacios), contratos JSON, referencias del artefacto (HTML/CSS, rutas estáticas JS, manifiesto y sitemap), sintaxis Python/JavaScript, pruebas unitarias, regresiones del calendario y del resto del frontend en navegador y generación completa desde cache dos veces, verificando idempotencia y conservación del HTML manual. Trabaja en una copia temporal y no necesita secretos ni llamadas a las APIs. Sin --browser las regresiones de navegador se omiten, salvo que BROWSER_BIN esté definido.

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

Los nombres y disparadores siguientes corresponden a los YAML locales. Estar implementados no implica que los últimos cambios estén subidos o ejecutados en GitHub. El estado de publicación se mantiene en [TODO general](TODO.md).

| Workflow | Cuándo se ejecuta | Resultado y guía |
| --- | --- | --- |
| **Publish website and refresh social feeds** (`pages.yml`) | Push y PR a main, ejecución manual y 00:23/06:23/12:23/18:23 UTC | PR: validación sin secretos ni despliegue. Los otros disparadores validan, consultan YouTube e Instagram, construyen y publican. Guías de proveedores abajo. |
| **Refresh IFBB competitions** (`competitions.yml`) | Martes 07:17 UTC o manual; solo rama predeterminada | Guarda únicamente competitions.json mediante commit del bot; no despliega directamente. [Calendario](docs/calendar.md). |
| **Optimize images on demand** (`optimize-images.yml`) | Exclusivamente manual; solo rama predeterminada | Optimiza, valida y abre una PR; no publica ni fusiona. [Imágenes](docs/images.md). |

Si falla la validación o cualquiera de las dos APIs sociales, Pages conserva la web anterior. Actualmente no hay un modo de publicación desde cache para evitar esos fallos; decidir esa política sigue en AUD-28. Los datos sociales actualizados quedan en el artefacto, sin commits automáticos, y pueden ser más recientes que los JSON del checkout.

Para una instalación nueva: seleccionar **GitHub Actions** como origen en Settings → Pages, configurar los secretos de ambas redes siguiendo sus guías, subir el workflow a main y ejecutar **Publish website and refresh social feeds → Run workflow**. Comprobar validate, build y deploy, y después las tarjetas publicadas. La activación anterior fue confirmada por el usuario; este documento no comprueba la configuración remota actual. Renovar credenciales no requiere repetir la instalación completa.

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
- [Optimización manual de imágenes](docs/images.md)
- [TODO técnico](docs/TODO-revision-tecnica.md)
- [TODO general](TODO.md)

Para comprobar solo el formato: `python scripts/check_format.py`. Para aplicarlo: `python scripts/check_format.py --fix`. Alcance y excepciones en [Convenciones](docs/conventions.md).

Registro de decisiones y comprobaciones anteriores: [Historial del TODO](docs/todo-history-2026-10-02.md).
