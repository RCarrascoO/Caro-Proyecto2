# 📊 ANÁLISIS COMPLETO: Proyecto vs Requisitos del PDF

**Fecha**: 31 de octubre de 2025  
**Proyecto**: INFO1157 - Sistemas Inteligentes - Proyecto #2  
**Alumno**: Alberto Caro

---

## ❌ PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **ARQUITECTURA INCORRECTA** 🚨
**Problema**: El proyecto implementa un sistema MQTT + Telegram Bot que NO es lo solicitado.

**Lo que pide el PDF**:
- ✅ HTTP Client (método POST) envía datos a HTTP Server
- ✅ HTTP Server almacena en SQLite/MariaDB
- ✅ HTTP Server genera PNGs con gráficos
- ❌ **NO menciona MQTT**
- ❌ **NO menciona Telegram**

**Lo que está implementado**:
- `src/clients/mqtt_subscriber.py` - Cliente MQTT que NO se usa en el flujo principal
- Telegram bot integration - NO solicitado
- Flask server existe pero NO está integrado con los clientes

**Impacto**: ⭐⭐⭐⭐⭐ CRÍTICO

---

### 2. **FALTA HTTPClient EN LAZARUS PASCAL** 🚨
**Problema**: El PDF especifica que el HTTPClient debe programarse en Lazarus Pascal, pero no está completo.

**Requisito del PDF (página 2)**:
> "Programar un HTTPCliente (Método POST) que envíe todos los datos que están almacenados en data.dat a un Flask WEB Server"

> "El HTTPServer y HTTPCliente se programan en **Mode Consola**. No se aceptan desarrollos de los HTTPServer y Client utilizando GUI"

**Estado actual**:
- ✅ Existe: `tools/pas_client_send_data.pas` (stub de Lazarus)
- ❌ NO compilado
- ❌ NO probado
- ❌ NO ejecutable desde consola

**Impacto**: ⭐⭐⭐⭐⭐ CRÍTICO - Es un requisito mandatorio

---

### 3. **GRÁFICOS INCORRECTOS O INCOMPLETOS** 🚨
**Problema**: Los gráficos generados no cumplen con el formato especificado en el PDF.

**Lo que pide el PDF (página 2)**:

Debe mostrar **6 filas**:
1. **Fila 1**: Gráfica de h01 con label, unidades, etc. - Promedio móvil ventana 10
2. **Fila 2**: Gráfica de h25 (igual formato)
3. **Fila 3**: Gráfica de MP25 (µg/m³)
4. **Fila 4**: Gráfica de MP10 (µg/m³)
5. **Fila 5**: Gráfica de MP10 s011 (?)
6. **Fila 6**: **HISTOGRAMA** de h01, h25, h50, h10 (barra de colores verde, amarillo, rojo, azul)

**Ejemplo del PDF**:
```
[Gráfica con promedio móvil ventana 10 de cada serie]
[...5 gráficas de series...]
[Histograma de barras de colores para h01, h25, h50, h10]
```

**Lo implementado**:

**En `mqtt_subscriber.py` (líneas 150-200)**:
```python
# Solo 5 subplots - FALTA EL HISTOGRAMA
fig, axes = plt.subplots(5, 1, sharex=True, figsize=(8, 10))
# mp01, mp25, mp10, temp, hr
# ❌ NO incluye histograma
```

**En `plot_utils.py` (líneas 50-150)**:
```python
# Tiene 6 subplots incluyendo histograma
fig, axes = plt.subplots(6, 1, sharex=True, figsize=(9, 13))
# Row 6: Histogram - PERO usa datos que NO vienen en MQTT:
h_vals = [last.get('h01', 0), last.get('h25', 0), ...]
# ❌ Los clientes MQTT NO envían h01, h25, h50, h10
```

**Problemas**:
- ❌ `mqtt_subscriber.py` no genera histograma
- ❌ `plot_utils.py` espera campos `h01`, `h25`, `h50`, `h10` que NO están en el flujo MQTT
- ❌ Los gráficos no usan promedio móvil ventana 10 correctamente
- ❌ No coinciden con el formato visual del PDF

**Impacto**: ⭐⭐⭐⭐ ALTO

---

### 4. **FLASK SERVER NO INTEGRADO** 🚨
**Problema**: El Flask server existe pero NO se usa en el flujo principal.

**Lo que debería pasar (según PDF)**:
```
[ESP32 con PMS5003] → [WiFi] → [data.dat] 
       ↓
[HTTPClient Lazarus] → POST JSON + Stream → [Flask Server]
       ↓                                            ↓
   Console Output                          Almacena SQLite/MariaDB
                                                    ↓
                                           Genera PNG con 6 gráficas
```

**Lo que pasa actualmente**:
```
[MQTT Broker] → [mqtt_subscriber.py] → genera PNG localmente
                                    ↓
                              (Telegram Bot) ← NO solicitado

[Flask Server] ← NO recibe nada de los clientes
```

**Estado del Flask Server** (`src/http_server/app.py`):
- ✅ Endpoints implementados: `/upload-json`, `/upload-stream`, `/plot/<client_id>`
- ✅ Base de datos SQLite funcionando
- ❌ NO se ejecuta en modo consola visible
- ❌ NO recibe datos de ningún cliente en el flujo actual

**Impacto**: ⭐⭐⭐⭐⭐ CRÍTICO

---

### 5. **NO SE VEN LAS CONSOLAS** 🚨
**Problema**: El PDF especifica "Mode Consola" pero no hay consolas visibles.

**Requisito del PDF (página 2)**:
> "El HTTPServer y HTTPCliente se programan en **Mode Consola**. No se aceptan desarrollos de los HTTPServer y Client utilizando GUI"

**Estado actual**:
- Flask server corre con `app.run()` pero sin consola visible explícita
- No hay logging claro en consola para el servidor
- Los clientes MQTT corren en background
- El cliente Lazarus Pascal NO está funcionando

**Lo que se espera ver**:
```
[Consola HTTPServer]
===========================================
Flask HTTP Server - INFO1157 Proyecto #2
Escuchando en: http://127.0.0.1:5000
===========================================
[2025-10-31 10:15:32] Cliente conectado: client1
[2025-10-31 10:15:32] POST /upload-json recibido: 10 muestras
[2025-10-31 10:15:33] POST /upload-stream recibido: 2340 bytes
[2025-10-31 10:15:33] Datos guardados en SQLite
[2025-10-31 10:15:34] GET /plot/client1 - Generando gráfico...
[2025-10-31 10:15:35] Gráfico generado: 6 subplots, 150 dpi, 245KB
```

```
[Consola HTTPClient - Lazarus]
===========================================
HTTP Client - INFO1157 Proyecto #2
Cliente ID: client1
===========================================
[1] Leyendo data.dat...
    Registros encontrados: 100
    Última estación: 10
[2] Preparando JSON (últimas 10 muestras)...
    Payload: 1.2 KB
[3] POST /upload-json...
    Estado: 200 OK
    Respuesta: {"status":"ok","inserted":10}
[4] POST /upload-stream...
    Estado: 200 OK
    Respuesta: {"status":"ok","saved":"stream_1730372133.bin"}
[✓] Proceso completado exitosamente.
```

**Impacto**: ⭐⭐⭐⭐ ALTO - Es un requisito explícito

---

### 6. **ARCHIVOS DE CONFIGURACIÓN FALTANTES**
**Problema**: No existen los archivos `client1.json` ... `client4.json` mencionados en el README.

**Estado actual**:
```
✅ config_example.json - Plantilla
❌ client1.json - NO EXISTE
❌ client2.json - NO EXISTE
❌ client3.json - NO EXISTE
❌ client4.json - NO EXISTE
```

**Impacto**: ⭐⭐⭐ MEDIO

---

## ✅ LO QUE SÍ ESTÁ BIEN

### 1. **Parser de data.dat** ✅
`src/data_parser.py` está correctamente implementado:
- ✅ Lee estructura binaria según especificación del PDF
- ✅ Formato: `<BBB7H` (3 bytes + 7 words)
- ✅ Campos: id, te, hr, mp01, mp25, mp10, h01, h25, h50, h10
- ✅ Funciones `parse_file()` y `parse_bytes()`

### 2. **Generador de datos sintéticos** ✅
`tools/generate_data_dat.py`:
- ✅ Genera data.dat con formato correcto
- ✅ Parametrizable (estaciones, registros, seed)

### 3. **Estructura del proyecto** ✅
```
src/
  data_parser.py ✅
  plot_utils.py ✅
  http_server/app.py ✅
  http_client/send_data.py ✅
tools/
  generate_data_dat.py ✅
  pas_client_send_data.pas ⚠️ (existe pero incompleto)
tests/ ✅
```

### 4. **Flask Server (parcialmente)** ⚠️
`src/http_server/app.py`:
- ✅ Endpoints `/upload-json`, `/upload-stream`, `/plot/<client_id>`
- ✅ Base de datos SQLite
- ✅ Integración con `plot_utils.py`
- ⚠️ Falta modo consola visible
- ⚠️ No recibe datos en el flujo actual

### 5. **Tests unitarios** ✅
- ✅ `tests/test_data_parser.py`
- ✅ `tests/test_endpoints.py`
- ✅ `tests/test_edge_cases.py`

---

## 🔧 PLAN DE CORRECCIÓN PRIORITARIO

### **FASE 1: CORREGIR ARQUITECTURA (PRIORIDAD CRÍTICA)**

#### **Tarea 1.1: Completar HTTPClient en Lazarus Pascal**
**Objetivo**: Compilar y hacer funcional `pas_client_send_data.pas`

**Acciones**:
1. Instalar Lazarus IDE (si no está instalado)
2. Instalar componentes Indy (TIdHTTP)
3. Compilar `tools/pas_client_send_data.pas`
4. Probar con `data.dat` generado
5. Verificar salida en consola (no GUI)

**Código a revisar en `pas_client_send_data.pas`**:
```pascal
// Verificar que compile y use:
// - TIdHTTP para POST
// - Console output con WriteLn
// - Lectura de data.dat con TRegistro
```

**Tiempo estimado**: 2-3 horas

---

#### **Tarea 1.2: Modificar Flask Server para Modo Consola**
**Objetivo**: Hacer que el servidor muestre logs claros en consola

**Archivo**: `src/http_server/app.py`

**Cambios necesarios**:
```python
import logging
from datetime import datetime

# Configurar logging para consola
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Añadir al inicio del main:
def main():
    print("=" * 50)
    print("Flask HTTP Server - INFO1157 Proyecto #2")
    print("By Alberto Caro")
    print("Escuchando en: http://0.0.0.0:5000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False para prod

# Modificar cada endpoint para logear:
@app.route('/upload-json', methods=['POST'])
def upload_json():
    logging.info(f"POST /upload-json desde {request.remote_addr}")
    # ...resto del código...
    logging.info(f"Insertadas {len(samples)} muestras de {client_id}")
    return jsonify(...)
```

**Tiempo estimado**: 1 hora

---

#### **Tarea 1.3: Crear archivos de configuración client1-4.json**

**Archivo**: `client1.json`
```json
{
  "client_id": "client1",
  "server_url": "http://127.0.0.1:5000",
  "data_file": "data.dat"
}
```

Repetir para client2, client3, client4 con diferentes `client_id`.

**Tiempo estimado**: 15 minutos

---

### **FASE 2: CORREGIR GRÁFICOS (PRIORIDAD ALTA)**

#### **Tarea 2.1: Corregir plot_utils.py para incluir datos h01-h10**

**Problema**: El parser lee correctamente h01, h25, h50, h10 de `data.dat`, pero el servidor no los recibe en el POST JSON.

**Solución**: Modificar `send_data.py` y `app.py` para incluir estos campos.

**Archivo**: `src/http_client/send_data.py` (líneas 95-110)
```python
# ANTES:
samples.append({
    'ts': now - (len(records[-10:]) - 1 - i) * 60,
    'mp01': r.get('mp01'),
    'mp25': r.get('mp25'),
    'mp10': r.get('mp10'),
    'temp': r.get('te'),
    'hr': r.get('hr')
})

# DESPUÉS:
samples.append({
    'ts': now - (len(records[-10:]) - 1 - i) * 60,
    'mp01': r.get('mp01'),
    'mp25': r.get('mp25'),
    'mp10': r.get('mp10'),
    'temp': r.get('te'),
    'hr': r.get('hr'),
    'h01': r.get('h01'),    # ← AÑADIR
    'h25': r.get('h25'),    # ← AÑADIR
    'h50': r.get('h50'),    # ← AÑADIR
    'h10': r.get('h10')     # ← AÑADIR
})
```

**Archivo**: `src/http_server/app.py` (líneas 60-70)
```python
# Modificar esquema de BD y INSERT:
c.execute('''
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT,
        ts INTEGER,
        mp01 REAL, mp25 REAL, mp10 REAL,
        temp REAL, hr REAL,
        h01 REAL, h25 REAL, h50 REAL, h10 REAL  -- ← AÑADIR
    )
''')

# Actualizar INSERT:
c.execute('''INSERT INTO measurements 
    (client_id, ts, mp01, mp25, mp10, temp, hr, h01, h25, h50, h10) 
    VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
    (client_id, ts, s.get('mp01'), s.get('mp25'), s.get('mp10'), 
     s.get('temp'), s.get('hr'),
     s.get('h01'), s.get('h25'), s.get('h50'), s.get('h10')))
```

**Tiempo estimado**: 1-2 horas

---

#### **Tarea 2.2: Verificar formato de gráficos según PDF**

Revisar que `plot_utils.py` genere exactamente:
- ✅ 6 subplots (5 series + 1 histograma)
- ✅ Promedio móvil ventana 10 visible
- ✅ Labels y unidades correctas
- ✅ Colores del histograma: verde, amarillo, rojo, azul

**Ya está implementado correctamente** en `plot_utils.py` líneas 50-150.

---

### **FASE 3: INTEGRACIÓN Y PRUEBAS (PRIORIDAD MEDIA)**

#### **Tarea 3.1: Script de ejecución completo**

**Crear**: `run_http_flow.ps1`
```powershell
# 1. Activar entorno
.\.venv\Scripts\Activate.ps1

# 2. Generar data.dat
python tools\generate_data_dat.py --out data.dat --count 10 --stations 10

# 3. Iniciar Flask server en background
Start-Process python -ArgumentList "src\http_server\app.py" -NoNewWindow

# 4. Esperar a que el servidor inicie
Start-Sleep -Seconds 3

# 5. Ejecutar cliente HTTP (Python primero, luego Lazarus)
python src\http_client\send_data.py --data-file data.dat --client-id client1

# 6. Descargar gráfico
Invoke-WebRequest -Uri "http://127.0.0.1:5000/plot/client1" -OutFile "plot_client1.png"

Write-Host "✓ Proceso completado. Ver: plot_client1.png"
```

**Tiempo estimado**: 30 minutos

---

#### **Tarea 3.2: Eliminar/Archivar código MQTT/Telegram**

**Acción**: Mover a `archive/` los archivos NO solicitados:
- `src/clients/mqtt_subscriber.py` → `archive/mqtt_legacy/`
- `config_example.json` (configs MQTT) → `archive/mqtt_legacy/`
- Toda referencia a Telegram en README

**Tiempo estimado**: 15 minutos

---

#### **Tarea 3.3: Actualizar README.md**

Reescribir el README con:
1. Descripción del proyecto según PDF
2. Requisitos: Lazarus, Python, Flask
3. Cómo ejecutar (HTTPClient Lazarus + HTTPServer Flask)
4. Capturas de consola
5. Estructura de data.dat

**Tiempo estimado**: 1 hora

---

## 📊 RESUMEN DE IMPACTO

| Problema | Impacto | Tiempo | Estado |
|----------|---------|--------|--------|
| HTTPClient Lazarus incompleto | ⭐⭐⭐⭐⭐ CRÍTICO | 2-3h | ❌ Pendiente |
| Flask Server no visible en consola | ⭐⭐⭐⭐ ALTO | 1h | ❌ Pendiente |
| Gráficos sin histograma correcto | ⭐⭐⭐⭐ ALTO | 1-2h | ⚠️ Parcial |
| Arquitectura MQTT incorrecta | ⭐⭐⭐⭐⭐ CRÍTICO | 1h | ❌ Pendiente |
| Archivos config faltantes | ⭐⭐⭐ MEDIO | 15min | ❌ Pendiente |
| Documentación desactualizada | ⭐⭐⭐ MEDIO | 1h | ❌ Pendiente |

**Total tiempo estimado de corrección**: 7-10 horas

---

## 🎯 PRÓXIMOS PASOS RECOMENDADOS

### **OPCIÓN A: Corrección Completa (Recomendado)**
1. ✅ Completar HTTPClient en Lazarus Pascal
2. ✅ Modificar Flask Server para modo consola
3. ✅ Corregir gráficos (añadir h01-h10)
4. ✅ Crear archivos client1-4.json
5. ✅ Archivar código MQTT/Telegram
6. ✅ Actualizar README
7. ✅ Pruebas end-to-end
8. ✅ Documentar con capturas

### **OPCIÓN B: Corrección Mínima Viable**
1. ✅ Completar HTTPClient Lazarus
2. ✅ Añadir logs de consola al Flask Server
3. ✅ Verificar gráficos con data.dat real
4. ✅ Crear script de ejecución

---

## 📝 CONCLUSIÓN

El proyecto tiene una **base técnica sólida** (parser, servidor Flask, generador de datos) pero implementa una **arquitectura completamente diferente** a la solicitada en el PDF:

- ❌ Se desarrolló un sistema MQTT + Telegram NO pedido
- ❌ Falta el HTTPClient en Lazarus Pascal (requisito mandatorio)
- ❌ No hay consolas visibles (requisito explícito)
- ❌ Los gráficos no incluyen correctamente el histograma

**Tiempo estimado de corrección**: 7-10 horas de trabajo enfocado.

**Recomendación**: Seguir la **Opción A** para cumplir al 100% con los requisitos del PDF y garantizar una evaluación positiva del proyecto.

---

**Generado el**: 31 de octubre de 2025  
**Por**: GitHub Copilot  
**Para**: Proyecto INFO1157 - Alberto Caro
