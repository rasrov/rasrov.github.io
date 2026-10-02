# Calendario

## Actualización de campeonatos

scripts/update_competitions.py consulta la API pública de IFBB Pro, sin credenciales, con paginación de 50 resultados. Importa eventos de categoría professional cuya descripción menciona Classic Physique. Decodifica HTML y conserva las fechas locales del evento completo, no una supuesta fecha de finales de Classic Physique.

La consulta comienza en 2026-01-01 para conservar y revisar el histórico. El límite incluye el 1 de octubre y se calcula con la fecha UTC de ejecución:

| Ejecución | Límite incluido |
| --- | --- |
| Hasta 30/09/2027 | 01/10/2027 |
| 01/10/2027–30/09/2028 | 01/10/2028 |
| 01/10/2028–30/09/2029 | 01/10/2029 |

El avance ocurre en la primera ejecución desde la fecha de cambio, sin editar el workflow. No se añade una ejecución extraordinaria el 1 de octubre si no es martes. El límite es un horizonte de consulta; no garantiza que IFBB haya publicado ya todos los eventos hasta esa fecha.

Comandos desde la raíz:

```sh
# Consulta y valida sin escribir archivos.
python scripts/update_competitions.py --dry-run
# Actualiza exclusivamente data/competitions.json.
python scripts/update_competitions.py
# Genera la previsualización local desde los datos actuales.
python scripts/build.py
```

Se incorporan IDs nuevos y se actualizan los existentes. Si una ficha anterior deja de aparecer entre los resultados elegibles, se conserva y se registra su ID en metadata.retained_missing_ids para revisión manual. Esto evita borrar historia o decisiones editoriales, pero no confirma que ese evento siga vigente. No se deduce una cancelación ni se fusionan IDs diferentes por similitud de nombre. La estrategia de asociación por nombres sigue aplazada.

Se rechazan respuestas vacías, páginas incompletas, IDs duplicados y cambios en los totales durante la paginación. Una consulta completa no constituye una instantánea transaccional del servidor remoto. Se reintentan hasta tres veces errores de red, HTTP 429 y errores 5xx. Los fallos de consulta, formato o validación conservan el JSON anterior. La escritura utiliza el respaldo y recuperación comunes de .snapshot-update; ejecutar un solo actualizador por checkout.

La nueva instantánea incluye checked_at y metadata con fuente, fetched_at UTC, rango consultado, total recibido antes del filtro y IDs conservados para revisión. Se guardan solo los campos públicos necesarios; no se importan contactos de promotores.

## GitHub Actions

.github/workflows/competitions.yml define **Refresh IFBB competitions**, los martes a las **07:17 UTC**, además de ejecución manual con workflow_dispatch. Solo se ejecuta sobre la rama predeterminada. La hora es UTC y la ejecución puede retrasarse por disponibilidad de GitHub Actions.

El job valida el proyecto, consulta IFBB, construye y valida el artefacto actualizado y hace commit/push únicamente de data/competitions.json. No modifica logos, participación, HTML fuente ni publicaciones sociales. El token del job solicita contents: write; no requiere un secreto de IFBB. La rama debe permitir ese push del bot. Si la rama avanza mientras se ejecuta, el push falla sin forzar ni sobrescribir cambios; se debe repetir la ejecución.

El commit realizado con GITHUB_TOKEN no dispara automáticamente el workflow de publicación por push. Los nuevos datos se incorporarán en la siguiente ejecución programada del workflow de Pages existente (cada seis horas), si sus validaciones y consultas de redes terminan correctamente. También puede lanzarse ese workflow manualmente. Referencia: [comportamiento de GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token).

Para activar la programación, estos cambios deben estar en la rama predeterminada de GitHub y Actions habilitado. Preparar los archivos localmente no activa el cron. La consulta completa y el importador se han probado localmente; la confirmación de activación y primera ejecución remota se gestiona en el [TODO general](../TODO.md).

## Logos y participación manuales

- data/competition-participation.json: decisiones independientes por ID. status admite pending (PENDIENTE), confirmed (PARTICIPA) y absent (NO PARTICIPA). Un evento nuevo sin decisión se muestra como pending; el importador no añade ni cambia decisiones.
- data/competition-logos.json: asociación ID/ruta local. Un evento sin asociación usa img/calendar/default-championship.png; también se usa si falla el logo en el navegador. No se utilizan automáticamente los carteles image_url de IFBB como logos.
- Para cambiar una decisión o logo, editar su JSON y ejecutar python scripts/build.py. Para regenerar deliberadamente el index.html fuente, ejecutar python scripts/render_calendar.py.

Los eventos naturales se conservan en los datos para auditoría, pero el renderizador excluye cualquier nombre que contenga natural, sin distinguir mayúsculas (incluye Euronaturals). También excluye Natural/Naturals como palabra completa en las líneas de Classic Physique; una mención en otra división no basta para excluir el evento. Masters no se excluye. No se infiere ausencia de Kim por no aparecer en listas provisionales.

## Procedencia y primera ejecución

El histórico inicial contenía 72 eventos consultados hasta el 29/09/2026; se conserva su auditoría en docs/ifbb-2026-audit.md y docs/ifbb-2026-audit.json. La consulta completa del 30/09/2026, hasta 01/10/2027, recibió 313 eventos y seleccionó 102 profesionales con Classic Physique: 30 incorporaciones y 66 fichas actualizadas, incluidas normalizaciones de texto. No faltó ningún ID previo. Estos recuentos describen esa ejecución, no valores fijos para futuras importaciones.

En días con varias competiciones, la celda muestra el primer logo propio disponible en el orden de la agenda (se omiten asociaciones vacías y la imagen genérica); si ninguno tiene logo propio, se usa default-championship.png, con opacidad 0,38 y el contador +N encima. Comparte el respaldo de imagen genérica con las celdas individuales; al pulsar se mantiene el selector de todas las competiciones del día.
