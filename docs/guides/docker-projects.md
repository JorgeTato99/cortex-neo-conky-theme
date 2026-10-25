# Docker por proyecto

```bash
cortex-neo containers
cortex-neo containers --format json
```

La vista agrupa por contexto (`default` o `desktop-linux`) y por las etiquetas
de proyecto/servicio Compose. Dentro de cada grupo muestra nombre, estado y
puertos. Los contenedores sin esas etiquetas quedan en «Sin proyecto Compose»;
no se adivina su relación con un repositorio. El indicador del escritorio suma
grupos Compose por contexto, no nombres únicos entre motores.

Son consultas GET locales a los sockets ya detectados. No se detienen servicios,
no se inspeccionan entornos, comandos, secretos ni volúmenes y no se abre un
servidor de red. La respuesta permite solo los campos necesarios. La publicación
completa se realiza desde un trabajador, por lo que un daemon lento no bloquea
el muestreo de CPU/RAM. Se intenta refrescar cada quince segundos.

La lectura tiene plazos de conexión/respuesta, un máximo de 1 MiB por respuesta,
cien contenedores y dieciséis puertos por contenedor. La vista indica truncamiento
o indisponibilidad. Una consulta fallida no representa cero contenedores; la
fecha de cada contexto permite reconocer datos antiguos. El comando consulta
la caché y no ejecuta otra petición Docker.

Referencias: [etiquetas Compose](https://docs.docker.com/reference/compose-file/services/#labels)
y [API de inventario](https://docs.docker.com/reference/api/engine/version/v1.51/).
