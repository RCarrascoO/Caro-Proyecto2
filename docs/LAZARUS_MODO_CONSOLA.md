# 🖥️ CLIENTE LAZARUS PASCAL - MODO CONSOLA

**Proyecto**: INFO1157 - Sistemas Inteligentes - Proyecto #2  
**Fecha**: 1 de noviembre de 2025

---

## 📋 RESPUESTA A TU PREGUNTA

### **¿Al compilar el Cliente en Lazarus, ahí se generarían las consolas que debo mostrar?**

✅ **SÍ, EXACTAMENTE**

Cuando compilas el programa Lazarus Pascal como **aplicación de consola**, se genera un ejecutable `.exe` que:

1. ✅ Se ejecuta desde **CMD** o **PowerShell**
2. ✅ Muestra salida en **modo consola** (texto)
3. ✅ **NO tiene interfaz gráfica (GUI)**
4. ✅ Cumple el requisito del PDF: "Mode Consola"

---

## 🎯 CÓMO FUNCIONA

### **Servidor Flask (Ya implementado)**

```
╔═══════════════════════════════════════════════════╗
║       HTTP SERVER - MODO CONSOLA                  ║
║       Sistemas Inteligentes - Proyecto #2         ║
╚═══════════════════════════════════════════════════╝

[INFO] Servidor corriendo en http://0.0.0.0:5000
[INFO] Base de datos: data/data.db

[2025-11-01 14:30:15] REQUEST: POST /upload-json from 127.0.0.1
[2025-11-01 14:30:15] SUCCESS: Stored 10 samples for client1
[2025-11-01 14:30:16] REQUEST: POST /upload-stream from 127.0.0.1
[2025-11-01 14:30:16] PARSE: Parsed 100 records
```

### **Cliente Lazarus Pascal (Cuando esté compilado)**

```
╔═══════════════════════════════════════════════════╗
║       HTTP CLIENT - MODO CONSOLA                  ║
║       Cliente Pascal - Proyecto #2                ║
╚═══════════════════════════════════════════════════╝

[INFO] Servidor: http://127.0.0.1:5000
[INFO] Archivo datos: outputs\data.dat
[INFO] Cliente ID: client1

[1/3] Leyendo archivo binario...
  ✓ Archivo leído: 100 registros (2300 bytes)

[2/3] Enviando datos JSON (POST /upload-json)...
  ✓ JSON enviado exitosamente
  ✓ Respuesta: {"status":"ok","records":10}

[3/3] Enviando datos Stream (POST /upload-stream)...
  ✓ Stream enviado: 2300 bytes
  ✓ Respuesta: {"status":"ok","parsed":100}

╔═══════════════════════════════════════════════════╗
║              PROCESO COMPLETADO                   ║
╚═══════════════════════════════════════════════════╝

Tiempo total: 0.8 segundos
```

---

## 🔧 PROCESO DE COMPILACIÓN

### **Paso 1: Instalar Lazarus IDE**

#### **Windows**
```powershell
# Opción 1: Con winget
winget install Lazarus.Lazarus

# Opción 2: Descarga manual
# https://www.lazarus-ide.org/index.php?page=downloads
```

#### **Linux**
```bash
sudo apt install lazarus
```

---

### **Paso 2: Instalar Componentes Indy**

**Desde Lazarus IDE**:
1. Abrir Lazarus
2. Ir a: `Package` → `Install/Uninstall Packages`
3. Buscar: `Indy10` o `IndyLaz`
4. Clic en `Add` → `Rebuild IDE`
5. Reiniciar Lazarus

**O desde Online Package Manager**:
1. `Package` → `Online Package Manager`
2. Buscar: `Indy`
3. Instalar `indylaz`

---

### **Paso 3: Configurar Proyecto como Consola**

**Archivo**: `tools/pas_client_send_data.pas`

**La primera línea es clave**:
```pascal
program pas_client_send_data;
```

Esta declaración indica que es un **programa de consola**, NO una aplicación GUI.

**En Lazarus IDE**:
1. `Project` → `Project Options`
2. `Config and Target` → `Target`
3. Verificar: **LCL Application type** = `Console Application`

---

### **Paso 4: Compilar**

#### **Desde Lazarus IDE**:
```
Run → Build (Ctrl+F9)
```

**Salida**: `tools\pas_client_send_data.exe`

#### **Desde Línea de Comandos**:
```powershell
# FreePascal Compiler
fpc -Mobjfpc -Scgi -O2 -FE.\tools\ pas_client_send_data.pas

# O con lazbuild
lazbuild tools\pas_client_send_data.pas
```

---

### **Paso 5: Ejecutar Cliente Pascal**

```powershell
# Sintaxis
.\tools\pas_client_send_data.exe <server_url> <data_file>

# Ejemplo
.\tools\pas_client_send_data.exe http://127.0.0.1:5000 outputs\data.dat
```

**Salida esperada en consola**:
```
Sending JSON...
JSON POST response:
{"status":"ok","client_id":"client1","records_stored":10}

Sending raw stream...
Stream POST response:
{"status":"ok","client_id":"client1","bytes_received":2300,"records_parsed":100}

Done.
```

---

## 📊 COMPARACIÓN: CLIENTE PYTHON VS CLIENTE LAZARUS

| Característica | Cliente Python | Cliente Lazarus Pascal |
|----------------|----------------|------------------------|
| **Lenguaje** | Python 3.8+ | Lazarus Pascal (FreePascal) |
| **Ejecutable** | Script `.py` | Binario `.exe` nativo |
| **Dependencias** | requests, venv | Indy Components |
| **Modo Consola** | ✅ Sí | ✅ Sí |
| **GUI** | ❌ No | ❌ No |
| **Funcionando** | ✅ SÍ | ⚠️ Pendiente compilar |
| **Requisito PDF** | ❌ No mandatorio | ✅ **MANDATORIO** |

---

## 🎯 LO QUE VERÁS EN CONSOLA

### **Cuando ejecutes el servidor Flask**

```powershell
PS> python src\http_server\app.py
```

**Consola del servidor**:
```
╔═══════════════════════════════════════════════════╗
║       HTTP SERVER - MODO CONSOLA                  ║
║       Sistemas Inteligentes - Proyecto #2         ║
╚═══════════════════════════════════════════════════╝

[2025-11-01 15:00:00] INFO: Servidor corriendo en http://0.0.0.0:5000
[2025-11-01 15:00:00] INFO: Base de datos: data/data.db
[2025-11-01 15:00:00] INFO: Endpoints disponibles:
  • POST /upload-json       - Recibir datos JSON
  • POST /upload-stream     - Recibir datos binarios
  • GET  /plot/<client_id>  - Generar gráfico PNG

 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

---

### **Cuando ejecutes el cliente Lazarus**

```powershell
PS> .\tools\pas_client_send_data.exe http://127.0.0.1:5000 outputs\data.dat
```

**Consola del cliente**:
```
╔═══════════════════════════════════════════════════╗
║       HTTP CLIENT - MODO CONSOLA                  ║
║       Cliente Pascal - Proyecto #2                ║
╚═══════════════════════════════════════════════════╝

Leyendo archivo: outputs\data.dat
  • Tamaño: 2300 bytes
  • Registros: 100

[1/2] Enviando datos JSON...
  URL: http://127.0.0.1:5000/upload-json
  Content-Type: application/json
  ✓ Enviado: 10 registros

[2/2] Enviando datos Stream...
  URL: http://127.0.0.1:5000/upload-stream
  Content-Type: application/octet-stream
  ✓ Enviado: 2300 bytes

Proceso completado exitosamente.
```

---

### **En la consola del servidor verás**

```
[2025-11-01 15:00:15] REQUEST: POST /upload-json from 127.0.0.1
[2025-11-01 15:00:15] SUCCESS: Stored 10 samples for client1
[2025-11-01 15:00:16] REQUEST: POST /upload-stream from 127.0.0.1
[2025-11-01 15:00:16] STREAM: Received 2300 bytes from client1
[2025-11-01 15:00:16] PARSE: Parsed 100 records (id, te, hr, mp01, mp25, mp10, h01, h25, h50, h10)
[2025-11-01 15:00:16] SUCCESS: 100 records stored in database
```

---

## 📝 ESTRUCTURA DEL CÓDIGO PASCAL

### **Componentes Principales**

```pascal
program pas_client_send_data;  // ← Programa de CONSOLA

uses
  Classes, SysUtils, IdHTTP;   // ← Indy HTTP components

type
  TRegistro = packed record    // ← Estructura de 23 bytes
    id: Byte;
    te: Byte;
    hr: Byte;
    mp01: Word;
    mp25: Word;
    mp10: Word;
    h01: Word;
    h25: Word;
    h50: Word;
    h10: Word;
  end;

procedure PostJSON(...);       // ← Enviar JSON
procedure PostStream(...);     // ← Enviar Stream

begin
  // ← CÓDIGO PRINCIPAL
  Writeln('Sending JSON...');  // ← Salida a CONSOLA
  PostJSON(...);
  
  Writeln('Sending stream...'); 
  PostStream(...);
  
  Writeln('Done.');
end.
```

---

## ✅ VERIFICACIÓN DE MODO CONSOLA

### **Checklist para el PDF**

- [x] **Servidor Flask**: Modo consola ✅
  - Sin interfaz gráfica
  - Banner en consola
  - Logs detallados en texto
  
- [ ] **Cliente Lazarus Pascal**: Modo consola ⚠️
  - Sin interfaz gráfica
  - Salida de texto con `Writeln()`
  - Ejecutable desde CMD/PowerShell
  - **Estado**: Código existe, falta compilar

---

## 🎯 REQUISITO DEL PDF (Página 2)

> "El HTTPServer y HTTPCliente se programan en **Mode Consola**. 
> No se aceptan desarrollos de los HTTPServer y Client utilizando **GUI**"

### **¿Qué significa "Mode Consola"?**

✅ **SÍ es Modo Consola**:
- Ejecutable desde terminal (CMD, PowerShell, Bash)
- Salida de texto en la consola
- Sin ventanas gráficas
- Sin botones, formularios, menús visuales

❌ **NO es Modo Consola**:
- Aplicación con ventanas (Windows Forms, VCL, LCL)
- Botones, cuadros de texto visuales
- Interfaz gráfica de usuario (GUI)

---

## 🔧 CÓDIGO ACTUAL vs MEJORADO

### **Código Actual** (Simple)

```pascal
begin
  Writeln('Sending JSON...');
  PostJSON(...);
  Writeln('Sending raw stream...');
  PostStream(...);
  Writeln('Done.');
end.
```

**Salida**:
```
Sending JSON...
JSON POST response:
{"status":"ok"}
Sending raw stream...
Stream POST response:
{"status":"ok"}
Done.
```

---

### **Código Mejorado** (Profesional)

```pascal
procedure PrintBanner;
begin
  Writeln('╔═══════════════════════════════════════════════════╗');
  Writeln('║       HTTP CLIENT - MODO CONSOLA                  ║');
  Writeln('║       Cliente Pascal - Proyecto #2                ║');
  Writeln('╚═══════════════════════════════════════════════════╝');
  Writeln;
end;

begin
  PrintBanner;
  
  Writeln('[INFO] Servidor: ', serverURL);
  Writeln('[INFO] Archivo datos: ', dataFile);
  Writeln;
  
  Writeln('[1/2] Enviando datos JSON...');
  PostJSON(...);
  Writeln('  ✓ JSON enviado exitosamente');
  Writeln;
  
  Writeln('[2/2] Enviando datos Stream...');
  PostStream(...);
  Writeln('  ✓ Stream enviado exitosamente');
  Writeln;
  
  Writeln('╔═══════════════════════════════════════════════════╗');
  Writeln('║              PROCESO COMPLETADO                   ║');
  Writeln('╚═══════════════════════════════════════════════════╝');
end.
```

**Salida mejorada**:
```
╔═══════════════════════════════════════════════════╗
║       HTTP CLIENT - MODO CONSOLA                  ║
║       Cliente Pascal - Proyecto #2                ║
╚═══════════════════════════════════════════════════╝

[INFO] Servidor: http://127.0.0.1:5000
[INFO] Archivo datos: outputs\data.dat

[1/2] Enviando datos JSON...
  ✓ JSON enviado exitosamente

[2/2] Enviando datos Stream...
  ✓ Stream enviado exitosamente

╔═══════════════════════════════════════════════════╗
║              PROCESO COMPLETADO                   ║
╚═══════════════════════════════════════════════════╝
```

---

## 🚀 PASOS PARA COMPLETAR

### **1. Compilar el Cliente Lazarus**

```powershell
# Instalar Lazarus (si no está instalado)
winget install Lazarus.Lazarus

# Abrir en Lazarus IDE
# File → Open → tools\pas_client_send_data.pas

# Compilar
# Run → Build (Ctrl+F9)
```

---

### **2. Probar con Servidor Flask**

**Terminal 1** (Servidor):
```powershell
python src\http_server\app.py
```

**Terminal 2** (Cliente Lazarus):
```powershell
.\tools\pas_client_send_data.exe http://127.0.0.1:5000 outputs\data.dat
```

---

### **3. Verificar Consolas**

✅ **Consola Servidor**: Debe mostrar banner y logs de recepción  
✅ **Consola Cliente**: Debe mostrar progreso del envío  
✅ **Base de Datos**: Datos almacenados correctamente  
✅ **Gráfico PNG**: Generado con 6 subplots  

---

## 🎓 DEMOSTRACIÓN EN DEFENSA

### **Qué mostrar al profesor**

#### **Demostración en Vivo**:

1. **Abrir 2 terminales lado a lado**
   - Terminal izquierda: Servidor Flask
   - Terminal derecha: Cliente Lazarus

2. **Iniciar servidor** (Terminal 1):
   ```powershell
   python src\http_server\app.py
   ```
   → Mostrar banner y logs en consola

3. **Ejecutar cliente** (Terminal 2):
   ```powershell
   .\tools\pas_client_send_data.exe http://127.0.0.1:5000 outputs\data.dat
   ```
   → Mostrar progreso en consola

4. **Mostrar interacción**:
   - Cliente envía → Servidor recibe
   - Logs simultáneos en ambas consolas

5. **Verificar resultados**:
   ```powershell
   # Ver gráfico generado
   Start-Process outputs\plot_client1.png
   
   # Verificar base de datos
   python check_db.py
   ```

---

## 📌 CONCLUSIÓN

### **Respuesta a tu pregunta**

✅ **SÍ**, al compilar el cliente Lazarus Pascal como **aplicación de consola**:

1. ✅ Se genera un `.exe` ejecutable
2. ✅ Se ejecuta desde CMD/PowerShell
3. ✅ Muestra salida en modo texto (consola)
4. ✅ NO tiene interfaz gráfica
5. ✅ Cumple requisito "Mode Consola" del PDF

---

### **Estado Actual**

| Componente | Estado | Modo Consola |
|------------|--------|--------------|
| **Servidor Flask** | ✅ Funcionando | ✅ SÍ (con banner) |
| **Cliente Python** | ✅ Funcionando | ✅ SÍ (sin GUI) |
| **Cliente Lazarus** | ⚠️ Código existe | ⚠️ Falta compilar |

---

### **Próximo Paso**

🔴 **URGENTE**: Compilar `pas_client_send_data.pas` para tener cliente Lazarus funcional

**Tiempo estimado**: 2-4 horas (incluye instalación de Lazarus + Indy)

---

**Última actualización**: 1 de noviembre de 2025
