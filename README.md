# Caro-Proyecto2

Proyecto para: 4 clientes MQTT suscriptores que generan un gráfico con 10 muestras y lo envían a bots de Telegram.

Requisitos mínimos
- Python 3.8+
- Entorno virtual (recomendado)
- Broker MQTT (p. ej. Mosquitto) — opcional en modo simulado

Instalación rápida (PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Archivos principales
- `mqtt_subscriber.py`: cliente MQTT genérico (también modo simulado).
- `config_example.json`: plantilla de configuración.
- `client1.json`..`client4.json`: ejemplos para ejecutar 4 instancias.
- `requirements.txt`: dependencias ya generadas.

Ejecutar en modo simulado (rápido, sin broker)
```powershell
.# activar venv
.\.venv\Scripts\Activate.ps1

python mqtt_subscriber.py --config client1.json
python mqtt_subscriber.py --config client2.json
python mqtt_subscriber.py --config client3.json
python mqtt_subscriber.py --config client4.json
```

Cada cliente en modo simulado generará imágenes `report_<client_id>_<timestamp>.png` en la carpeta del proyecto.

Ejecutar con broker MQTT real
1. Edita `client1.json`..`client4.json` y establece `simulate: false`, `broker`, `port`, `topic` y si quieres `bot_token`/`chat_id`.
# Caro-Proyecto2

Estado actual del proyecto (resumen)
- Implementado: `mqtt_subscriber.py` (cliente MQTT parametrizable) que:
	- se suscribe a un topic MQTT y parsea mensajes en formato CSV: mp01,mp25,mp10,temp,hr
	- mantiene un buffer circular de 10 muestras
	- genera un gráfico con Matplotlib (5 subplots) y lo exporta como PNG
	- puede enviar la imagen a Telegram si configuras `bot_token` y `chat_id`
	- incluye un modo `simulate` para generar datos de prueba localmente
- Se añadió `start_services.ps1` para arrancar Mosquitto (o su ejecutable), abrir un subscriber y lanzar los 4 clientes en background.
- Se configuró Matplotlib para usar el backend no interactivo `Agg` (evita advertencias al ejecutar en background).

Qué falta / qué revisar
- Ajustar si quieres que el cliente envíe imágenes sólo cuando el buffer tenga 10 muestras (actualmente genera imágenes por cada mensaje recibido en modo real y en simulación guarda una imagen cada iteración).
- Opcional: añadir autenticación/TLS para Mosquitto si es necesario en producción.

Requisitos (básicos)
- Python 3.8+
- Windows (instrucciones aquí) o Linux (comandos similares)
- `mosquitto` instalado para pruebas locales (o usar broker remoto)
- Virtualenv recomendado (el repo ya contiene `requirements.txt`)

Instalación rápida (PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Archivos clave añadidos
- `mqtt_subscriber.py` — cliente MQTT (modo real y simulado)
- `config_example.json` — plantilla de configuración
- `client1.json`..`client4.json` — ejemplos de configuración (editar antes de usar en modo real)
- `start_services.ps1` — script PowerShell para arrancar Mosquitto/subscriber y los clientes

Cómo continuar: tres opciones (pasos claros)

Opción A — Comprobar que el broker funciona (recomendado primero)
1. Abre una terminal y suscríbete a los topics (mostrará mensajes recibidos):
```powershell
mosquitto_sub -h 127.0.0.1 -t "DATA/#" -v
```
2. En otra terminal publica un mensaje de prueba:
```powershell
mosquitto_pub -h 127.0.0.1 -t "DATA/MP" -m "12.3,25.7,31.0,23.5,45.2"
```
3. Si ves el payload en la terminal del subscriber, el broker está funcionando.

Opción B — Ejecutar 1 cliente real y validar su procesamiento
1. Edita `client1.json` y establece `"simulate": false`, `broker`, `port` y `topic` según tu entorno.
2. Ejecuta el cliente en primer plano para ver logs y generar una imagen:
```powershell
.\.venv\Scripts\Activate.ps1
python mqtt_subscriber.py --config client1.json --loglevel INFO
```
3. Verifica que se genera `report_client1_<timestamp>.png` en la carpeta del proyecto (o que se envía a Telegram si configuras `bot_token`/`chat_id`).

Opción C — Lanzar los 4 clientes en background (después de validar la Opción B)
1. Asegúrate de que `client2.json`..`client4.json` estén configurados (`simulate:false`, broker, topic, etc.).
2. Ejecuta el script que arranca los clientes (no inicia Mosquitto si ya está activo):
```powershell
powershell -ExecutionPolicy Bypass -File .\start_services.ps1 -StartClients
```
3. Para arrancar también Mosquitto y abrir un subscriber de monitoreo, usa:
```powershell
powershell -ExecutionPolicy Bypass -File .\start_services.ps1 -StartMosquitto -OpenSubscriber -StartClients
```

Notas sobre recursos y buenas prácticas
- Para evitar saturar la laptop: primero prueba con un cliente en modo real (Opción B). Ejecutar 4 clientes simultáneos genera CPU/IO según la tasa de mensajes.
- Si trabajas con el modo simulado, cambia `publish_interval` en los `clientN.json` para espaciar la generación de gráficos.
- Para producción: considera ejecutar cada cliente como servicio (Windows Service o sistema de gestión en Linux) o con Docker, y activar TLS en Mosquitto.

Cómo retomar desde otra máquina (por ejemplo con GPT-5 mini)
1. Clona este repositorio y copia tus tokens/IDs en los archivos `clientN.json`.
2. Crea y activa el virtualenv e instala `requirements.txt`.
3. Sigue la Opción A -> B -> C para avanzar en las pruebas.
4. Si vas a usar Telegram, asegúrate de proteger los tokens (no subirlos al repo).

Agradecimiento
Gracias por la sesión de hoy — avancé la base del proyecto (scripts, configuración y utilidades de inicio). Si quieres que deje preparados más cambios (por ejemplo Dockerfiles, pruebas unitarias o envío solo con 10 muestras), dímelo y lo preparo para la siguiente sesión.
