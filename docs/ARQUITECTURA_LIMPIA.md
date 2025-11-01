# Arquitectura del Proyecto - Clean Architecture

## 📐 Principios Aplicados

Este proyecto sigue los principios de **Clean Architecture** (Arquitectura Limpia) adaptados para un proyecto Python de tamaño medio:

### 1. **Separación de Responsabilidades**
- **src/** - Código fuente (lógica de negocio, parsers, utilidades)
- **tests/** - Pruebas unitarias e integración
- **tools/** - Herramientas auxiliares y scripts de desarrollo
- **scripts/** - Scripts de ejecución y automatización
- **config/** - Configuración (separada del código)
- **docs/** - Documentación (separada del código)
- **outputs/** - Salidas generadas (no versionadas)
- **data/** - Datos y BD (gitignored, solo estructura)

### 2. **Dependencias Hacia Dentro**
```
┌─────────────────────────────────────┐
│         Interfaces (HTTP)           │
│    (app.py, send_data.py)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Application Logic              │
│   (plot_utils.py, negocio)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Domain / Core                  │
│    (data_parser.py)                │
└─────────────────────────────────────┘
```

### 3. **Independencia de Frameworks**
- Core (data_parser.py) no depende de Flask
- Lógica de gráficos (plot_utils.py) es reutilizable
- Tests no requieren servidor HTTP

### 4. **Testeable**
- Tests unitarios en `tests/`
- Tests E2E en `tools/e2e_inproc_test.py`
- Mocking fácil por separación de capas

---

## 📁 Estructura Detallada

### `src/` - Código Fuente

```
src/
├── __init__.py              # Package marker
├── data_parser.py           # CORE: Parser de datos binarios
├── plot_utils.py            # APPLICATION: Generación de gráficos
├── http_server/
│   └── app.py               # INTERFACE: API REST Flask
└── http_client/
    └── send_data.py         # INTERFACE: Cliente HTTP
```

**Capas**:
- **Core/Domain**: `data_parser.py` - Conoce solo Python estándar
- **Application**: `plot_utils.py` - Usa matplotlib, numpy
- **Interface**: `app.py`, `send_data.py` - Usan Flask, requests

### `tests/` - Pruebas

```
tests/
├── test_data_parser.py      # Tests del core
├── test_endpoints.py        # Tests de integración
└── test_edge_cases.py       # Tests de casos límite
```

**Estrategia de Testing**:
- Unit tests para `data_parser.py` (sin dependencias)
- Integration tests para endpoints Flask
- E2E tests en `tools/`

### `tools/` - Herramientas de Desarrollo

```
tools/
├── generate_data_dat.py     # Generador de datos de prueba
├── e2e_inproc_test.py       # Test end-to-end in-process
├── run_e2e.ps1              # Script de test E2E
├── pas_client_send_data.pas # Cliente alternativo (Lazarus)
└── README.md                # Documentación de herramientas
```

### `config/` - Configuración

```
config/
├── client1.json
├── client2.json
├── client3.json
└── client4.json
```

**Principio**: Configuración separada del código (12 Factor App)

### `scripts/` - Scripts de Ejecución

```
scripts/
├── run_http_flow.ps1        # Script principal (PowerShell)
├── start_all.ps1            # Script alternativo
└── run_all.py               # Script alternativo (Python)
```

### `docs/` - Documentación

```
docs/
├── ANALISIS_PROYECTO.md             # Análisis vs requisitos
├── CORRECCIONES_COMPLETADAS.md      # Changelog
├── ARQUITECTURA_LIMPIA.md           # Este archivo
└── PDF_Original/                    # PDFs del proyecto
```

### `data/` - Datos y Base de Datos

```
data/
├── .gitignore               # Ignora DB y streams
├── data.db                  # SQLite (generado, no versionado)
├── fixtures/                # Datos de prueba fixture
│   └── data.dat
└── streams/                 # Streams recibidos
    └── .gitkeep
```

**Principio**: Datos no se versionan, solo estructura

### `outputs/` - Salidas Generadas

```
outputs/
├── .gitkeep
├── data.dat                 # Generado por scripts
└── plot_*.png               # Gráficos generados
```

**Principio**: Outputs son efímeros, regenerables

### `archive/` - Código Legacy

```
archive/
├── mqtt_legacy/             # Implementación MQTT antigua
└── removed_*.zip            # Backups
```

---

## 🔄 Flujo de Datos

### 1. Generación de Datos
```
tools/generate_data_dat.py
    ↓
outputs/data.dat (binario)
```

### 2. Lectura y Parseo
```
outputs/data.dat
    ↓
src/data_parser.py (parse_file)
    ↓
List[Dict] (registros parseados)
```

### 3. Envío HTTP
```
src/http_client/send_data.py
    ├→ POST /upload-json (JSON)
    └→ POST /upload-stream (binario)
         ↓
    src/http_server/app.py
         ↓
    data/data.db (SQLite)
```

### 4. Generación de Gráficos
```
GET /plot/<client_id>
    ↓
src/http_server/app.py
    ↓
src/plot_utils.py (build_timeseries_plot)
    ↓
BytesIO PNG (6 subplots)
```

---

## 🧪 Estrategia de Testing

### Pirámide de Tests

```
           ╱╲
          ╱E2E╲         ← 1-2 tests (tools/e2e_inproc_test.py)
         ╱────╲
        ╱ INT  ╲        ← 5-10 tests (tests/test_endpoints.py)
       ╱────────╲
      ╱   UNIT   ╲      ← 20+ tests (tests/test_data_parser.py, etc.)
     ╱────────────╲
```

### Niveles de Testing

1. **Unit Tests** (Base)
   - `test_data_parser.py`: Parser sin dependencias
   - Fast (~ms), aislados, sin I/O

2. **Integration Tests** (Medio)
   - `test_endpoints.py`: Flask + SQLite
   - Medium speed (~100ms), BD en memoria

3. **E2E Tests** (Cima)
   - `e2e_inproc_test.py`: Flujo completo
   - Slow (~segundos), I/O real

---

## 🏗️ Decisiones de Arquitectura

### ¿Por qué esta estructura?

#### ✅ **Separación de Capas**
- **Core** (`data_parser.py`) no conoce Flask ni matplotlib
- **Application** (`plot_utils.py`) no conoce HTTP
- **Interface** (`app.py`, `send_data.py`) orquestan

**Ventaja**: Puedo cambiar Flask por FastAPI sin tocar el core.

#### ✅ **Config como Código**
- JSON en `config/` en lugar de hardcoded
- Fácil de modificar sin tocar Python

**Ventaja**: 4 clientes con 1 solo código.

#### ✅ **Outputs Separados**
- Generados en `outputs/`, no en raíz
- Gitignored automáticamente

**Ventaja**: Repositorio limpio, regenerables.

#### ✅ **Docs Separados**
- Markdown en `docs/`, no en raíz
- README principal corto y directo

**Ventaja**: Fácil navegación, no abruma.

#### ✅ **Scripts en Carpeta**
- PowerShell/Python en `scripts/`
- No mezclados con código fuente

**Ventaja**: Clara separación código vs automatización.

---

## 🔐 Principios SOLID Aplicados

### **S** - Single Responsibility
- `data_parser.py`: Solo parsear binario
- `plot_utils.py`: Solo generar gráficos
- `app.py`: Solo HTTP endpoints

### **O** - Open/Closed
- `plot_utils.py` acepta cualquier lista de samples
- Extensible: añadir nuevos tipos de gráficos

### **L** - Liskov Substitution
- `parse_file()` y `parse_bytes()` son intercambiables
- Ambos devuelven `List[Dict]`

### **I** - Interface Segregation
- Cliente HTTP no conoce lógica de servidor
- Servidor no conoce lógica de cliente

### **D** - Dependency Inversion
- `app.py` depende de `plot_utils.py` (abstracción)
- No de implementación específica de matplotlib

---

## 📊 Métricas de Código

### Complejidad
```
src/
  data_parser.py     ~110 LOC   Complejidad: Baja
  plot_utils.py      ~160 LOC   Complejidad: Media
  app.py             ~210 LOC   Complejidad: Media
  send_data.py       ~140 LOC   Complejidad: Baja
```

### Cobertura de Tests
```
data_parser.py     95%+ (crítico)
endpoints          80%+ (importante)
edge cases         70%+ (bueno)
```

---

## 🚀 Evolución Futura

### Posibles Mejoras

1. **Inyección de Dependencias**
   - Usar dependency injection container
   - Facilitar testing con mocks

2. **Repository Pattern**
   - Abstraer acceso a BD
   - `MeasurementRepository` interface

3. **Domain Events**
   - Eventos cuando se reciben datos
   - Observers para procesamiento async

4. **CQRS**
   - Separar comandos (write) de queries (read)
   - Optimizar cada uno independientemente

5. **API Gateway**
   - Capa de API Gateway antes de Flask
   - Rate limiting, autenticación centralizada

---

## 📚 Referencias

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [12 Factor App](https://12factor.net/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

**Última actualización**: 31 de octubre de 2025  
**Versión**: 2.0 (Arquitectura Limpia)
