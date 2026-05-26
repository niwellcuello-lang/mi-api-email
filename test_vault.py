"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                 PRUEBAS DE CAJA FUERTE - VAULT SYSTEM                    ║
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

Pruebas para endpoints de Caja Fuerte
Ejecuta esta prueba con: python test_vault.py

VERSIÓN: 1.0.0
AUTOR: Niwell Cuello
"""

import requests
import json
import time

BASE_URL = "http://localhost:10000"
TOKEN = None

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_generar_clave():
    print_section("TEST 1: Generar Clave de Encriptación")
    
    endpoint = f"{BASE_URL}/api/vault/generar-clave"
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
        return data.get('data', {}).get('clave')
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_registro():
    print_section("TEST 2: Registrarse en la Caja Fuerte")
    
    endpoint = f"{BASE_URL}/api/vault/registro"
    payload = {
        "email": "prueba@ejemplo.com",
        "password": "MiPassword_Segura_123",
        "user_id": "usuario_prueba"
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if data.get('success'):
            print("✓ Registro exitoso")
            return True
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_login():
    global TOKEN
    
    print_section("TEST 3: Iniciar Sesión")
    
    endpoint = f"{BASE_URL}/api/vault/login"
    payload = {
        "email": "prueba@ejemplo.com",
        "password": "MiPassword_Segura_123"
    }
    
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if data.get('success'):
            TOKEN = data['data']['token']
            print(f"\n✓ Login exitoso")
            print(f"Token: {TOKEN[:50]}...")
            return True
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_guardar_secretos():
    global TOKEN
    
    if not TOKEN:
        print("⚠️  Sin token disponible")
        return
    
    print_section("TEST 4: Guardar Secretos")
    
    secretos = [
        {
            "nombre": "paypal_key",
            "contenido": "sk_live_abc123xyz789paypal",
            "tipo": "credencial"
        },
        {
            "nombre": "stripe_key",
            "contenido": "sk_live_abc123xyz789stripe",
            "tipo": "credencial"
        },
        {
            "nombre": "cuenta_bancaria",
            "contenido": "34409930013",
            "tipo": "finanzas"
        }
    ]
    
    endpoint = f"{BASE_URL}/api/vault/guardar"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    for secreto in secretos:
        print(f"\n📝 Guardando: {secreto['nombre']}")
        
        try:
            response = requests.post(endpoint, json=secreto, headers=headers)
            print(f"Response ({response.status_code}):")
            data = response.json()
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error: {e}")

def test_listar_secretos():
    global TOKEN
    
    if not TOKEN:
        print("⚠️  Sin token disponible")
        return
    
    print_section("TEST 5: Listar Secretos")
    
    endpoint = f"{BASE_URL}/api/vault/listar"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint, headers=headers)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_obtener_secreto():
    global TOKEN
    
    if not TOKEN:
        print("⚠️  Sin token disponible")
        return
    
    print_section("TEST 6: Obtener Secreto Desencriptado")
    
    endpoint = f"{BASE_URL}/api/vault/obtener/paypal_key"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"GET {endpoint}")
    
    try:
        response = requests.get(endpoint, headers=headers)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if data.get('success'):
            contenido = data['data'].get('contenido')
            print(f"\n✓ Secreto desencriptado: {contenido}")
    except Exception as e:
        print(f"Error: {e}")

def test_obtener_secreto_inexistente():
    global TOKEN
    
    if not TOKEN:
        print("⚠️  Sin token disponible")
        return
    
    print_section("TEST 7: Obtener Secreto Inexistente (Error)")
    
    endpoint = f"{BASE_URL}/api/vault/obtener/secreto_inexistente"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"GET {endpoint}")
    print("(Esto debe fallar con error 404)")
    
    try:
        response = requests.get(endpoint, headers=headers)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_sin_token():
    print_section("TEST 8: Acceso sin Token (Error de Autenticación)")
    
    endpoint = f"{BASE_URL}/api/vault/listar"
    
    print(f"GET {endpoint}")
    print("(Sin header Authorization - debe fallar)")
    
    try:
        response = requests.get(endpoint)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

def test_eliminar_secreto():
    global TOKEN
    
    if not TOKEN:
        print("⚠️  Sin token disponible")
        return
    
    print_section("TEST 9: Eliminar Secreto")
    
    endpoint = f"{BASE_URL}/api/vault/eliminar/cuenta_bancaria"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"DELETE {endpoint}")
    
    try:
        response = requests.delete(endpoint, headers=headers)
        print(f"\nResponse ({response.status_code}):")
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PRUEBAS DE CAJA FUERTE - VAULT SYSTEM")
    print("="*60)
    print("\n⚠️  Requisitos:")
    print("    1. API debe estar corriendo: python api_unified.py")
    print("    2. Clave de encriptación configurada en .env.local")
    print("    3. Database vault.db se creará automáticamente\n")
    
    try:
        # Verificar conexión
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        print("✓ API conectada correctamente\n")
        
        # Ejecutar pruebas
        test_generar_clave()
        time.sleep(1)
        
        if test_registro():
            time.sleep(1)
            if test_login():
                time.sleep(1)
                test_guardar_secretos()
                time.sleep(1)
                test_listar_secretos()
                time.sleep(1)
                test_obtener_secreto()
                time.sleep(1)
                test_obtener_secreto_inexistente()
                time.sleep(1)
                test_sin_token()
                time.sleep(1)
                test_eliminar_secreto()
        
        print("\n" + "="*60)
        print("  ✓ PRUEBAS COMPLETADAS")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar a la API")
        print("   Asegúrate de ejecutar: python api_unified.py\n")
    except Exception as e:
        print(f"❌ ERROR: {e}\n")
