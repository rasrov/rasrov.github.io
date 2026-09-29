# Calendario

## Datos actuales
72 eventos profesionales con Classic Physique recuperados del histórico IFBB Pro entre enero y el 29/09/2026. Incluye Masters y Natural; no todos son Open. Fuente y auditoría: docs/ifbb-2026-audit.md. Las fechas abarcan el evento completo, no necesariamente las finales de Classic Physique. No se incorporan anuncios futuros ni se deducen fechas históricas de ellos.

## Mantenimiento
- data/competitions.json: eventos importados con ID estable y fuente.
- data/competition-participation.json: decisión editorial independiente por ID. El campo name ayuda a localizar el evento. status puede ser pending (PENDIENTE), confirmed (PARTICIPA), absent (NO PARTICIPA). Todos parten de pending.
- data/competition-logos.json: asociación ID/ruta local del logo; sin asociación se muestra img/calendar/default-championship.png. Los carteles de la API no se usan como logos.

Para cambiar participación, editar status del evento en data/competition-participation.json. Después ejecutar:

    python scripts/render_calendar.py

Recargar localhost. Al subir los archivos a GitHub, Actions regenera el HTML automáticamente antes de desplegar. La consulta periódica a IFBB todavía NO está activada; solo la generación desde los datos locales.

## Estrategia futura
La importación automática actualizará exclusivamente competitions.json; no sobrescribirá participation ni logos. Un ID nuevo sin decisión editorial será pending. No inferir ausencia de Kim por no figurar en listas provisionales. Si se incorporan listas oficiales, proponer cambios para revisión antes de confirmar participación. La imagen genérica del usuario sustituye al respaldo morado y también se usa si falla un logo. Si falla la imagen genérica se evita un bucle de solicitudes.

Logo Olympia 2026: https://mrolympia.com/sites/mrolympia.com/files/logo-2026.png (cabecera de https://mrolympia.com/). Asociado al evento IFBB 24691.

Filtro de publicación: excluir eventos con Natural/Naturals en el nombre o en las líneas de Classic Physique. Se conserva la instantánea completa para auditoría. Masters no se excluye por este criterio. La ausencia de la etiqueta Natural no certifica las reglas antidopaje de un evento.
