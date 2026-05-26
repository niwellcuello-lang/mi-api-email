# 💳 Guía de Configuración - Pagos con Stripe

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Crear Cuenta en Stripe](#crear-cuenta-en-stripe)
3. [Obtener Claves API](#obtener-claves-api)
4. [Configurar Variables de Entorno](#configurar-variables-de-entorno)
5. [Probar Endpoints](#probar-endpoints)
6. [Seguridad](#seguridad)
7. [Troubleshooting](#troubleshooting)

---

## ✅ Requisitos Previos

- ✓ Python 3.8+
- ✓ Cuenta de email válida
- ✓ Documento de identidad (para verificación bancaria)

---

## 🔧 Crear Cuenta en Stripe

### Paso 1: Ir a Stripe.com
```
Visita: https://dashboard.stripe.com/register
```

### Paso 2: Completar Registro
- Email: Tu email comercial
- Contraseña: Contraseña segura (mín. 12 caracteres)
- Empresa: Niwell (o tu nombre)
- País: Baréin (o tu país)

### Paso 3: Verificar Email
Stripe enviará un correo de confirmación. Verifica tu email.

### Paso 4: Información de Cuenta
Complete:
- Nombre personal
- Número de teléfono
- Dirección
- Tipo de negocio: SaaS / API Services

---

## 🔑 Obtener Claves API

### Acceder al Dashboard
```
https://dashboard.stripe.com/apikeys
```

### Encontrar las Claves

Verás dos modos:

#### Modo TEST (Desarrollo - Seguro)
```
Publishable Key:  pk_test_51234567890abcdefghijk
Secret Key:       sk_test_51234567890abcdefghijk
```

#### Modo LIVE (Producción - Solo cuando esté listo)
```
Publishable Key:  pk_live_51234567890abcdefghijk
Secret Key:       sk_live_51234567890abcdefghijk
```

⚠️ **Usa SIEMPRE modo TEST para desarrollo**

---

## 🔐 Configurar Variables de Entorno

### Paso 1: Copiar Archivo de Ejemplo
```bash
cp .env.local.example .env.local
```

### Paso 2: Editar .env.local
```bash
# Abrir con tu editor favorito
nano .env.local
# o
code .env.local
```

### Paso 3: Reemplazar las Claves

**ANTES:**
```
STRIPE_PUBLISHABLE_KEY=pk_test_tu_clave_publica_aqui
STRIPE_SECRET_KEY=sk_test_tu_clave_privada_aqui
```

**DESPUÉS:**
```
STRIPE_PUBLISHABLE_KEY=pk_test_51234567890abcdefghijk
STRIPE_SECRET_KEY=sk_test_51234567890abcdefghijk
```

### Paso 4: Guardar y Cerrar

✓ El archivo `.env.local` está en `.gitignore` - NO será commiteado

---

## 🧪 Probar Endpoints

### Requisito: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 1: Iniciar la API
```bash
python api_unified.py
```

La API correrá en: `http://localhost:10000`

### Paso 2: Abrir otra Terminal y Ejecutar Pruebas
```bash
python test_payments.py
```

---

## 📊 Endpoints Disponibles

### 1️⃣ Obtener Clave Pública
```bash
GET http://localhost:10000/api/pagos/clave-publica
```

**Response:**
```json
{
  "success": true,
  "data": {
    "publishable_key": "pk_test_..."
  }
}
```

### 2️⃣ Crear Intento de Pago
```bash
POST http://localhost:10000/api/pagos/crear-intento
```

**Body:**
```json
{
  "monto": 29.99,
  "moneda": "usd",
  "descripcion": "Acceso Premium",
  "email_cliente": "cliente@ejemplo.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "client_secret": "pi_test_..._secret_...",
    "payment_intent_id": "pi_test_...",
    "monto": 29.99,
    "moneda": "USD",
    "estado": "requires_payment_method"
  }
}
```

### 3️⃣ Obtener Estado de Pago
```bash
GET http://localhost:10000/api/pagos/estado/pi_test_...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "payment_intent_id": "pi_test_...",
    "estado": "succeeded",
    "monto": 29.99,
    "moneda": "USD"
  }
}
```

### 4️⃣ Listar Pagos
```bash
GET http://localhost:10000/api/pagos/listar?limite=10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 5,
    "pagos": [
      {
        "id": "pi_test_...",
        "monto": 29.99,
        "moneda": "USD",
        "estado": "succeeded",
        "fecha": "2026-05-29T12:34:56.789012"
      }
    ]
  }
}
```

---

## 🔐 Seguridad

### ✅ HACER

- ✓ Usar **SIEMPRE** modo TEST (pk_test_) en desarrollo
- ✓ Guardar `.env.local` en `.gitignore`
- ✓ Rotar claves regularmente
- ✓ Usar HTTPS en producción
- ✓ Validar montos en servidor
- ✓ Loguear intentos de pago fallidos
- ✓ Verificar emails de clientes

### ❌ NUNCA

- ✗ Commitear `.env.local` a Git
- ✗ Compartir claves por email/Slack
- ✗ Usar `pk_live` en desarrollo
- ✗ Loguear `sk_live` completas
- ✗ Guardar números de tarjeta
- ✗ Pasar secrets como query parameters
- ✗ Exponerlas en el frontend (salvo pk_test)

---

## 🧪 Pruebas Stripe

Stripe proporciona números de tarjeta de prueba:

### Tarjeta de Prueba Exitosa
```
Número: 4242 4242 4242 4242
Vencimiento: 12/25
CVC: 123
```

### Tarjeta Rechazada
```
Número: 4000 0000 0000 0002
Vencimiento: 12/25
CVC: 123
```

### Tarjeta Requiere Autenticación
```
Número: 4000 0025 0000 3155
Vencimiento: 12/25
CVC: 123
```

---

## 🐛 Troubleshooting

### Error: "No module named 'stripe'"

**Solución:**
```bash
pip install stripe==15.2.0
```

### Error: "Stripe no configurado correctamente"

**Solución:**
1. Verifica que `.env.local` existe en la carpeta del proyecto
2. Verifica que tiene las claves:
   ```bash
   cat .env.local
   ```
3. Reinicia el servidor

### Error: "Invalid API Key"

**Solución:**
- Verifica que copiaste la clave correctamente
- Verifica que está usando `sk_test_` (no `pk_test_`)
- Genera nuevas claves en el dashboard

### Error: "CORS blocked the request"

**Solución:**
- CORS está configurado automáticamente
- Si persiste, verifica que la API está corriendo
- Comprueba el puerto: `http://localhost:10000`

### Error: "Monto debe ser mayor a 0"

**Solución:**
- El monto debe ser un número positivo
- Ejemplo válido: `{"monto": 25.50}`

---

## 📈 Próximos Pasos

### Implementar en Frontend
```javascript
// Obtener clave pública
const response = await fetch('/api/pagos/clave-publica');
const data = await response.json();
const stripeKey = data.data.publishable_key;

// Crear intent
const intentResponse = await fetch('/api/pagos/crear-intento', {
  method: 'POST',
  body: JSON.stringify({
    monto: 29.99,
    moneda: 'usd',
    email_cliente: 'cliente@ejemplo.com'
  })
});

const intent = await intentResponse.json();
// Usar client_secret para confirmación...
```

### Pasar a Producción
1. Cambiar `pk_test_` y `sk_test_` por `pk_live_` y `sk_live_`
2. Implementar HTTPS obligatorio
3. Agregar webhooks para eventos
4. Implementar logging de auditoría
5. Certificación PCI DSS (Stripe maneja esto)

---

## 📞 Soporte

- **Documentación Stripe**: https://stripe.com/docs
- **API Reference**: https://stripe.com/docs/api
- **Dashboard**: https://dashboard.stripe.com
- **Contacto**: contacto@niwell.dev

---

**© 2026 Niwell Cuello - Todos los derechos reservados**
