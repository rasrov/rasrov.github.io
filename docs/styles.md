# Organización de estilos

La hoja pública sigue siendo css/styles.css, sin dependencias de compilación. Se organiza en base/layout/tokens, portada y navegación, presentación, Hall of Fame y visor, calendario y agenda, YouTube, redes, patrocinadores, pie, controles compartidos y utilidades de accesibilidad. Buscar el encabezado del componente antes de añadir reglas; evitar parches al final del archivo.

## Cascada y variables

Las reglas responsive permanecen junto a su componente y conservan su orden relativo. Algunas repeticiones son necesarias para la cascada: no fusionar selectores a través de condiciones distintas sin comprobar el resultado. Conservar los fallbacks consecutivos de unidades vh/dvh. Las imágenes ocultas de las galerías mantienen display: none; el calendario conserva logos y etiquetas accesibles sin cambiar la altura de las filas.

:root centraliza los tamaños de layout y las variables de portada existentes. --calendar-surface identifica el fondo de paneles y del selector de coincidencias; --calendar-divider identifica los separadores y bordes de paginación. Compartir variables por significado, sin unir colores parecidos de componentes distintos. Se eliminó --navigation-border, que no tenía consumidores.

## Breakpoints

| Condición | Responsabilidad actual |
| --- | --- |
| Hasta 540 px | Densidad del calendario, tarjetas y patrocinadores; ajustes de separación y tipografía. |
| Hasta 767 px | Márgenes de página y composición compacta de portada, galerías y contenido audiovisual. |
| Hasta 900 px | Menú desplegable, presentación en una columna, calendario y controles adaptados al espacio disponible. |
| Hasta 1100 px | Redes en una columna; YouTube utiliza dos columnas entre 768 y 1100 px. |
| Hasta 900 px o pointer: coarse | Desplazamiento natural y alturas svh; ocultación del indicador lateral. |
| hover: none / prefers-reduced-motion | Adaptación de interacción y reducción de movimiento. |

Estos umbrales corresponden al comportamiento existente; no son nuevos puntos de corte. El Hall of Fame conserva dos columnas también en pantalla estrecha. Cambiar esta decisión de diseño requiere una tarea y comparación propias.

## Comprobación de la consolidación

El 30/09/2026 se comparó la hoja anterior con la consolidada en Edge headless: 390, 540, 541, 767, 768, 900, 901, 1100, 1101 y 1440 px, con altura de 900 px. Se recorrieron portada, presentación, Hall, galería abierta, visor, calendario, selector de coincidencias, YouTube, redes, patrocinadores y pie.

Resultado: sin diferencias en las propiedades calculadas y rectángulos muestreados en 110 escenarios; sin diferencias de píxeles en 23 parejas de capturas (390 y 1440 px, más el menú a 390 px). La muestra de estilos incluye el primer elemento de cada combinación de etiqueta y clases, no todos los nodos ni pseudoelementos.

Las capturas usan recursos locales, sustituyen imágenes remotas, omiten iframes externos y desactivan animaciones/transiciones para obtener referencias estables. No prueban servicios externos, tacto real, hover/foco en todos sus estados, lectores de pantalla ni todas las preferencias de accesibilidad. AUD-25 conserva esas comprobaciones pendientes. Para futuros cambios, repetir las interacciones y los límites de los breakpoints afectados, además de python scripts/validate.py --browser.
