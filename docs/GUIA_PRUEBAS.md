# 🧪 GUÍA DE PRUEBAS DEL PROYECTO

**Proyecto**: INFO1157 - Sistemas Inteligentes - Proyecto #2  
**Fecha**: 31 de octubre de 2025

---

## 🚀 CÓMO PROBAR EL PROYECTO (COMPLETO)

### **OPCIÓN 1: Prueba Automática (Recomendada)**

#### **1.1 Flujo Completo HTTP**
```powershell
# Desde la raíz del proyecto
.\scripts\run_http_flow.ps1
```

**¿Qué hace?**
1. ✅ Genera `outputs\data.dat` con 100 registros sintéticos
2. ✅ Inicia el servidor Flask en modo consola (puerto 5000)
3. ✅ Ejecuta el cliente HTTP Python que envía:
   - POST JSON a `/upload-json`
   - POST Stream binario a `/upload-stream`
4. ✅ Descarga el gráfico PNG generado
5. ✅ Detiene el servidor

**Archivos generados:**
- `outputs\data.dat` - Datos binarios (23 bytes × 100 registros)
- `outputs\plot_client1.png` - Gráfico de 6 subplots
- `data\data.db` - Base de datos SQLite

**Verificación:**
```powershell
# Ver tamaño de archivos generados
Get-ChildItem outputs\, data\ -Include *.dat, *.png, *.db -Recurse

# Ver imagen generada (abrirla)
Start-Process outputs\plot_client1.png
```

---

#### **1.2 Solo Servidor (Modo Manual)**
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Iniciar servidor Flask
python src\http_server\app.py
```

**Console Output esperado:**
```
╔═══════════════════════════════════════════════════╗
║       HTTP SERVER - MODO CONSOLA                  ║
║       Sistemas Inteligentes - Proyecto #2         ║
╚═══════════════════════════════════════════════════╝

[INFO] Servidor corriendo en http://0.0.0.0:5000
[INFO] Base de datos: data/data.db
[INFO] Endpoints disponibles:
  • POST /upload-json       - Recibir datos JSON
  • POST /upload-stream     - Recibir datos binarios
  • GET  /plot/<client_id>  - Generar gráfico PNG
```

**Probar endpoints manualmente:**
```powershell
# En otra terminal, generar datos
python tools\generate_data_dat.py --output outputs\data.dat --records 50

# Enviar datos con cliente Python
python src\http_client\send_data.py config\client1.json

# O usar curl (Windows)
curl -X POST http://127.0.0.1:5000/upload-json -H "Content-Type: application/json" -d "{\"client_id\":\"test\",\"samples\":[{\"id\":1,\"te\":25,\"hr\":60,\"mp01\":10,\"mp25\":15,\"mp10\":20,\"h01\":5,\"h25\":8,\"h50\":10,\"h10\":3}]}"
```

---

#### **1.3 Cliente Específico**
```powershell
# Cliente 2 (sin generar datos nuevos)
.\scripts\run_http_flow.ps1 -ClientId client2 -NoGenerate

# Cliente 3 sin instalar dependencias
.\scripts\run_http_flow.ps1 -ClientId client3 -NoInstall
```

---

### **OPCIÓN 2: Pruebas Unitarias**

#### **2.1 Ejecutar Todos los Tests**
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar pytest
pytest tests\ -v

# Con cobertura
pytest tests\ --cov=src --cov-report=html
```

**Tests disponibles:**
- `test_data_parser.py` - Parseo de archivos binarios
- `test_endpoints.py` - Endpoints Flask
- `test_edge_cases.py` - Casos límite

**Output esperado:**
```
tests/test_data_parser.py::test_parse_file PASSED       [33%]
tests/test_data_parser.py::test_parse_bytes PASSED      [66%]
tests/test_endpoints.py::test_upload_json PASSED        [100%]

====== 3 passed in 0.5s ======
```

---

#### **2.2 Tests Individuales**
```powershell
# Solo parser
pytest tests\test_data_parser.py -v

# Solo endpoints
pytest tests\test_endpoints.py -v

# Test específico
pytest tests\test_data_parser.py::test_parse_file -v
```

---

### **OPCIÓN 3: Prueba End-to-End (E2E)**

#### **3.1 Test E2E In-Process**
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar E2E
python tools\e2e_inproc_test.py
```

**¿Qué hace?**
- Genera datos sintéticos en memoria
- Inicia servidor Flask en thread separado
- Envía datos al servidor
- Verifica que se almacenaron correctamente
- Genera y valida el gráfico PNG

---

#### **3.2 Test E2E con PowerShell**
```powershell
.\tools\run_e2e.ps1
```

---

### **OPCIÓN 4: Cliente Lazarus Pascal** ⚠️

**ESTADO**: NO COMPILADO AÚN

#### **4.1 Compilar Cliente Pascal**
```powershell
# Requisitos:
# - Lazarus IDE instalado
# - Indy Components (TIdHTTP) instalados

# Compilar desde línea de comandos
lazbuild tools\pas_client_send_data.pas

# O abrir en Lazarus IDE
# File → Open → tools\pas_client_send_data.pas
# Run → Compile
```

#### **4.2 Ejecutar Cliente Pascal**
```powershell
# Una vez compilado
.\tools\pas_client_send_data.exe config\client1.json
```

**PENDIENTE DE IMPLEMENTAR** 🔴

---

## 📊 VERIFICACIÓN DE RESULTADOS

### **1. Verificar Base de Datos**

```powershell
# Instalar sqlite3 si no está instalado
# choco install sqlite (con Chocolatey)

# Abrir base de datos
sqlite3 data\data.db

# Consultas SQL
.tables                        # Ver tablas
SELECT COUNT(*) FROM measurements;  # Contar registros
SELECT * FROM measurements LIMIT 5; # Ver primeros 5
.quit
```

**Esquema de tabla `measurements`:**
```sql
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    station_id INTEGER NOT NULL,
    te REAL,
    hr REAL,
    mp01 REAL,
    mp25 REAL,
    mp10 REAL,
    h01 REAL,
    h25 REAL,
    h50 REAL,
    h10 REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### **2. Verificar Gráfico PNG**

```powershell
# Abrir imagen generada
Start-Process outputs\plot_client1.png

# Ver propiedades
Get-Item outputs\plot_client1.png | Format-List
```

**Debe contener 6 subplots:**
1. **Temperatura (te)** - Serie temporal con media móvil
2. **Humedad (hr)** - Serie temporal con media móvil
3. **MP01** - Serie temporal con media móvil
4. **MP25** - Serie temporal con media móvil
5. **MP10** - Serie temporal con media móvil
6. **Histograma** - Barras de h01, h25, h50, h10

---

### **3. Verificar Logs del Servidor**

**Debe mostrar:**
```
[2025-10-31 14:30:15] REQUEST: POST /upload-json from 127.0.0.1
[2025-10-31 14:30:15] SUCCESS: Stored 100 samples for client1
[2025-10-31 14:30:16] REQUEST: POST /upload-stream from 127.0.0.1
[2025-10-31 14:30:16] STREAM: Received 2300 bytes from client1
[2025-10-31 14:30:16] PARSE: Parsed 100 records
[2025-10-31 14:30:17] REQUEST: GET /plot/client1 from 127.0.0.1
[2025-10-31 14:30:18] SUCCESS: Generated plot for client1 (85KB PNG)
```

---

## 🔍 TROUBLESHOOTING

### **Error: "Puerto 5000 ya en uso"**
```powershell
# Matar proceso en puerto 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# O usar puerto diferente
$env:FLASK_PORT = "5001"
python src\http_server\app.py
```

---

### **Error: "ModuleNotFoundError"**
```powershell
# Reinstalar dependencias
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### **Error: "data.dat not found"**
```powershell
# Generar datos manualmente
python tools\generate_data_dat.py --output outputs\data.dat
```

---

### **Gráfico no se genera**
```powershell
# Verificar que matplotlib use backend Agg
python -c "import matplotlib; print(matplotlib.get_backend())"

# Debe mostrar: Agg
```

---

## ✅ CHECKLIST DE PRUEBAS

### **Flujo HTTP Completo**
- [ ] Generación de `data.dat` exitosa
- [ ] Servidor Flask inicia correctamente
- [ ] Cliente envía datos JSON (POST /upload-json)
- [ ] Cliente envía datos stream (POST /upload-stream)
- [ ] Datos se almacenan en SQLite
- [ ] Gráfico PNG se genera correctamente
- [ ] 6 subplots visibles en PNG

### **Tests Unitarios**
- [ ] `test_data_parser.py` pasa
- [ ] `test_endpoints.py` pasa
- [ ] `test_edge_cases.py` pasa

### **Verificación Manual**
- [ ] Base de datos contiene registros
- [ ] PNG tiene 6 subplots con datos
- [ ] Logs del servidor son legibles
- [ ] Archivos en carpetas correctas

### **Cliente Pascal** ⚠️
- [ ] Código compila sin errores
- [ ] Ejecutable funciona desde consola
- [ ] Envía datos al servidor
- [ ] Datos se almacenan correctamente

---

## 📝 NOTAS IMPORTANTES

### **Arquitectura Implementada**
✅ **HTTP Client/Server** (Python implementado)  
⚠️ **Lazarus Pascal Client** (pendiente de compilación)  
❌ **MQTT** (archivado - NO es parte del proyecto según PDF)

### **Datos de Prueba**
- Cada registro = 23 bytes (3 bytes + 7 words × 2 bytes)
- 100 registros = 2300 bytes
- Generación aleatoria con seed fijo para reproducibilidad

### **Configuraciones Múltiples**
El proyecto soporta múltiples clientes simultáneos:
- `config/client1.json` → `plot_client1.png`
- `config/client2.json` → `plot_client2.png`
- `config/client3.json` → `plot_client3.png`
- `config/client4.json` → `plot_client4.png`

---

## 🎯 PRÓXIMOS PASOS

1. **Compilar cliente Lazarus Pascal** 🔴 PENDIENTE
2. Probar con datos reales de ESP32 + PMS5003
3. Implementar soporte MariaDB (opcional)
4. Agregar autenticación a endpoints
5. Dockerizar aplicación

---

**Última actualización**: 31 de octubre de 2025
