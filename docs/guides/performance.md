# Medir el coste del dashboard

```bash
cortex-neo performance --seconds 15
```

La medición observa los dos servicios de usuario de CÓRTEX y sus descendientes.
No inspecciona argumentos, variables de entorno ni procesos ajenos. La ventana
admite entre 2 y 60 segundos; no cambia cadencias ni límites de recursos.

- `cpu_core_percent`: 100 equivale a un núcleo ocupado durante toda la ventana.
- `cpu_machine_percent`: lo anterior dividido por los procesadores lógicos.
- `rss_bytes` y `peak_rss_bytes`: suma RSS, que incluye páginas compartidas y
  puede contarlas varias veces. No es memoria privada ni PSS.
- `payload_bytes`: tamaño real de los archivos publicados en ese momento.
- `available: false`: no se pudo observar la instalación activa; no implica
  consumo cero. Procesos breves o reconstrucciones pueden quedar fuera del delta.

El snapshot también expone `collector.sample_ms`, `providers_ms`, `interval_ms`
y `overrun`. El tiempo de muestreo termina antes de serializar/publicar archivos;
la medición de CPU de los servicios sí incluye ese trabajo. Los proveedores que
no se ejecutaron en ese ciclo no aparecen como si hubieran costado cero.

Para comparar cambios, usar la misma ventana, pantalla, escala y aplicaciones
en ambas mediciones. Una diferencia aislada no es un benchmark reproducible.

Las gráficas de Conky mantienen su propio búfer. El historial de herramientas se
conserva en JSON y no se copia al payload Lua que vuelve a cargar cada tarjeta.
Esta reducción de datos no implica por sí sola un ahorro específico de CPU.
