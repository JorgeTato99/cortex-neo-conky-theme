# Diagnóstico

Empieza con `cortex-neo doctor`, o con `cortex-neo doctor --dependencies-only`
cuando todavía no hay sesión gráfica. La salida JSON contiene comprobaciones
con estados `ok`, `warning` y `error`, junto con acciones para resolver fallos.
El diagnóstico no consulta Internet ni intenta determinar tu ubicación.

| Síntoma | Comprobación y solución |
|---|---|
| Conky existe, pero no aparece ninguna tarjeta | Revisar `conky_x11`, `conky_lua` y `display`; verificar la conexión real al monitor y el journal. |
| GTK no importa aunque existe Python | Usar el Python del sistema con python3-gi y GDK 3; reinstalar el entorno del tema. |
| Iconos cuadrados o incorrectos | Revisar `icons`; fontconfig puede devolver una fuente de sustitución aun con código de salida cero. Instalar fonts-font-awesome. |
| Fuente diferente en Debian | `monospace` puede advertir sustitución por DejaVu; no impide iniciar. |
| No hay gestor systemd del usuario | Ejecutar en la sesión de escritorio o instalar con --no-start para la próxima sesión. No arrancar el tema con sudo. |
| No aparece el clima | Revisar manualmente location.json; sin ciudad válida la tarjeta permanece oculta. |
| No aparecen DDR, marca o velocidad | El firmware o los permisos pueden no exponer SMBIOS. Es opcional; no otorgar sudo general para corregirlo. |
| No hay porcentaje de GPU | Depende del driver/sensores. Frecuencia Intel no equivale a utilización; nunca se inventa un 0 %. |

Para el registro de los servicios:

```bash
systemctl --user status cortex-neo.service cortex-neo-metrics.service
journalctl --user -u cortex-neo.service -u cortex-neo-metrics.service -n 100
```

Conky anterior a 1.24.3 usa opciones antiguas; versiones nuevas usan
`output_backend='x11'`. El tema selecciona la sintaxis según el binario instalado
y comprueba que la compilación incluya X11 y Lua. No basta con actualizar solo
Python para resolver diferencias de Conky o del compositor.

Antes de compartir registros o capturas, revisa hostname, nombres de procesos,
rutas de proyectos y ubicación de ciudad. No publiques archivos personales de
configuración ni el contenido completo del entorno de la sesión.
