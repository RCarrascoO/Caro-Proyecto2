# Proyecto #2 - Sistemas Inteligentes INFO1157
## Sistema de Monitoreo Ambiental IoT

**Por**: Alberto Caro  
**Curso**: INFO1157 - Sistemas Inteligentes  
**Tema**: Sistemas Embebidos + Sensores (IoT)

---

## 📋 Descripción

Sistema de adquisición, transmisión y visualización de datos ambientales desde sensores IoT. Implementa un **HTTPClient** que lee datos binarios de sensores (archivo `data.dat`) y los envía a un **HTTPServer Flask** que almacena en base de datos SQLite y genera gráficos PNG con análisis estadístico.

### Flujo del Sistema

```
ESP32 + PMS5003  →  WiFi  →  data.dat (binario)
                                 ↓
                          HTTP Client (POST)
                                 ↓
                          HTTP Server (Flask)
                                 ↓
                    ┌────────────┴────────────┐
                    ↓                         ↓
              SQLite/MariaDB            Gráficos PNG
                                       (6 subplots)
```

---

## 🚀 Inicio Rápido

### Instalación

```powershell
# 1. Clonar repositorio
git clone https://github.com/RCarrascoO/Caro-Proyecto2.git
cd Caro-Proyecto2

# 2. Crear entorno virtual
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Ejecución (Automática)

```powershell
# Ejecutar flujo completo
.\scripts\run_http_flow.ps1
```

Esto generará automáticamente:
- `data.dat` con datos sintéticos
- Base de datos SQLite con mediciones
- Gráfico PNG en `outputs/plot_client1.png`

---

## 📁 Estructura del Proyecto

```
Caro-Proyecto2/
│
├── src/                         # Código fuente principal
│   ├── data_parser.py           # Parser de archivos binarios data.dat
│   ├── plot_utils.py            # Generación de gráficos (6 subplots)
│   ├── http_server/
│   │   └── app.py               # Servidor Flask (endpoints REST)
│   └── http_client/
│       └── send_data.py         # Cliente HTTP (POST JSON + Stream)
│
├── tests/                       # Tests unitarios
│   ├── test_data_parser.py      # Tests del parser binario
│   ├── test_endpoints.py        # Tests de endpoints Flask
│   └── test_edge_cases.py       # Tests de casos límite
│
├── tools/                       # Herramientas auxiliares
│   ├── generate_data_dat.py     # Generador de datos sintéticos
│   ├── e2e_inproc_test.py       # Test end-to-end
│   ├── run_e2e.ps1              # Script de pruebas E2E
│   └── pas_client_send_data.pas # Cliente HTTP en Lazarus Pascal
│
├── config/                      # Archivos de configuración
│   ├── client1.json             # Config cliente 1
│   ├── client2.json             # Config cliente 2
│   ├── client3.json             # Config cliente 3
│   └── client4.json             # Config cliente 4
│
├── scripts/                     # Scripts de ejecución
│   ├── run_http_flow.ps1        # Script principal (flujo completo)
│   ├── start_all.ps1            # Script alternativo
│   └── run_all.py               # Script Python alternativo
│
├── docs/                        # Documentación
│   ├── ANALISIS_PROYECTO.md     # Análisis detallado vs PDF
│   ├── CORRECCIONES_COMPLETADAS.md  # Log de correcciones
│   ├── PDF_Original/            # PDF del proyecto y capturas
│   └── README_NEW.md            # README alternativo
│
├── data/                        # Datos y base de datos
│   ├── data.db                  # Base de datos SQLite (generada)
│   ├── fixtures/                # Datos de prueba
│   └── streams/                 # Streams binarios recibidos
│
├── outputs/                     # Archivos generados
│   ├── .gitkeep                 # (gráficos y data.dat se generan aquí)
│   └── plot_client*.png         # Gráficos generados
│
├── archive/                     # Código legacy/archivado
│   └── mqtt_legacy/             # Implementación MQTT antigua
│
├── .gitignore                   # Archivos ignorados por Git
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

---

## 📊 Estructura de Datos

### Archivo `data.dat` (Formato Binario)

```pascal
TRegistro = record
  id   : Byte;    // ID de estación (1-10)
  te   : Byte;    // Temperatura en °C
  hr   : Byte;    // Humedad relativa en %
  mp01 : Word;    // Material particulado 1.0 µm (µg/m³)
  mp25 : Word;    // Material particulado 2.5 µm (µg/m³)
  mp10 : Word;    // Material particulado 10 µm (µg/m³)
  h01  : Word;    // Histograma partículas 1.0 µm
  h25  : Word;    // Histograma partículas 2.5 µm
  h50  : Word;    // Histograma partículas 5.0 µm
  h10  : Word;    // Histograma partículas 10 µm
end;
```

**Formato**: Little-endian, 23 bytes por registro

---

## 🔌 API del Servidor

### `POST /upload-json`
Recibe datos en formato JSON.

**Request**:
```json
{
  "client_id": "client1",
  "samples": [
    {
      "ts": 1730425800,
      "mp01": 12, "mp25": 25, "mp10": 45,
      "temp": 23, "hr": 65,
      "h01": 100, "h25": 80, "h50": 60, "h10": 40
    }
  ]
}
```

**Response**:
```json
{"status": "ok", "inserted": 10}
```

### `POST /upload-stream`
Recibe datos binarios (formato `data.dat`).

**Headers**: 
- `Content-Type: application/octet-stream`
- `X-PARSE: 1` (opcional, para parsear automáticamente)

**Response**:
```json
{"status": "ok", "saved": "stream_123.bin", "inserted": 100}
```

### `GET /plot/<client_id>`
Genera y descarga gráfico PNG con 6 subplots.

**Ejemplo**: `http://127.0.0.1:5000/plot/client1`

---

## 📈 Gráficos Generados

El servidor genera PNG con **6 subplots**:

1. **Temperatura (te)** - Serie temporal + promedio móvil (ventana=10)
2. **Humedad (hr)** - Serie temporal + promedio móvil
3. **MP 1.0** - Material particulado 1.0 µm
4. **MP 2.5** - Material particulado 2.5 µm  
5. **MP 10** - Material particulado 10 µm
6. **Histograma** - Barras de h01, h25, h50, h10 (colores: verde, amarillo, rojo, azul)

**Formato**: PNG, 150 dpi, ~80-100 KB

---

## 🧪 Pruebas

### Ejecutar todos los tests

```powershell
python -m pytest tests/ -v
```

### Test end-to-end

```powershell
# PowerShell
.\tools\run_e2e.ps1

# Python
python tools\e2e_inproc_test.py
```

### Generar datos de prueba

```powershell
python tools\generate_data_dat.py --out test.dat --count 10 --stations 5 --seed 42
```

---

## 🛠️ Uso Avanzado

### Ejecutar servidor manualmente

```powershell
# Terminal 1: Servidor Flask
python src\http_server\app.py
```

El servidor mostrará:
```
============================================================
  Flask HTTP Server - INFO1157 Proyecto #2
  By Alberto Caro
============================================================
  Servidor escuchando en: http://0.0.0.0:5000
============================================================
```

### Ejecutar cliente manualmente

```powershell
# Terminal 2: Cliente HTTP
python src\http_client\send_data.py ^
    --server http://127.0.0.1:5000 ^
    --data-file outputs\data.dat ^
    --client-id client1
```

### Descargar gráfico

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/plot/client1" -OutFile "outputs\plot_client1.png"
```

### Múltiples clientes

```powershell
# Usar diferentes configuraciones
.\scripts\run_http_flow.ps1 -ClientId client1
.\scripts\run_http_flow.ps1 -ClientId client2 -NoGenerate
```

---

## 🗃️ Base de Datos

### Esquema SQLite

```sql
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT,
    ts INTEGER,           -- Unix timestamp
    mp01 REAL,            -- PM 1.0 µm
    mp25 REAL,            -- PM 2.5 µm
    mp10 REAL,            -- PM 10 µm
    temp REAL,            -- Temperatura °C
    hr REAL,              -- Humedad %
    h01 REAL,             -- Histograma 1.0
    h25 REAL,             -- Histograma 2.5
    h50 REAL,             -- Histograma 5.0
    h10 REAL              -- Histograma 10
);
```

### Consultar datos

```powershell
sqlite3 data\data.db

# Ejemplos de consultas
SELECT client_id, COUNT(*) FROM measurements GROUP BY client_id;
SELECT * FROM measurements WHERE client_id = 'client1' LIMIT 10;
```

---

## 📦 Dependencias

Ver `requirements.txt`. Principales:

- **Flask 2.3.3** - Framework web
- **matplotlib 3.10.7** - Generación de gráficos
- **numpy 2.3.3** - Procesamiento numérico
- **requests 2.32.5** - Cliente HTTP

---

## 🐛 Troubleshooting

### Puerto 5000 en uso
```powershell
# Buscar proceso
netstat -ano | findstr :5000

# Matar proceso
taskkill /PID <PID> /F
```

### Error: "No module named 'flask'"
```powershell
# Verificar entorno virtual
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### No se generan gráficos
```powershell
# Verificar que se enviaron datos
sqlite3 data\data.db "SELECT COUNT(*) FROM measurements;"

# Regenerar gráfico
Invoke-WebRequest -Uri http://127.0.0.1:5000/plot/client1 -OutFile outputs\plot.png
```

---

## 📚 Documentación Adicional

Ver carpeta `docs/` para:
- **ANALISIS_PROYECTO.md** - Análisis completo vs requisitos del PDF
- **CORRECCIONES_COMPLETADAS.md** - Log de cambios y correcciones
- **PDF_Original/** - PDF del proyecto y capturas

---

## 🎓 Información Académica

**Proyecto**: #2 - Sistemas Inteligentes  
**Curso**: INFO1157  
**Tema**: IoT - Sistemas Embebidos + Sensores  
**Alumno**: Alberto Caro  
**Fecha**: Octubre 2025  

---

## 📄 Licencia

Proyecto académico - Universidad [Nombre]  
Todos los derechos reservados © 2025

---

## 🤝 Contacto

**GitHub**: https://github.com/RCarrascoO/Caro-Proyecto2  
**Alumno**: Alberto Caro

---

**Última actualización**: 31 de octubre de 2025
