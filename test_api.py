"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    SUITE DE PRUEBAS - SISTEMA PROPIETARIO                ║
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

Ejemplos de uso de la API Unificada
Ejecuta esta prueba con: python test_api.py

VERSIÓN: 1.0.0
AUTOR: Niwell Cuello
"""

import requests
import json

BASE_URL = "http://localhost:10000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_validar_email():
    print_section("TEST 1: Validar Email")
    
    endpoint = f"{BASE_URL}/api/validar-email"
    payload = {
        "email": "usuario@ejemplo.com"
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_validar_emails_lote():
    print_section("TEST 2: Validar Múltiples Emails")
    
    endpoint = f"{BASE_URL}/api/validar-emails-lote"
    payload = {
        "emails": ["usuario@ejemplo.com", "invalido@", "test@gmail.com", "otro"]
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_sumar():
    print_section("TEST 3: Sumar Números")
    
    endpoint = f"{BASE_URL}/api/excel/sumar"
    payload = {
        "numeros": [10, 20, 30, 40, 50]
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_estadisticas():
    print_section("TEST 4: Estadísticas Completas")
    
    endpoint = f"{BASE_URL}/api/excel/estadisticas"
    payload = {
        "numeros": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_promedio():
    print_section("TEST 5: Calcular Promedio")
    
    endpoint = f"{BASE_URL}/api/excel/promedio"
    payload = {
        "numeros": [5, 10, 15, 20, 25]
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_analizar_texto():
    print_section("TEST 6: Analizar Texto")
    
    endpoint = f"{BASE_URL}/api/texto/analizar"
    payload = {
        "texto": "Hola mundo. Este es un texto de prueba para analizar."
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_health():
    print_section("TEST 7: Health Check")
    
    endpoint = f"{BASE_URL}/api/health"
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_list_endpoints():
    print_section("TEST 8: Listar Endpoints")
    
    endpoint = f"{BASE_URL}/api/endpoints"
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_home():
    print_section("TEST 9: Página Principal")
    
    endpoint = f"{BASE_URL}/"
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PRUEBAS DE API UNIFICADA")
    print("="*60)
    print("\n⚠️  Asegúrate de que la API esté corriendo en puerto 10000")
    print("    Ejecuta: python api_unified.py\n")
    
    try:
        # Verificar conexión
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        print("✓ API conectada correctamente\n")
        
        # Ejecutar pruebas
        test_home()
        test_validar_email()
        test_validar_emails_lote()
        test_sumar()
        test_estadisticas()
        test_promedio()
        test_analizar_texto()
        test_health()
        test_list_endpoints()
        
        print("\n" + "="*60)
        print("  ✓ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar a la API")
        print("   Asegúrate de ejecutar: python api_unified.py\n")
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
