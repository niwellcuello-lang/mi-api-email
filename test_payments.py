"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                 PRUEBAS DE PAGOS - SISTEMA PROPIETARIO                   ║
║                                                                           ║
║ © 2026 NIWELL CUELLO - TODOS LOS DERECHOS RESERVADOS                    ║
║                                                                           ║
║ LICENCIA COMERCIAL EXCLUSIVA                                             ║
║ Documentación Legal: LICENSE_COMMERCIAL.md                               ║
║                                                                           ║
║ CONTACTO: contacto@niwell.dev                                            ║
║ SITIO WEB: www.niwell-api.com                                            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Pruebas para endpoints de pagos Stripe
Ejecuta esta prueba con: python test_payments.py

VERSIÓN: 1.0.0
AUTOR: Niwell Cuello
"""

import requests
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.local')

BASE_URL = "http://localhost:10000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_clave_publica():
    print_section("TEST 1: Obtener Clave Pública de Stripe")
    
    endpoint = f"{BASE_URL}/api/pagos/clave-publica"
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_crear_intento():
    print_section("TEST 2: Crear Intento de Pago")
    
    endpoint = f"{BASE_URL}/api/pagos/crear-intento"
    payload = {
        "monto": 29.99,
        "moneda": "usd",
        "descripcion": "Acceso Premium API Niwell - Mensual",
        "email_cliente": "cliente@ejemplo.com"
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Guardar payment_intent_id para pruebas posteriores
        if data.get('success') and 'data' in data:
            payment_id = data['data'].get('payment_intent_id')
            if payment_id:
                print(f"\n💾 Payment Intent ID guardado: {payment_id}")
                return payment_id
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_obtener_estado(payment_intent_id):
    print_section("TEST 3: Obtener Estado de Pago")
    
    if not payment_intent_id:
        print("⚠️  Sin ID de pago para prueba (requiere Stripe configurado)")
        return
    
    endpoint = f"{BASE_URL}/api/pagos/estado/{payment_intent_id}"
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_listar_pagos():
    print_section("TEST 4: Listar Pagos Recientes")
    
    endpoint = f"{BASE_URL}/api/pagos/listar?limite=5"
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_validaciones():
    print_section("TEST 5: Validaciones - Monto Inválido")
    
    endpoint = f"{BASE_URL}/api/pagos/crear-intento"
    payload = {
        "monto": -10,
        "moneda": "usd",
        "descripcion": "Prueba de error"
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("(Esto debe fallar con error de validación)")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PRUEBAS DE PAGOS - STRIPE")
    print("="*60)
    print("\n⚠️  Requisitos:")
    print("    1. API debe estar corriendo: python api_unified.py")
    print("    2. Stripe debe estar configurado en .env.local")
    print("    3. En modo TEST (pk_test_*, sk_test_*)\n")
    
    # Verificar si Stripe está configurado
    stripe_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe_key or 'tu_clave' in stripe_key:
        print("⚠️  ADVERTENCIA: Stripe no está configurado correctamente")
        print("    Variables de entorno no cargadas desde .env.local")
        print("    Ver .env.local.example para instrucciones\n")
    
    try:
        # Verificar conexión
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        print("✓ API conectada correctamente\n")
        
        # Ejecutar pruebas
        test_clave_publica()
        payment_id = test_crear_intento()
        test_obtener_estado(payment_id)
        test_listar_pagos()
        test_validaciones()
        
        print("\n" + "="*60)
        print("  ✓ PRUEBAS COMPLETADAS")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar a la API")
        print("   Asegúrate de ejecutar: python api_unified.py\n")
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
