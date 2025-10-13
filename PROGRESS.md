PROGRESS — Caro-Proyecto2

Fecha: 13-10-2025

Este documento resume lo realizado hasta ahora, cómo reproducir las pruebas y los siguientes pasos recomendados (incluyendo cómo probar envío a Telegram).

Estado general
- Entorno Python creado (`.venv`) y dependencias instaladas (ver `requirements.txt`).
- Broker Mosquitto instalado y probado localmente (pub/sub OK).
- Script principal: `mqtt_subscriber.py` (cliente MQTT parametrizable) implementado.
- Archivos de config: `config_example.json`, `client1.json` .. `client4.json`.
- Script helper: `start_services.ps1` para iniciar Mosquitto/subscriber y los clientes.
- Backend Matplotlib forzado a `Agg` (para generar imágenes en background sin GUI).
- Guardado controlado: añadida lógica `save_to_disk`, `save_when_full`, `save_path`.
- Carpeta `reports/` para almacenar las imágenes generadas por los clientes.
- README actualizado con instrucciones y las 3 opciones (A/B/C).

Archivos creados/actualizados (principales)
- `mqtt_subscriber.py` — cliente MQTT que:
  - parsea mensajes CSV (mp01,mp25,mp10,temp,hr)
  - mantiene buffer circular de 10 muestras
  - genera gráfico con 5 subplots y lo exporta a PNG
  - envía la imagen a Telegram si `bot_token` y `chat_id` están configurados
  - guarda la imagen en disco según `save_to_disk` / `save_when_full`
- `client1.json`..`client4.json` — ejemplos de configuración por cliente
- `start_services.ps1` — helper PowerShell para iniciar servicios y clientes
- `README.md` — instrucciones resumidas
- `PROGRESS.md` — este archivo

Comandos útiles (PowerShell)
- Activar entorno:

  .\.venv\Scripts\Activate.ps1

- Suscribir y publicar (prueba rápida broker):

  mosquitto_sub -h 127.0.0.1 -t "DATA/#" -v
  mosquitto_pub -h 127.0.0.1 -t "DATA/MP" -m "12.3,25.7,31.0,23.5,45.2"

- Ejecutar cliente en primer plano (client1):

  python mqtt_subscriber.py --config client1.json --loglevel INFO

- Lanzar los 4 clientes en background con helper (si Mosquitto activo):

  powershell -ExecutionPolicy Bypass -File .\start_services.ps1 -StartClients

Pruebas realizadas y resultados
- Pub/Sub: verificado con `mosquitto_sub` y `mosquitto_pub` (mensaje recibido: `DATA/MP 12.3,25.7,31.0,23.5,45.2`).
- Guardado de imágenes:
  - Probamos `save_to_disk:true` en `client1` con `save_when_full:false` y generó imágenes inmediatamente.
  - Luego configuramos `save_when_full:true` para `client1..client4` y verificamos que cada cliente guarda una única imagen en `reports/` cuando su buffer alcanzó 10 muestras.
  - Ejemplos de archivos generados: `reports/report_client1_1760374960.png`, `report_client2_1760374961.png`, etc.

Cómo probar envío a Telegram (paso a paso)
1. Crear un bot con BotFather en Telegram y copiar el `bot_token`.
2. Conseguir tu `chat_id` enviando un mensaje al bot y consultando `getUpdates` con:
   - Abre en el navegador:
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   - Busca `chat` → `id` en la respuesta (o añade `@userinfobot` como alternativa).
3. Edita `client1.json` (o el cliente que quieras usar) y coloca `bot_token` y `chat_id`:

  {
    "client_id": "client1",
    "simulate": false,
    "broker": "127.0.0.1",
    "port": 1883,
    "topic": "DATA/MP",
    "bot_token": "<PON_TU_TOKEN_AQUI>",
    "chat_id": "<PON_TU_CHAT_ID>",
    "save_to_disk": true,
    "save_when_full": true,
    "save_path": "./reports"
  }

4. Reinicia el cliente y publica datos hasta que el buffer esté lleno (o fuerza `save_when_full:false` temporalmente). El cliente deberá enviar la imagen al chat configurado.

Seguridad y privacidad
- No subas `bot_token` ni `chat_id` al repositorio público.
- Para producción considera TLS y autenticación para Mosquitto.

Próximos pasos recomendados
- Validar envío a Telegram con un cliente (client1) y comprobar tiempos/errores.
- Si todo OK, propagar tokens/config a otros clientes y gestionar reintentos/ratelimit.
- Opcional: Dockerizar clientes, convertir en servicios, añadir logs rotativos o una cola si el tráfico es alto.

Si quieres que haga ahora la prueba de Telegram, indícame (a) el `bot_token` y (b) el `chat_id` — o prefieres que te guíe para obtenerlos y lo ejecutes tú; en ese caso te doy comandos exactos.
