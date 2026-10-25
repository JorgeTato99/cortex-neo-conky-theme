# Pantallas y escalado

La resolución física del monitor y el escalado del escritorio son datos
distintos. Por ejemplo, 1920 × 1080 al 125 % y 2560 × 1440 al 166,67 % producen
aproximadamente el mismo escritorio lógico de 1536 × 864.

El tema calcula la disposición en el área útil lógica que entrega GDK mediante
XWayland, excluyendo paneles y dock. La escala interna del tema se aplica a
fuentes, márgenes, gráficas e iconos. No es el porcentaje de escalado de GNOME.

`settings.json` admite `monitor: "primary"` o el índice de un monitor, y
`layout: "auto"`, `"landscape"` o `"portrait"`. `scale_multiplier` entre 0.5 y 1.0
reduce proporcionalmente el ajuste automático. Los cambios de geometría se
comprueban cada diez segundos.

En horizontal hay hasta cuatro columnas; en vertical se organizan en dos.
Las tarjetas opcionales ausentes se retiran. CPU/RAM y GPU/almacenamiento
comparten alturas por fila. El calendario completa el borde inferior de su
columna en horizontal.

El supervisor mide las ventanas Xft reales y corrige redondeos de fuente. Que
una composición quepa matemáticamente no garantiza legibilidad física en un
monitor pequeño de alta densidad. Las [capturas reales](../validation/screenshots.md)
documentan resolución y escalado conjuntamente.

El tema no cambia la resolución ni configura adaptadores virtuales o RustDesk.
Las pruebas Xvfb acreditan dibujo sobre X11; no simulan por completo GNOME
Wayland, sus portales ni un driver NVIDIA real.
