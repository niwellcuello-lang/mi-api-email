"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     API UNIFICADA - SISTEMA PROPIETARIO                  ║
║                                                                           ║
║ © 2026 NIWELL CUELLO - TODOS LOS DERECHOS RESERVADOS                    ║
║                                                                           ║
║ LICENCIA COMERCIAL EXCLUSIVA                                             ║
║ Documentación Legal: LICENSE_COMMERCIAL.md                               ║
║ Patentes Pendientes: INTELLECTUAL_PROPERTY.md                            ║
║ Modelo de Monetización: MONETIZATION_PLAN.md                             ║
║                                                                           ║
║ PROHIBIDO:                                                                ║
║ • Copiar sin autorización                                                 ║
║ • Crear versiones derivadas                                               ║
║ • Usar comercialmente sin licencia                                        ║
║ • Sublicenciar                                                            ║
║                                                                           ║
║ CONTACTO COMERCIAL: contacto@niwell.dev                                  ║
║ SITIO WEB: www.niwell-api.com                                            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

API Unificada - Consolida funcionalidades de validación, cálculos y análisis
Endpoints: validación de emails, cálculos Excel, análisis de texto

VERSIÓN: 1.0.0
AUTOR: Niwell Cuello
FECHA CREACIÓN: 2026-05-29
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import os
from datetime import datetime
from functools import wraps
from payment_handler import PaymentHandler
from vault_handler import (
    VaultDatabase, AuthHandler, Encryptor, requerir_autenticacion
)
from academy_handler import (
    AcademyDatabase, Cursos, PlanesSubscripcion, EmailHandler, ReporteGenerator
)

app = Flask(__name__)
CORS(app)

# Inicializar caja fuerte
VaultDatabase.inicializar()

# Inicializar Academia
AcademyDatabase.inicializar()

# ============================================================================
# UTILIDADES Y DECORADORES
# ============================================================================

def require_json(f):
    """Decorador para validar que el request contiene JSON válido"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return decorated_function

def safe_response(data, status=200):
    """Envuelve respuestas con metadata"""
    return jsonify({
        'success': True,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }), status

def error_response(message, status=400):
    """Envuelve errores con metadata"""
    return jsonify({
        'success': False,
        'timestamp': datetime.utcnow().isoformat(),
        'error': message
    }), status

# ============================================================================
# VALIDADORES
# ============================================================================

class Validador:
    """Clase con métodos de validación reutilizables"""
    
    @staticmethod
    def validar_email(email):
        """Valida formato de email"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email))
    
    @staticmethod
    def validar_numero(valor):
        """Valida si es un número válido"""
        try:
            float(valor)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_lista_numeros(numeros):
        """Valida que sea lista de números"""
        if not isinstance(numeros, list):
            return False
        return all(Validador.validar_numero(n) for n in numeros)

# ============================================================================
# CALCULADORES
# ============================================================================

class Calculador:
    """Clase con funciones matemáticas para Excel"""
    
    @staticmethod
    def sumar(numeros):
        """Suma una lista de números"""
        if not numeros:
            return 0
        return sum(float(n) for n in numeros)
    
    @staticmethod
    def promedio(numeros):
        """Calcula el promedio"""
        if not numeros:
            return 0
        return Calculador.sumar(numeros) / len(numeros)
    
    @staticmethod
    def maximo(numeros):
        """Encuentra el número máximo"""
        if not numeros:
            return None
        return max(float(n) for n in numeros)
    
    @staticmethod
    def minimo(numeros):
        """Encuentra el número mínimo"""
        if not numeros:
            return None
        return min(float(n) for n in numeros)
    
    @staticmethod
    def desviacion_estandar(numeros):
        """Calcula desviación estándar"""
        if len(numeros) < 2:
            return 0
        media = Calculador.promedio(numeros)
        varianza = sum((float(n) - media) ** 2 for n in numeros) / len(numeros)
        return varianza ** 0.5

# ============================================================================
# ENDPOINTS: VALIDACIÓN
# ============================================================================

@app.route('/api/validar-email', methods=['POST'])
@require_json
def validar_email():
    """Valida formato de email
    
    Body: {"email": "usuario@ejemplo.com"}
    """
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return error_response('El campo "email" es requerido')
    
    valido = Validador.validar_email(email)
    
    return safe_response({
        'email': email,
        'valido': valido,
        'mensaje': 'Email válido' if valido else 'Email inválido'
    })

@app.route('/api/validar-emails-lote', methods=['POST'])
@require_json
def validar_emails_lote():
    """Valida múltiples emails
    
    Body: {"emails": ["email1@ejemplo.com", "email2@ejemplo.com"]}
    """
    data = request.get_json()
    emails = data.get('emails', [])
    
    if not isinstance(emails, list):
        return error_response('El campo "emails" debe ser una lista')
    
    resultados = []
    for email in emails:
        email = email.strip()
        valido = Validador.validar_email(email)
        resultados.append({
            'email': email,
            'valido': valido
        })
    
    return safe_response({
        'total': len(resultados),
        'validos': sum(1 for r in resultados if r['valido']),
        'invalidos': sum(1 for r in resultados if not r['valido']),
        'resultados': resultados
    })

# ============================================================================
# ENDPOINTS: CÁLCULOS EXCEL
# ============================================================================

@app.route('/api/excel/sumar', methods=['POST'])
@require_json
def excel_sumar():
    """Suma una lista de números
    
    Body: {"numeros": [10, 20, 30]}
    """
    data = request.get_json()
    numeros = data.get('numeros', [])
    
    if not Validador.validar_lista_numeros(numeros):
        return error_response('El campo "numeros" debe ser una lista de números válidos')
    
    suma = Calculador.sumar(numeros)
    
    return safe_response({
        'numeros': numeros,
        'suma': suma,
        'cantidad': len(numeros)
    })

@app.route('/api/excel/estadisticas', methods=['POST'])
@require_json
def excel_estadisticas():
    """Calcula estadísticas completas de números
    
    Body: {"numeros": [10, 20, 30, 40, 50]}
    """
    data = request.get_json()
    numeros = data.get('numeros', [])
    
    if not Validador.validar_lista_numeros(numeros):
        return error_response('El campo "numeros" debe ser una lista de números válidos')
    
    if not numeros:
        return error_response('La lista de números no puede estar vacía')
    
    nums_float = [float(n) for n in numeros]
    
    return safe_response({
        'numeros': numeros,
        'cantidad': len(numeros),
        'suma': Calculador.sumar(nums_float),
        'promedio': Calculador.promedio(nums_float),
        'maximo': Calculador.maximo(nums_float),
        'minimo': Calculador.minimo(nums_float),
        'desviacion_estandar': round(Calculador.desviacion_estandar(nums_float), 4)
    })

@app.route('/api/excel/promedio', methods=['POST'])
@require_json
def excel_promedio():
    """Calcula el promedio
    
    Body: {"numeros": [10, 20, 30]}
    """
    data = request.get_json()
    numeros = data.get('numeros', [])
    
    if not Validador.validar_lista_numeros(numeros):
        return error_response('El campo "numeros" debe ser una lista de números válidos')
    
    if not numeros:
        return error_response('La lista de números no puede estar vacía')
    
    promedio = Calculador.promedio(numeros)
    
    return safe_response({
        'numeros': numeros,
        'promedio': promedio,
        'cantidad': len(numeros)
    })

# ============================================================================
# ENDPOINTS: ANÁLISIS DE TEXTO
# ============================================================================

@app.route('/api/texto/analizar', methods=['POST'])
@require_json
def texto_analizar():
    """Analiza un texto (caracteres, palabras, líneas)
    
    Body: {"texto": "Hola mundo"}
    """
    data = request.get_json()
    texto = data.get('texto', '')
    
    if not texto:
        return error_response('El campo "texto" es requerido')
    
    lineas = texto.split('\n')
    palabras = texto.split()
    caracteres = len(texto)
    caracteres_sin_espacios = len(texto.replace(' ', ''))
    
    return safe_response({
        'caracteres': caracteres,
        'caracteres_sin_espacios': caracteres_sin_espacios,
        'palabras': len(palabras),
        'lineas': len(lineas),
        'promedio_caracteres_por_palabra': round(caracteres / len(palabras), 2) if palabras else 0
    })

# ============================================================================
# ENDPOINTS: PAGOS (STRIPE)
# ============================================================================

@app.route('/api/pagos/crear-intento', methods=['POST'])
@require_json
def crear_intento_pago():
    """Crea un intento de pago con Stripe
    
    Body: {
        "monto": 50.00,
        "moneda": "usd",
        "descripcion": "Acceso a API Premium",
        "email_cliente": "cliente@ejemplo.com"
    }
    """
    data = request.get_json()
    monto = data.get('monto')
    moneda = data.get('moneda', 'usd').lower()
    descripcion = data.get('descripcion', 'Pago API Niwell')
    email_cliente = data.get('email_cliente', '')
    
    # Validar campos
    if not monto:
        return error_response('El campo "monto" es requerido')
    
    if not isinstance(monto, (int, float)) or monto <= 0:
        return error_response('El monto debe ser un número positivo')
    
    # Crear intento de pago
    resultado = PaymentHandler.crear_intento_pago(
        monto=monto,
        moneda=moneda,
        descripcion=descripcion,
        email_cliente=email_cliente
    )
    
    if resultado['success']:
        return safe_response(resultado, 201)
    else:
        return error_response(resultado['error'], 400)

@app.route('/api/pagos/estado/<payment_intent_id>', methods=['GET'])
def obtener_estado_pago(payment_intent_id):
    """Obtiene el estado de un intento de pago
    
    Parámetro: payment_intent_id (URL)
    """
    if not payment_intent_id:
        return error_response('El ID de pago es requerido')
    
    resultado = PaymentHandler.obtener_estado_pago(payment_intent_id)
    
    if resultado['success']:
        return safe_response(resultado)
    else:
        return error_response(resultado['error'], 404)

@app.route('/api/pagos/listar', methods=['GET'])
def listar_pagos():
    """Lista los últimos pagos procesados
    
    Query params: ?limite=10
    """
    limite = request.args.get('limite', 10, type=int)
    
    if limite < 1 or limite > 100:
        return error_response('El límite debe estar entre 1 y 100')
    
    resultado = PaymentHandler.listar_pagos(limite=limite)
    
    if resultado['success']:
        return safe_response(resultado)
    else:
        return error_response(resultado['error'], 400)

@app.route('/api/pagos/clave-publica', methods=['GET'])
def obtener_clave_publica():
    """Obtiene la clave pública de Stripe
    
    (Usada por clientes frontend para crear elementos de pago)
    """
    resultado = PaymentHandler.obtener_clave_publica()
    
    if resultado['success']:
        return safe_response(resultado)
    else:
        return error_response(resultado['error'], 400)

# ============================================================================
# ENDPOINTS: CAJA FUERTE (VAULT)
# ============================================================================

@app.route('/api/vault/registro', methods=['POST'])
@require_json
def vault_registro():
    """Crea una cuenta en la Caja Fuerte
    
    Body: {
        "email": "usuario@ejemplo.com",
        "password": "contraseña-segura",
        "user_id": "niwell"
    }
    """
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    user_id = data.get('user_id', '').strip()
    
    # Validaciones
    if not email or not password or not user_id:
        return error_response('Email, contraseña y user_id son requeridos')
    
    if len(password) < 12:
        return error_response('La contraseña debe tener mínimo 12 caracteres')
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return error_response('Email inválido')
    
    # Crear usuario
    if VaultDatabase.crear_usuario(user_id, email, password):
        VaultDatabase.registrar_auditoria(user_id, "REGISTRO", f"Cuenta creada para {email}")
        
        return safe_response({
            'mensaje': 'Cuenta creada exitosamente',
            'user_id': user_id,
            'email': email
        }, 201)
    else:
        return error_response('El usuario o email ya existe', 409)

@app.route('/api/vault/login', methods=['POST'])
@require_json
def vault_login():
    """Inicia sesión en la Caja Fuerte
    
    Body: {
        "email": "usuario@ejemplo.com",
        "password": "contraseña-segura"
    }
    
    Retorna: Token JWT para autenticación
    """
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return error_response('Email y contraseña requeridos')
    
    usuario = VaultDatabase.obtener_usuario(email)
    
    if not usuario or not AuthHandler.verificar_password(password, usuario['password_hash']):
        return error_response('Email o contraseña incorrectos', 401)
    
    # Crear token
    token = AuthHandler.crear_token_jwt(usuario['id'])
    VaultDatabase.registrar_auditoria(usuario['id'], "LOGIN", "Login exitoso")
    
    return safe_response({
        'token': token,
        'user_id': usuario['id'],
        'email': usuario['email'],
        'expiry_hours': 24
    })

@app.route('/api/vault/guardar', methods=['POST'])
@require_json
@requerir_autenticacion
def vault_guardar():
    """Guarda un secreto encriptado en la caja fuerte
    
    Headers: Authorization: Bearer <token>
    
    Body: {
        "nombre": "paypal_key",
        "contenido": "datos-sensibles-aqui",
        "tipo": "credencial"
    }
    """
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    contenido = data.get('contenido', '').strip()
    tipo = data.get('tipo', 'general').strip()
    
    if not nombre or not contenido:
        return error_response('Nombre y contenido son requeridos')
    
    if len(nombre) > 100:
        return error_response('El nombre no puede superar 100 caracteres')
    
    try:
        # Generar clave de encriptación si no existe
        cipher_key = os.getenv("VAULT_CIPHER_KEY")
        if not cipher_key:
            cipher_key = Encryptor.generar_clave()
        
        # Encriptar
        datos_encriptados = Encryptor.encriptar(contenido, cipher_key)
        
        # Guardar
        if VaultDatabase.guardar_secreto(request.user_id, nombre, datos_encriptados, tipo):
            VaultDatabase.registrar_auditoria(request.user_id, "GUARDAR_SECRETO", f"Secreto guardado: {nombre}")
            
            return safe_response({
                'mensaje': 'Secreto guardado exitosamente',
                'nombre': nombre,
                'tipo': tipo
            }, 201)
        else:
            return error_response('Error al guardar secreto', 500)
    
    except Exception as e:
        return error_response(f'Error: {str(e)}', 500)

@app.route('/api/vault/obtener/<nombre>', methods=['GET'])
@requerir_autenticacion
def vault_obtener(nombre):
    """Obtiene un secreto desencriptado de la caja fuerte
    
    Headers: Authorization: Bearer <token>
    
    URL: /api/vault/obtener/paypal_key
    """
    nombre = nombre.strip()
    
    if not nombre:
        return error_response('Nombre de secreto requerido')
    
    try:
        datos_encriptados = VaultDatabase.obtener_secreto(request.user_id, nombre)
        
        if not datos_encriptados:
            return error_response('Secreto no encontrado', 404)
        
        # Desencriptar
        cipher_key = os.getenv("VAULT_CIPHER_KEY")
        if not cipher_key:
            return error_response('Caja fuerte no configurada', 500)
        
        contenido = Encryptor.desencriptar(datos_encriptados, cipher_key)
        VaultDatabase.registrar_auditoria(request.user_id, "LEER_SECRETO", f"Secreto leído: {nombre}")
        
        return safe_response({
            'nombre': nombre,
            'contenido': contenido
        })
    
    except Exception as e:
        return error_response(f'Error: {str(e)}', 500)

@app.route('/api/vault/listar', methods=['GET'])
@requerir_autenticacion
def vault_listar():
    """Lista todos los secretos del usuario (sin datos)
    
    Headers: Authorization: Bearer <token>
    """
    try:
        secretos = VaultDatabase.listar_secretos(request.user_id)
        VaultDatabase.registrar_auditoria(request.user_id, "LISTAR_SECRETOS", f"Total: {len(secretos)}")
        
        return safe_response({
            'total': len(secretos),
            'secretos': secretos
        })
    
    except Exception as e:
        return error_response(f'Error: {str(e)}', 500)

@app.route('/api/vault/eliminar/<nombre>', methods=['DELETE'])
@requerir_autenticacion
def vault_eliminar(nombre):
    """Elimina un secreto de la caja fuerte
    
    Headers: Authorization: Bearer <token>
    
    URL: /api/vault/eliminar/paypal_key
    """
    nombre = nombre.strip()
    
    if not nombre:
        return error_response('Nombre de secreto requerido')
    
    try:
        # Verificar que existe
        if not VaultDatabase.obtener_secreto(request.user_id, nombre):
            return error_response('Secreto no encontrado', 404)
        
        if VaultDatabase.eliminar_secreto(request.user_id, nombre):
            VaultDatabase.registrar_auditoria(request.user_id, "ELIMINAR_SECRETO", f"Secreto eliminado: {nombre}")
            
            return safe_response({
                'mensaje': f'Secreto "{nombre}" eliminado exitosamente'
            })
        else:
            return error_response('Error al eliminar secreto', 500)
    
    except Exception as e:
        return error_response(f'Error: {str(e)}', 500)

@app.route('/api/vault/generar-clave', methods=['GET'])
def vault_generar_clave():
    """Genera una clave de encriptación válida
    
    (Usa esta clave como VAULT_CIPHER_KEY en .env)
    """
    try:
        clave = Encryptor.generar_clave()
        
        return safe_response({
            'clave': clave,
            'instruccion': 'Guarda este valor en VAULT_CIPHER_KEY de .env.local',
            'advertencia': 'NUNCA compartas esta clave. Es única para tu caja fuerte.'
        })
    
    except Exception as e:
        return error_response(f'Error: {str(e)}', 500)

# ============================================================================
# ENDPOINTS: ACADEMIA EDUCATIVA
# ============================================================================

@app.route('/api/academy/planes', methods=['GET'])
def academy_listar_planes():
    """Lista todos los planes de suscripción disponibles"""
    planes = PlanesSubscripcion.listar_planes()
    
    return safe_response({
        'total': len(planes),
        'planes': planes
    })

@app.route('/api/academy/cursos', methods=['GET'])
def academy_listar_cursos():
    """Lista todos los cursos disponibles"""
    cursos = Cursos.listar_cursos()
    
    return safe_response({
        'total': len(cursos),
        'cursos': cursos
    })

@app.route('/api/academy/mi-plan', methods=['GET'])
@require_json
@requerir_autenticacion
def academy_mi_plan():
    """Obtiene el plan del usuario autenticado
    
    Headers: Authorization: Bearer <token>
    """
    plan_id = AcademyDatabase.obtener_plan_usuario(request.user_id)
    plan_info = PlanesSubscripcion.obtener_plan(plan_id)
    
    return safe_response({
        'plan_id': plan_id,
        'plan': plan_info
    })

@app.route('/api/academy/upgrade', methods=['POST'])
@require_json
@requerir_autenticacion
def academy_upgrade_plan():
    """Mejora el plan del usuario (requiere pago con Stripe)
    
    Headers: Authorization: Bearer <token>
    
    Body: {
        "nuevo_plan": "profesional"
    }
    """
    data = request.get_json()
    nuevo_plan = data.get('nuevo_plan', '').strip()
    
    # Validar que plan existe
    if not PlanesSubscripcion.obtener_plan(nuevo_plan):
        return error_response('Plan no válido')
    
    # Crear intento de pago
    plan_info = PlanesSubscripcion.obtener_plan(nuevo_plan)
    
    if plan_info['precio'] == 0:
        # Plan gratuito - sin pago
        if AcademyDatabase.actualizar_plan(request.user_id, nuevo_plan):
            return safe_response({
                'mensaje': f'Plan actualizado a {plan_info["nombre"]}',
                'plan': plan_info
            })
    else:
        # Requiere pago - crear intento
        resultado = PaymentHandler.crear_intento_pago(
            monto=plan_info['precio'],
            moneda='usd',
            descripcion=f"Plan {plan_info['nombre']} - Academia",
            email_cliente=""
        )
        
        if resultado['success']:
            return safe_response({
                'mensaje': 'Intento de pago creado. Completa el pago para activar.',
                'client_secret': resultado['client_secret'],
                'payment_intent_id': resultado['payment_intent_id'],
                'plan': plan_info
            })
    
    return error_response('Error al procesar plan')

@app.route('/api/academy/progreso', methods=['GET'])
@requerir_autenticacion
def academy_mi_progreso():
    """Obtiene el progreso del usuario en todos los cursos
    
    Headers: Authorization: Bearer <token>
    """
    progreso = AcademyDatabase.obtener_progreso(request.user_id)
    
    return safe_response({
        'total_cursos': len(progreso),
        'progreso': progreso
    })

@app.route('/api/academy/registrar-progreso', methods=['POST'])
@require_json
@requerir_autenticacion
def academy_registrar_progreso():
    """Registra progreso en un curso
    
    Headers: Authorization: Bearer <token>
    
    Body: {
        "curso_id": "api-basics",
        "lecciones_completadas": 3
    }
    """
    data = request.get_json()
    curso_id = data.get('curso_id', '').strip()
    lecciones = data.get('lecciones_completadas', 0)
    
    if not curso_id or not Cursos.obtener_curso(curso_id):
        return error_response('Curso no válido')
    
    if lecciones < 0:
        return error_response('Lecciones no puede ser negativo')
    
    if AcademyDatabase.registrar_progreso(request.user_id, curso_id, lecciones):
        return safe_response({
            'mensaje': 'Progreso registrado',
            'curso_id': curso_id,
            'lecciones_completadas': lecciones
        })
    
    return error_response('Error al registrar progreso', 500)

@app.route('/api/academy/exportar-reporte', methods=['POST'])
@require_json
@requerir_autenticacion
def academy_exportar_reporte():
    """Genera y envía reporte personal al email
    
    Headers: Authorization: Bearer <token>
    
    Body: {
        "email": "usuario@ejemplo.com",
        "tipo": "personal"
    }
    """
    data = request.get_json()
    email = data.get('email', '').strip()
    tipo_reporte = data.get('tipo', 'personal').strip()
    
    if not email or '@' not in email:
        return error_response('Email inválido')
    
    if tipo_reporte not in ['personal', 'monetizacion']:
        return error_response('Tipo de reporte no válido')
    
    try:
        # Generar reporte
        if tipo_reporte == 'personal':
            contenido = ReporteGenerator.generar_reporte_personal(request.user_id, email)
            asunto = "📊 Tu Reporte Personal - Niwell Academy"
        else:
            contenido = ReporteGenerator.generar_reporte_monetizacion(request.user_id)
            asunto = "💰 Tu Reporte de Monetización - Niwell Academy"
        
        # Guardar en BD
        report_id = AcademyDatabase.guardar_reporte(
            request.user_id,
            tipo_reporte,
            contenido
        )
        
        # Enviar por email
        nombre_archivo = f"reporte_{tipo_reporte}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        enviado = EmailHandler.enviar_documento(
            email,
            asunto,
            contenido,
            contenido,
            nombre_archivo
        )
        
        return safe_response({
            'mensaje': 'Reporte generado exitosamente',
            'report_id': report_id,
            'email': email,
            'tipo': tipo_reporte,
            'enviado': enviado,
            'nota': 'Si el email no fue enviado, verifica SMTP_USER y SMTP_PASSWORD en .env.local'
        }, 201)
    
    except Exception as e:
        return error_response(f'Error: {str(e)}', 500)

@app.route('/api/academy/mi-informacion', methods=['GET'])
@requerir_autenticacion
def academy_mi_informacion():
    """Obtiene toda la información del usuario
    
    Headers: Authorization: Bearer <token>
    
    Retorna: plan, progreso, cursos inscritos, etc.
    """
    plan_id = AcademyDatabase.obtener_plan_usuario(request.user_id)
    plan_info = PlanesSubscripcion.obtener_plan(plan_id)
    progreso = AcademyDatabase.obtener_progreso(request.user_id)
    
    return safe_response({
        'user_id': request.user_id,
        'plan_actual': plan_info,
        'progreso_cursos': progreso,
        'total_cursos_disponibles': len(Cursos.listar_cursos()),
        'cursos_disponibles': [c['titulo'] for c in Cursos.listar_cursos()],
        'data_descarga_disponible': True,
        'nota': 'Usa /api/academy/exportar-reporte para descargar tu información'
    })

# ============================================================================
# ENDPOINTS: INFORMACIÓN
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """Endpoint raíz con lista de endpoints disponibles"""
    endpoints = {
        'validacion': {
            'POST /api/validar-email': 'Valida un email individual',
            'POST /api/validar-emails-lote': 'Valida múltiples emails'
        },
        'excel': {
            'POST /api/excel/sumar': 'Suma números',
            'POST /api/excel/promedio': 'Calcula promedio',
            'POST /api/excel/estadisticas': 'Calcula estadísticas completas'
        },
        'texto': {
            'POST /api/texto/analizar': 'Analiza texto'
        },
        'pagos': {
            'POST /api/pagos/crear-intento': 'Crea intento de pago con Stripe',
            'GET /api/pagos/estado/<payment_intent_id>': 'Obtiene estado de pago',
            'GET /api/pagos/listar': 'Lista pagos recientes',
            'GET /api/pagos/clave-publica': 'Obtiene clave pública Stripe'
        },
        'caja-fuerte': {
            'POST /api/vault/registro': 'Registrarse en la Caja Fuerte',
            'POST /api/vault/login': 'Inicia sesión (retorna token)',
            'POST /api/vault/guardar': 'Guarda secreto encriptado',
            'GET /api/vault/obtener/<nombre>': 'Obtiene secreto desencriptado',
            'GET /api/vault/listar': 'Lista secretos guardados',
            'DELETE /api/vault/eliminar/<nombre>': 'Elimina un secreto',
            'GET /api/vault/generar-clave': 'Genera clave de encriptación'
        },
        'academia-educativa': {
            'GET /api/academy/planes': 'Lista planes de suscripción',
            'GET /api/academy/cursos': 'Lista cursos disponibles',
            'GET /api/academy/mi-plan': 'Tu plan actual',
            'POST /api/academy/upgrade': 'Mejora tu plan',
            'GET /api/academy/progreso': 'Tu progreso en cursos',
            'POST /api/academy/registrar-progreso': 'Registra progreso',
            'POST /api/academy/exportar-reporte': 'Descarga reporte por email',
            'GET /api/academy/mi-informacion': 'Toda tu información'
        },
        'info': {
            'GET /': 'Este endpoint',
            'GET /api/health': 'Estado de salud de la API',
            'GET /api/endpoints': 'Lista de todos los endpoints'
        }
    }
    
    return safe_response(endpoints)

@app.route('/api/health', methods=['GET'])
def health():
    """Verifica que la API esté funcionando"""
    return safe_response({'status': 'healthy', 'version': '1.0.0'})

@app.route('/api/endpoints', methods=['GET'])
def list_endpoints():
    """Lista todos los endpoints disponibles"""
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'path': str(rule)
            })
    return safe_response({'endpoints': routes})

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return error_response('Endpoint no encontrado', 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return error_response('Método no permitido', 405)

@app.errorhandler(500)
def internal_error(error):
    return error_response('Error interno del servidor', 500)

# ============================================================================
# INICIO DE LA APLICACIÓN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("API UNIFICADA - Iniciando servidor...")
    print("=" * 70)
    print("\n📍 Accede a: http://localhost:10000/")
    print("\n📚 Endpoints disponibles:")
    print("   • POST /api/validar-email")
    print("   • POST /api/validar-emails-lote")
    print("   • POST /api/excel/sumar")
    print("   • POST /api/excel/estadisticas")
    print("   • POST /api/excel/promedio")
    print("   • POST /api/texto/analizar")
    print("   • POST /api/pagos/crear-intento          💳 PAGOS")
    print("   • GET  /api/pagos/estado/<payment_id>    💳 PAGOS")
    print("   • GET  /api/pagos/listar                 💳 PAGOS")
    print("   • GET  /api/pagos/clave-publica          💳 PAGOS")
    print("   • POST /api/vault/registro               🔐 CAJA FUERTE")
    print("   • POST /api/vault/login                  🔐 CAJA FUERTE")
    print("   • POST /api/vault/guardar                🔐 CAJA FUERTE")
    print("   • GET  /api/vault/obtener/<nombre>       🔐 CAJA FUERTE")
    print("   • GET  /api/vault/listar                 🔐 CAJA FUERTE")
    print("   • DELETE /api/vault/eliminar/<nombre>    🔐 CAJA FUERTE")
    print("   • GET  /api/vault/generar-clave          🔐 CAJA FUERTE")
    print("   • GET  /api/health")
    print("   • GET  /api/endpoints")
    print("\n" + "=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=10000, debug=True)
