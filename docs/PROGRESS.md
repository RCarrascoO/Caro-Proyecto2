PROGRESS — Caro-Proyecto2

Fecha: 29-10-2025

Resumen corto (qué se hizo)
- Reorganización: el código y las utilidades se reorganizaron en carpetas claras:
  - `src/` contiene el código principal: `plot_utils.py`, `http_server/app.py`, `http_client/send_data.py`, y `clients/mqtt_subscriber.py`.
  - `tools/` contiene utilidades de prueba (publish/sniff/send image).
  - `archive/` contiene archivos y artefactos que no son necesarios para el entregable (configs con tokens, logs, imágenes antiguas, helpers de Mosquitto).
- Se extrajo la lógica de graficado a `src/plot_utils.py` (genera PNG con 6 subplots: 5 series + histograma).
- Se añadió un esqueleto de servidor Flask en `src/http_server/app.py` con endpoints `/upload-json`, `/upload-stream` y `/plot/<client_id>` (usa SQLite para almacenar mediciones).
- Se creó un cliente de prueba en `src/http_client/send_data.py` (envía JSON y stream). Actualmente envía datos de ejemplo; lo conectaremos al parser de `data.dat` en el siguiente paso.

Qué quedó fuera (archive)
- `client1.json`..`client4.json` (archivados porque contenían tokens y no son necesarios para el entregable)
- `start_services.ps1`, `mosquitto_log.txt`, `sniff_results.json`, y los scripts/archivos de prueba originales (moved to `archive/`).

Por qué esta decisión
- El PDF pide un HTTP Client (POST JSON + stream), un HTTP Server (Flask/SQLite) y generación de PNGs con matplotlib. MQTT, Mosquitto y el bot de Telegram no son requeridos por la especificación, por eso se archivaron.

Próximo paso recomendado (qué hacer ahora)
1) Implementar el parser de `data.dat` (PRIORIDAD)
   - Crear `src/data_parser.py` que lea el binario con la estructura mostrada en el PDF:
     - Campos: id (Byte), te (Byte), hr (Byte), mp01/mp25/mp10/h01/h25/h50/h10 (Word cada uno).
     - Asunción por defecto: little-endian (si no indicas lo contrario).
   - Función principal: `parse_file(path) -> list[dict]` con campos legibles.

2) Generador de prueba (si no dispones de `data.dat` real)
   - Crear `tools/generate_data_dat.py` para producir `data.dat` sintético y así poder probar todo el flujo sin el micro.

3) Conectar el HTTP client al parser
   - Actualizar `src/http_client/send_data.py` para leer `data.dat` con `data_parser`, enviar primero JSON a `/upload-json` y luego enviar el stream raw a `/upload-stream`.

4) Completar servidor y pruebas
   - Asegurar que `/upload-json` guarda en SQLite correctamente.
   - Añadir (opcional) parsing del stream en `/upload-stream` usando `data_parser`.
   - Probar endpoint `/plot/<client_id>` para que devuelva un PNG con promedio móvil ventana=10.

Cómo ejecutar (rápido)
1. Crear y activar entorno (PowerShell):
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
2. Ejecutar servidor Flask (desde la raíz):
```powershell
python src\http_server\app.py
# abre en http://127.0.0.1:5000
```
3. Enviar datos de ejemplo con el cliente de prueba:
```powershell
python src\http_client\send_data.py --server http://127.0.0.1:5000 --client-id client1
```
4. Ver la gráfica generada (en navegador):
  http://127.0.0.1:5000/plot/client1

Decisiones pendientes y preguntas para ti
- Confirmar endianness del `data.dat` (asumo little-endian por defecto). Si puedes subir un `data.dat` de ejemplo lo usaré para validar.
- ¿Deseas que añada soporte para MariaDB desde el inicio o lo dejamos opcional y documentado? (recomiendo empezar con SQLite y dejar MariaDB como opcional).

Siguientes acciones que puedo hacer ahora (elige una)
- A) Implementar `src/data_parser.py` + `tools/generate_data_dat.py` (recomendado). Esto permitirá pruebas end-to-end.
- B) Implementar integración del cliente para leer `data.dat` y enviar los dos POST.
- C) Añadir tests y documentación detallada de uso para evaluación.

Estado del todo
- Reestructuración y refactor: COMPLETADA
- Auditoría y archivado de archivos no necesarios: COMPLETADA
- Parser `data.dat`: PENDIENTE (PRIORIDAD)
- Cliente → Server end-to-end con `data.dat`: PENDIENTE

Si confirmas la A (parser + generador sintético), empiezo ahora y te dejo el primer `data.dat` de prueba y el parser listo para usar.

Fin del resumen.
