# API Unificada - Consolidación de Scripts

## 📋 Descripción

API Flask consolidada que unifica múltiples funcionalidades en un solo servidor:
- ✅ **Validación de emails** (individual y lotes)
- 🔢 **Cálculos Excel** (suma, promedio, estadísticas)
- 📝 **Análisis de texto** (caracteres, palabras, líneas)

## 🚀 Instalación y Uso

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la API

```bash
python api_unified.py
```

La API estará disponible en: **http://localhost:10000/**

### 3. Ejecutar pruebas

En otra terminal:

```bash
python test_api.py
```

## 📚 Endpoints Disponibles

### 🔐 VALIDACIÓN DE EMAILS

#### `POST /api/validar-email`
Valida un email individual

**Request:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-05-29T01:09:50.340-04:00",
  "data": {
    "email": "usuario@ejemplo.com",
    "valido": true,
    "mensaje": "Email válido"
  }
}
```

---

#### `POST /api/validar-emails-lote`
Valida múltiples emails a la vez

**Request:**
```json
{
  "emails": ["user1@ejemplo.com", "user2@ejemplo.com", "invalido@"]
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-05-29T01:09:50.340-04:00",
  "data": {
    "total": 3,
    "validos": 2,
    "invalidos": 1,
    "resultados": [
      {"email": "user1@ejemplo.com", "valido": true},
      {"email": "user2@ejemplo.com", "valido": true},
      {"email": "invalido@", "valido": false}
    ]
  }
}
```

---

### 🔢 CÁLCULOS EXCEL

#### `POST /api/excel/sumar`
Suma una lista de números

**Request:**
```json
{
  "numeros": [10, 20, 30, 40, 50]
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-05-29T01:09:50.340-04:00",
  "data": {
    "numeros": [10, 20, 30, 40, 50],
    "suma": 150,
    "cantidad": 5
  }
}
```

---

#### `POST /api/excel/promedio`
Calcula el promedio de números

**Request:**
```json
{
  "numeros": [10, 20, 30]
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-05-29T01:09:50.340-04:00",
  "data": {
    "numeros": [10, 20, 30],
    "promedio": 20,
    "cantidad": 3
  }
}
```

---

#### `POST /api/excel/estadisticas`
Calcula estadísticas completas (suma, promedio, máximo, mínimo, desviación estándar)

**Request:**
```json
{
  "numeros": [10, 20, 30, 40, 50]
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-05-29T01:09:50.340-04:00",
  "data": {
    "numeros": [10, 20, 30, 40, 50],
    "cantidad": 5,
    "suma": 150,
    "promedio": 30,
    "maximo": 50,
    "minimo": 10,
    "desviacion_estandar": 14.1421
  }
}
```

---

### 📝 ANÁLISIS DE TEXTO

#### `POST /api/texto/analizar`
Analiza un texto (caracteres, palabras, líneas, etc.)

**Request:**
```json
{
  "texto": "Hola mundo. Este es un texto de prueba."
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-05-29T01:09:50.340-04:00",
  "data": {
    "caracteres": 40,
    "caracteres_sin_espacios": 34,
    "palabras": 7,
    "lineas": 1,
    "promedio_caracteres_por_palabra": 5.71
  }
}
```

---

### ℹ️ INFORMACIÓN

#### `GET /`
Retorna lista de todos los endpoints disponibles

---

#### `GET /api/health`
Verifica que la API esté funcionando

**Response:**
```json
{
  "success": true,
  "timestamp": "2026-05-29T01:09:50.340-04:00",
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  }
}
```

---

#### `GET /api/endpoints`
Lista todos los endpoints registrados

---

## 🛠️ Estructura del Código

```
api_unified.py
├── UTILIDADES Y DECORADORES
│   ├── require_json (validar Content-Type)
│   ├── safe_response (respuestas exitosas)
│   └── error_response (manejo de errores)
├── VALIDADORES
│   ├── Validador.validar_email()
│   ├── Validador.validar_numero()
│   └── Validador.validar_lista_numeros()
├── CALCULADORES
│   ├── Calculador.sumar()
│   ├── Calculador.promedio()
│   ├── Calculador.maximo()
│   ├── Calculador.minimo()
│   └── Calculador.desviacion_estandar()
├── ENDPOINTS (agrupados por categoría)
│   ├── Validación
│   ├── Excel
│   ├── Texto
│   └── Información
└── MANEJO DE ERRORES (404, 405, 500)
```

## 🧪 Ejemplos de Uso con cURL

### Validar email
```bash
curl -X POST http://localhost:10000/api/validar-email \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@ejemplo.com"}'
```

### Sumar números
```bash
curl -X POST http://localhost:10000/api/excel/sumar \
  -H "Content-Type: application/json" \
  -d '{"numeros":[10,20,30]}'
```

### Estadísticas
```bash
curl -X POST http://localhost:10000/api/excel/estadisticas \
  -H "Content-Type: application/json" \
  -d '{"numeros":[10,20,30,40,50]}'
```

### Analizar texto
```bash
curl -X POST http://localhost:10000/api/texto/analizar \
  -H "Content-Type: application/json" \
  -d '{"texto":"Hola mundo"}'
```

## 📦 Requisitos

- Python 3.7+
- Flask 3.1.3
- Flask-CORS 6.0.2
- Gunicorn 26.0.0
- Requests 2.34.2

## 🚢 Deploy en Render/Heroku

### Procfile (ya existe)
```
web: gunicorn api_unified:app
```

### Actualizar requirements.txt
```
pip freeze > requirements.txt
```

### Deploy
```bash
git add .
git commit -m "API consolidada"
git push heroku main  # o tu rama
```

## 📝 Características

✅ Validación completa de inputs
✅ Manejo robusto de errores
✅ Respuestas con timestamps
✅ CORS habilitado para requests desde otros orígenes
✅ Documentación integrada en endpoints
✅ Suite de pruebas completa
✅ Código modular y reutilizable

## 🔄 Consolidación de Scripts

Este archivo consolida:
1. `api.py` - API de validación de emails y cálculos
2. Funcionalidades adicionales para análisis de texto
3. Decoradores y utilitarios mejorados
4. Manejo completo de errores

## 📧 Soporte

Para reportar problemas o sugerencias, usa los endpoints `/api/health` para verificar el estado.

---

**Versión:** 1.0.0
**Última actualización:** 2026-05-29
