# 🔐 Guía Completa - Sistema de Caja Fuerte (Vault)

## 📋 Tabla de Contenidos
1. [¿Qué es la Caja Fuerte?](#qué-es-la-caja-fuerte)
2. [Características de Seguridad](#características-de-seguridad)
3. [Configuración Inicial](#configuración-inicial)
4. [Guía de Uso Paso a Paso](#guía-de-uso-paso-a-paso)
5. [Endpoints Disponibles](#endpoints-disponibles)
6. [Ejemplos Prácticos](#ejemplos-prácticos)
7. [Troubleshooting](#troubleshooting)

---

## 🔐 ¿Qué es la Caja Fuerte?

La **Caja Fuerte** (Vault) es un sistema encriptado donde **SOLO TÚ** puedes almacenar y recuperar:

- 🔑 Claves API (Stripe, PayPal, etc.)
- 📧 Contraseñas
- 💰 Datos bancarios
- 🎫 Tokens de acceso
- 📱 Números de teléfono
- 🆔 Documentos de identidad (referencias)
- Cualquier información sensible

---

## 🛡️ Características de Seguridad

### ✅ Encriptación AES-256
- Estándar militar de encriptación
- Los datos almacenados están cifrados
- **Ni siquiera los administradores pueden leer tus datos**

### ✅ Autenticación JWT
- Token de 24 horas
- Solo con token válido puedes acceder
- Token expira automáticamente

### ✅ Hash Bcrypt
- Contraseña hasheada con 12 rondas
- Imposible de revertir
- Incluso si la base de datos se filtra, las contraseñas están seguras

### ✅ Auditoría Completa
- Cada acción se registra
- Se puede revisar quién accedió a qué y cuándo
- Previene accesos no autorizados

### ✅ Almacenamiento Seguro
- Base de datos SQLite encriptada
- Archivo `.db` en .gitignore
- No se sincroniza a Git

---

## 🚀 Configuración Inicial

### Paso 1: Generar Clave de Encriptación

```bash
# Accede al endpoint para generar la clave
curl http://localhost:10000/api/vault/generar-clave
```

**Response:**
```json
{
  "success": true,
  "data": {
    "clave": "Fernet_clave_super_larga_y_unica",
    "instruccion": "Guarda este valor en VAULT_CIPHER_KEY de .env.local",
    "advertencia": "NUNCA compartas esta clave. Es única para tu caja fuerte."
  }
}
```

### Paso 2: Agregar a .env.local

Abre `.env.local` y agrega:

```bash
# Caja Fuerte - Encriptación
VAULT_CIPHER_KEY=Fernet_clave_super_larga_y_unica
VAULT_SECRET_KEY=tu-clave-secreta-jwt-aqui
```

### Paso 3: Reiniciar la API

```bash
python api_unified.py
```

---

## 📝 Guía de Uso Paso a Paso

### 1️⃣ Registrarse

**Endpoint:**
```
POST http://localhost:10000/api/vault/registro
```

**Body:**
```json
{
  "email": "niwellcuello@gmail.com",
  "password": "MiContraseña_Segura_123",
  "user_id": "niwell"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "mensaje": "Cuenta creada exitosamente",
    "user_id": "niwell",
    "email": "niwellcuello@gmail.com"
  }
}
```

### 2️⃣ Iniciar Sesión

**Endpoint:**
```
POST http://localhost:10000/api/vault/login
```

**Body:**
```json
{
  "email": "niwellcuello@gmail.com",
  "password": "MiContraseña_Segura_123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_id": "niwell",
    "email": "niwellcuello@gmail.com",
    "expiry_hours": 24
  }
}
```

**Guarda este `token` - lo necesitarás para todos los demás endpoints**

### 3️⃣ Guardar un Secreto

**Endpoint:**
```
POST http://localhost:10000/api/vault/guardar
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Body:**
```json
{
  "nombre": "paypal_api_key",
  "contenido": "sk_live_abc123xyz789...",
  "tipo": "credencial"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "mensaje": "Secreto guardado exitosamente",
    "nombre": "paypal_api_key",
    "tipo": "credencial"
  }
}
```

### 4️⃣ Obtener un Secreto

**Endpoint:**
```
GET http://localhost:10000/api/vault/obtener/paypal_api_key
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "nombre": "paypal_api_key",
    "contenido": "sk_live_abc123xyz789..."
  }
}
```

### 5️⃣ Listar Secretos

**Endpoint:**
```
GET http://localhost:10000/api/vault/listar
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 3,
    "secretos": [
      {
        "nombre": "paypal_api_key",
        "tipo": "credencial",
        "fecha_creacion": "2026-05-29T12:34:56.789",
        "fecha_actualizacion": "2026-05-29T12:34:56.789"
      },
      {
        "nombre": "stripe_secret_key",
        "tipo": "credencial",
        "fecha_creacion": "2026-05-29T12:35:00.000",
        "fecha_actualizacion": "2026-05-29T12:35:00.000"
      },
      {
        "nombre": "cuenta_bancaria_bhd",
        "tipo": "finanzas",
        "fecha_creacion": "2026-05-29T12:36:00.000",
        "fecha_actualizacion": "2026-05-29T12:36:00.000"
      }
    ]
  }
}
```

### 6️⃣ Eliminar un Secreto

**Endpoint:**
```
DELETE http://localhost:10000/api/vault/eliminar/paypal_api_key
```

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "mensaje": "Secreto \"paypal_api_key\" eliminado exitosamente"
  }
}
```

---

## 📡 Endpoints Disponibles

| Método | Endpoint | Autenticación | Descripción |
|--------|----------|---|---|
| POST | `/api/vault/registro` | ❌ | Crear cuenta |
| POST | `/api/vault/login` | ❌ | Iniciar sesión (retorna token) |
| POST | `/api/vault/guardar` | ✅ | Guardar secreto encriptado |
| GET | `/api/vault/obtener/<nombre>` | ✅ | Obtener secreto desencriptado |
| GET | `/api/vault/listar` | ✅ | Listar secretos |
| DELETE | `/api/vault/eliminar/<nombre>` | ✅ | Eliminar secreto |
| GET | `/api/vault/generar-clave` | ❌ | Generar clave de encriptación |

✅ = Requiere Token JWT
❌ = No requiere autenticación

---

## 💡 Ejemplos Prácticos

### Guardar Claves de Stripe

```bash
curl -X POST http://localhost:10000/api/vault/guardar \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "stripe_sk_live",
    "contenido": "sk_live_51234567890abcdefghijk",
    "tipo": "credencial"
  }'
```

### Guardar Número de Cuenta Bancaria

```bash
curl -X POST http://localhost:10000/api/vault/guardar \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "cuenta_bancaria",
    "contenido": "34409930013",
    "tipo": "finanzas"
  }'
```

### Guardar Email Personal

```bash
curl -X POST http://localhost:10000/api/vault/guardar \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "email_personal",
    "contenido": "niwellcuello@gmail.com",
    "tipo": "contacto"
  }'
```

---

## 🐛 Troubleshooting

### ❌ Error: "Token requerido"

**Solución:**
- Asegúrate de incluir el header `Authorization: Bearer TOKEN`
- El token expira en 24 horas, vuelve a hacer login
- Copia el token exactamente (sin espacios extra)

### ❌ Error: "Token expirado o inválido"

**Solución:**
- Ve a `/api/vault/login` para obtener un nuevo token
- Verifica que la clave `VAULT_SECRET_KEY` en `.env.local` es correcta

### ❌ Error: "Secreto no encontrado"

**Solución:**
- Usa `/api/vault/listar` para ver exactamente cómo se llaman
- El nombre es case-sensitive (paypal_key ≠ Paypal_Key)

### ❌ Error: "Caja fuerte no configurada"

**Solución:**
1. Ejecuta: `curl http://localhost:10000/api/vault/generar-clave`
2. Copia el valor de `clave`
3. Agrega a `.env.local`: `VAULT_CIPHER_KEY=...`
4. Reinicia la API: `python api_unified.py`

### ❌ Error: "Email o contraseña incorrectos"

**Solución:**
- Las contraseñas son case-sensitive
- Verifica que el email es correcto
- Si olvidaste la contraseña, crea una nueva cuenta (perderás acceso a secretos anteriores)

### ❌ Error: "La contraseña debe tener mínimo 12 caracteres"

**Solución:**
- Usa contraseñas largas: `MiPassword_123`
- Combina mayúsculas, minúsculas, números y símbolos

---

## 🔒 Mejores Prácticas

### ✅ HACER

- ✓ Usar contraseña única para la Caja Fuerte
- ✓ Guardar el token JWT de forma segura (en memoria)
- ✓ Cambiar `VAULT_CIPHER_KEY` regularmente
- ✓ Revisar auditoría regularmente
- ✓ Usar HTTPS en producción
- ✓ Nombres descriptivos para secretos
- ✓ Guardar cambios de contraseña

### ❌ NUNCA

- ✗ Compartir el token con otros
- ✗ Guardar token en texto plano
- ✗ Usar contraseña simple
- ✗ Guardar `VAULT_CIPHER_KEY` en Git
- ✗ Cambiar `VAULT_CIPHER_KEY` sin backup
- ✗ Compartir secretos por email/Slack
- ✗ Dejar sesión abierta sin vigilancia

---

## 📞 Soporte

- **Documentación**: Este archivo
- **API Health**: `GET /api/health`
- **Contacto**: contacto@niwell.dev

---

**© 2026 Niwell Cuello - Todos los derechos reservados**
