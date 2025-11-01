# Proyecto #2 - Sistemas Inteligentes INFO1157
## By Alberto Caro

---

## 📋 Descripción del Proyecto

Sistema de adquisición y visualización de datos ambientales para IoT (Internet de las Cosas) + Sistemas Inteligentes. El proyecto implementa un **HTTPClient** que envía datos de sensores a un **HTTPServer Flask** que los almacena en base de datos (SQLite/MariaDB) y genera gráficos PNG con análisis de series temporales.

### 🎯 Objetivo

Desarrollar la capa de comunicación entre dispositivos embebidos (ESP32 + sensor PMS5003) y un servidor de procesamiento mediante:
- **HTTP Client**: Lee archivo binario `data.dat` y envía datos mediante POST (JSON + Stream)
- **HTTP Server**: Recibe datos, los almacena en BD y genera gráficos PNG con 6 subplots

---

## 🚀 Inicio Rápido

### Ejecución Automática (Recomendado)

```powershell
.\run_http_flow.ps1
```

Este script ejecuta todo el flujo automáticamente y genera `plot_client1.png`.

---

## 📂 Estructura del Proyecto

```
Caro-Proyecto2/
├── src/
│   ├── data_parser.py          # Parser de data.dat
│   ├── plot_utils.py            # Generación de gráficos (6 subplots)
│   ├── http_server/app.py      # Servidor Flask
│   └── http_client/send_data.py # Cliente HTTP
├── tools/                       # Herramientas auxiliares
├── tests/                       # Tests unitarios
├── client1-4.json              # Configuraciones
├── run_http_flow.ps1           # Script principal
└── README.md
```

---

## 📊 Estructura de Datos (data.dat)

```pascal
TRegistro = record
  id   : Byte;    // ID estación (1-10)
  te   : Byte;    // Temperatura (°C)
  hr   : Byte;    // Humedad (%)
  mp01 : Word;    // PM 1.0 µm
  mp25 : Word;    // PM 2.5 µm
  mp10 : Word;    // PM 10 µm
  h01  : Word;    // Histograma 1.0
  h25  : Word;    // Histograma 2.5
  h50  : Word;    // Histograma 5.0
  h10  : Word;    // Histograma 10
end;
```

**Formato**: Little-endian, 23 bytes/registro

---

## 🔌 Endpoints del Servidor

- `POST /upload-json` - Recibe datos JSON
- `POST /upload-stream` - Recibe datos binarios
- `GET /plot/<client_id>` - Descarga gráfico PNG

---

## 📈 Gráficos Generados

El servidor genera PNG con 6 subplots:
1-5. Series temporales (temperatura, humedad, MP01, MP2.5, MP10)
6. Histograma de partículas (h01, h25, h50, h10)

---

**Ver documentación completa en el archivo o ejecutar `.\run_http_flow.ps1` para probar**
