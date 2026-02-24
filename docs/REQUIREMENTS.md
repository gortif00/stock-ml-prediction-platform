# 📦 Gestión de Dependencias

## Archivos de Requirements

Este proyecto utiliza **varios archivos de requirements** con diferentes propósitos:

### 1️⃣ `requirements.txt` (root) - Dependencias unificadas

```bash
pip install -r requirements.txt
```

**Propósito:** Unifica dependencias del servidor, UI y scheduler con **versiones flexibles**.

**Características:**
- ✅ Versiones mínimas especificadas (ej: `pandas>=2.3.0`)
- ✅ Rangos de compatibilidad (ej: `pandas>=2.3.0,<3.0.0`)
- ✅ Permite actualizaciones de seguridad automáticas
- ✅ Organizado por categorías (Web, Data, ML, etc.)

**Cuándo usar:**
- Desarrollo local
- Instalaciones nuevas
- Actualizaciones controladas

---

### 2️⃣ `requirements-dev.txt` - Testing y herramientas de desarrollo

```bash
pip install -r requirements-dev.txt
```

**Propósito:** Añade dependencias de testing (pytest, coverage, etc.).

---

### 3️⃣ `mcp_server/requirements.txt` - Runtime del API (Docker)

```bash
pip install -r mcp_server/requirements.txt
```

**Propósito:** Dependencias mínimas para el servidor FastAPI/MCP en Docker.

---

### 4️⃣ `mcp_server/requirements-lock.txt` - Versiones Exactas

```bash
pip install -r mcp_server/requirements-lock.txt
```

**Propósito:** Captura las **versiones exactas** de TODOS los packages instalados.

**Características:**
- 🔒 Versiones exactas (ej: `pandas==2.3.3`)
- 🔒 Incluye TODAS las dependencias transitivas (82 packages)
- 🔒 Reproducibilidad 100% garantizada

**Cuándo usar:**
- Despliegues a producción
- Reproducir entorno exacto
- CI/CD pipelines
- Depuración de problemas de versiones

**Generación:**
```bash
# Generar nuevo lock file
pip freeze > mcp_server/requirements-lock.txt
```

---

## 📊 Comparación

| Característica | requirements.txt | mcp_server/requirements-lock.txt |
|----------------|------------------|----------------------------------|
| **Packages** | Unificadas (server + UI + scheduler) | Exactas (incluye deps) |
| **Versiones** | Flexibles (>=) | Exactas (==) |
| **Propósito** | Desarrollo local | Producción |
| **Actualizaciones** | Permitidas | Bloqueadas |
| **Reproducibilidad** | Alta | Absoluta |

---

## 🚀 Flujo de Trabajo Recomendado

### Desarrollo Local

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. Instalar dependencias flexibles
pip install -r requirements.txt

# 2b. (Opcional) Herramientas de testing
pip install -r requirements-dev.txt

# 3. Trabajar en el proyecto...
```

### Antes de Commit

```bash
# Actualizar lock file si cambiaste dependencias del servidor
pip freeze > mcp_server/requirements-lock.txt

# Commit ambos archivos
git add requirements.txt mcp_server/requirements-lock.txt
git commit -m "Update dependencies"
```

### Despliegue a Producción

```bash
# Usar versiones exactas para reproducibilidad
pip install -r mcp_server/requirements-lock.txt
```

---

## 🔄 Actualizar Dependencias

### Actualizar Un Package Específico

```bash
# Actualizar pandas a última versión compatible
pip install --upgrade 'pandas>=2.3.0,<3.0.0'

# Regenerar lock file
pip freeze > mcp_server/requirements-lock.txt
```

### Actualizar Todos los Packages

```bash
# Ver packages desactualizados
pip list --outdated

# Actualizar todos (con cuidado!)
pip install --upgrade -r requirements.txt

# Regenerar lock file
pip freeze > mcp_server/requirements-lock.txt

# Probar que todo funciona
pytest  # o tu comando de tests
```

---

## 📋 Packages Principales

### 🌐 Web Framework
- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI para FastAPI

### 📊 Data Science
- **Pandas**: Manipulación de datos tabulares
- **NumPy**: Operaciones matemáticas y arrays
- **Scikit-learn**: Framework de Machine Learning

### 🤖 Machine Learning
- **XGBoost**: Gradient boosting (alta precisión)
- **LightGBM**: Gradient boosting (rápido)
- **CatBoost**: Gradient boosting (categorías)
- **Prophet**: Time series forecasting (Facebook)

### 📈 Financial Data
- **yfinance**: Datos de Yahoo Finance
- **feedparser**: Parser de RSS feeds

### 🗄️ Database
- **psycopg2-binary**: Driver PostgreSQL
- **SQLAlchemy**: ORM para bases de datos

---

## ⚠️ Problemas Comunes

### Error: "No module named 'X'"

```bash
# Solución: Instalar dependencias
pip install -r requirements.txt
```

### Error: Versiones incompatibles

```bash
# Solución: Usar lock file
pip install -r mcp_server/requirements-lock.txt
```

### Error: "pip: command not found"

```bash
# Solución: Usar python3 -m pip
python3 -m pip install -r requirements.txt
```

---

## 🔧 Comandos Útiles

```bash
# Ver packages instalados
pip list

# Ver info de un package
pip show pandas

# Ver dependencias de un package
pip show pandas | grep Requires

# Buscar packages desactualizados
pip list --outdated

# Verificar compatibilidad
pip check
```

---

## 📝 Notas

- **Siempre** usa entornos virtuales (`venv`)
- **Actualiza** `mcp_server/requirements-lock.txt` después de cambiar dependencias
- **Prueba** tu aplicación después de actualizar packages
- **Documenta** por qué necesitas cada package

---

## 🔗 Referencias

- [pip documentation](https://pip.pypa.io/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Guide](https://packaging.python.org/)
