"""
╔═══════════════════════════════════════════════════════════════════════════╗
║              SISTEMA EDUCATIVO + MONETIZACIÓN - ACADEMY                  ║
║                                                                           ║
║ © 2026 NIWELL CUELLO - TODOS LOS DERECHOS RESERVADOS                    ║
║                                                                           ║
║ LICENCIA COMERCIAL EXCLUSIVA                                             ║
║ Plataforma educativa con monetización integrada                          ║
║                                                                           ║
║ CONTACTO: contacto@niwell.dev                                            ║
║ SITIO WEB: www.niwell-api.com                                            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Sistema Educativo y Monetización
- Cursos y lecciones
- Planes de suscripción
- Certificados
- Reportes

VERSIÓN: 1.0.0
AUTOR: Niwell Cuello
"""

import os
import sqlite3
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from io import BytesIO

# ============================================================================
# CONFIGURACIÓN DE EMAIL
# ============================================================================

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class Cursos:
    """Cursos disponibles"""
    
    CURSOS = {
        "api-basics": {
            "titulo": "Fundamentos de APIs REST",
            "descripcion": "Aprende a crear y usar APIs REST profesionales",
            "lecciones": 5,
            "duracion_horas": 3,
            "precio_mensual": 9.99,
            "nivel": "principiante"
        },
        "seguridad": {
            "titulo": "Seguridad en APIs - Encriptación",
            "descripcion": "Aprende encriptación AES-256, JWT y autenticación",
            "lecciones": 8,
            "duracion_horas": 6,
            "precio_mensual": 19.99,
            "nivel": "intermedio"
        },
        "monetizacion": {
            "titulo": "Monetizar tu API con Stripe",
            "descripcion": "Integra pagos y crea planes de suscripción",
            "lecciones": 6,
            "duracion_horas": 4,
            "precio_mensual": 14.99,
            "nivel": "intermedio"
        },
        "produccion": {
            "titulo": "Desplegar a Producción",
            "descripcion": "Deploy, escalabilidad, monitoreo",
            "lecciones": 10,
            "duracion_horas": 8,
            "precio_mensual": 24.99,
            "nivel": "avanzado"
        }
    }
    
    @staticmethod
    def obtener_curso(curso_id: str) -> Optional[Dict]:
        """Obtiene detalles del curso"""
        return Cursos.CURSOS.get(curso_id)
    
    @staticmethod
    def listar_cursos() -> List[Dict]:
        """Lista todos los cursos"""
        return [
            {
                "id": k,
                **v
            }
            for k, v in Cursos.CURSOS.items()
        ]

class PlanesSubscripcion:
    """Planes de suscripción disponibles"""
    
    PLANES = {
        "gratuito": {
            "nombre": "Gratuito",
            "precio": 0,
            "cursos_incluidos": 1,
            "lecciones_ilimitadas": False,
            "certificados": False,
            "soporte": False,
            "descripcion": "Acceso limitado"
        },
        "basico": {
            "nombre": "Básico",
            "precio": 9.99,
            "cursos_incluidos": 3,
            "lecciones_ilimitadas": True,
            "certificados": False,
            "soporte": False,
            "descripcion": "Perfecto para empezar"
        },
        "profesional": {
            "nombre": "Profesional",
            "precio": 29.99,
            "cursos_incluidos": 10,
            "lecciones_ilimitadas": True,
            "certificados": True,
            "soporte": True,
            "descripcion": "Para desarrolladores"
        },
        "empresarial": {
            "nombre": "Empresarial",
            "precio": 99.99,
            "cursos_incluidos": 999,
            "lecciones_ilimitadas": True,
            "certificados": True,
            "soporte": True,
            "descripcion": "Solución completa"
        }
    }
    
    @staticmethod
    def obtener_plan(plan_id: str) -> Optional[Dict]:
        """Obtiene detalles del plan"""
        plan = PlanesSubscripcion.PLANES.get(plan_id)
        if plan:
            return {"id": plan_id, **plan}
        return None
    
    @staticmethod
    def listar_planes() -> List[Dict]:
        """Lista todos los planes"""
        return [
            {"id": k, **v}
            for k, v in PlanesSubscripcion.PLANES.items()
        ]

# ============================================================================
# BASE DE DATOS
# ============================================================================

class AcademyDatabase:
    """Gestor de base de datos para Academia"""
    
    DATABASE = "academy.db"
    
    @staticmethod
    def inicializar():
        """Crea tablas si no existen"""
        conn = sqlite3.connect(AcademyDatabase.DATABASE)
        c = conn.cursor()
        
        # Tabla de usuarios academy
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios_academy (
                id TEXT PRIMARY KEY,
                plan TEXT DEFAULT 'gratuito',
                fecha_suscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_renovacion TIMESTAMP,
                estado TEXT DEFAULT 'activo'
            )
        ''')
        
        # Tabla de progreso en cursos
        c.execute('''
            CREATE TABLE IF NOT EXISTS progreso_cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                curso_id TEXT NOT NULL,
                lecciones_completadas INTEGER DEFAULT 0,
                porcentaje_completo REAL DEFAULT 0,
                certificado_obtenido BOOLEAN DEFAULT FALSE,
                fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_completacion TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES usuarios_academy(id),
                UNIQUE(user_id, curso_id)
            )
        ''')
        
        # Tabla de suscripciones
        c.execute('''
            CREATE TABLE IF NOT EXISTS suscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                plan TEXT NOT NULL,
                stripe_subscription_id TEXT,
                estado TEXT DEFAULT 'activo',
                fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_vencimiento TIMESTAMP,
                fecha_proximo_pago TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES usuarios_academy(id)
            )
        ''')
        
        # Tabla de reportes/exportaciones
        c.execute('''
            CREATE TABLE IF NOT EXISTS reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                tipo TEXT,
                contenido TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enviado_por_email BOOLEAN DEFAULT FALSE,
                FOREIGN KEY(user_id) REFERENCES usuarios_academy(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def obtener_o_crear_usuario(user_id: str, email: str) -> bool:
        """Crea usuario en academy si no existe"""
        try:
            conn = sqlite3.connect(AcademyDatabase.DATABASE)
            c = conn.cursor()
            
            c.execute('SELECT id FROM usuarios_academy WHERE id = ?', (user_id,))
            if not c.fetchone():
                c.execute('''
                    INSERT INTO usuarios_academy (id, plan)
                    VALUES (?, 'gratuito')
                ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def obtener_plan_usuario(user_id: str) -> str:
        """Obtiene plan del usuario"""
        conn = sqlite3.connect(AcademyDatabase.DATABASE)
        c = conn.cursor()
        
        c.execute('SELECT plan FROM usuarios_academy WHERE id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        return row[0] if row else "gratuito"
    
    @staticmethod
    def actualizar_plan(user_id: str, nuevo_plan: str) -> bool:
        """Actualiza plan del usuario"""
        try:
            conn = sqlite3.connect(AcademyDatabase.DATABASE)
            c = conn.cursor()
            
            c.execute('''
                UPDATE usuarios_academy 
                SET plan = ?, fecha_suscripcion = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (nuevo_plan, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def registrar_progreso(user_id: str, curso_id: str, lecciones: int) -> bool:
        """Registra progreso en un curso"""
        try:
            conn = sqlite3.connect(AcademyDatabase.DATABASE)
            c = conn.cursor()
            
            curso = Cursos.obtener_curso(curso_id)
            if not curso:
                return False
            
            porcentaje = (lecciones / curso['lecciones']) * 100
            
            c.execute('''
                INSERT OR REPLACE INTO progreso_cursos
                (user_id, curso_id, lecciones_completadas, porcentaje_completo)
                VALUES (?, ?, ?, ?)
            ''', (user_id, curso_id, lecciones, porcentaje))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def obtener_progreso(user_id: str) -> List[Dict]:
        """Obtiene progreso del usuario en todos los cursos"""
        conn = sqlite3.connect(AcademyDatabase.DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT curso_id, lecciones_completadas, porcentaje_completo, 
                   certificado_obtenido, fecha_inicio, fecha_completacion
            FROM progreso_cursos
            WHERE user_id = ?
            ORDER BY fecha_inicio DESC
        ''', (user_id,))
        
        rows = c.fetchall()
        conn.close()
        
        return [{
            'curso_id': row[0],
            'lecciones_completadas': row[1],
            'porcentaje_completo': row[2],
            'certificado_obtenido': row[3],
            'fecha_inicio': row[4],
            'fecha_completacion': row[5]
        } for row in rows]
    
    @staticmethod
    def guardar_reporte(user_id: str, tipo: str, contenido: str) -> int:
        """Guarda reporte generado"""
        try:
            conn = sqlite3.connect(AcademyDatabase.DATABASE)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO reportes (user_id, tipo, contenido)
                VALUES (?, ?, ?)
            ''', (user_id, tipo, contenido))
            
            report_id = c.lastrowid
            conn.commit()
            conn.close()
            return report_id
        except Exception:
            return -1

# ============================================================================
# EMAIL HANDLER
# ============================================================================

class EmailHandler:
    """Manejador de envío de emails"""
    
    @staticmethod
    def enviar_documento(destinatario: str, asunto: str, cuerpo: str, 
                        archivo_contenido: str = None, nombre_archivo: str = None) -> bool:
        """Envía email con documento adjunto"""
        try:
            if not SMTP_USER or not SMTP_PASSWORD:
                return False
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            # Agregar cuerpo
            msg.attach(MIMEText(cuerpo, 'html'))
            
            # Agregar archivo si existe
            if archivo_contenido and nombre_archivo:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(archivo_contenido.encode())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', f'attachment; filename= {nombre_archivo}')
                msg.attach(attachment)
            
            # Enviar
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")
            return False

# ============================================================================
# GENERADOR DE REPORTES
# ============================================================================

class ReporteGenerator:
    """Genera reportes educativos y financieros"""
    
    @staticmethod
    def generar_reporte_personal(user_id: str, email: str) -> str:
        """Genera reporte personal con todos los datos"""
        
        plan = AcademyDatabase.obtener_plan_usuario(user_id)
        progreso = AcademyDatabase.obtener_progreso(user_id)
        plan_info = PlanesSubscripcion.obtener_plan(plan)
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .info-box {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 15px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                table th, table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                table th {{ background: #007bff; color: white; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>📊 Reporte Personal - {datetime.now().strftime('%d/%m/%Y')}</h1>
            
            <div class="info-box">
                <h2>👤 Información de Usuario</h2>
                <p><strong>ID:</strong> {user_id}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Plan Actual:</strong> {plan_info['nombre'] if plan_info else 'N/A'}</p>
                <p><strong>Precio Mensual:</strong> ${plan_info['precio'] if plan_info else 0}</p>
                <p><strong>Desde:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
            
            <div class="info-box">
                <h2>📚 Beneficios del Plan</h2>
                <ul>
                    <li>Cursos Incluidos: {plan_info['cursos_incluidos'] if plan_info else 0}</li>
                    <li>Lecciones Ilimitadas: {'✓ Sí' if plan_info and plan_info['lecciones_ilimitadas'] else '✗ No'}</li>
                    <li>Certificados: {'✓ Sí' if plan_info and plan_info['certificados'] else '✗ No'}</li>
                    <li>Soporte: {'✓ Sí' if plan_info and plan_info['soporte'] else '✗ No'}</li>
                </ul>
            </div>
            
            <h2>📈 Progreso en Cursos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Curso</th>
                        <th>Lecciones</th>
                        <th>Progreso</th>
                        <th>Certificado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for prog in progreso:
            curso = Cursos.obtener_curso(prog['curso_id'])
            curso_nombre = curso['titulo'] if curso else prog['curso_id']
            certificado = "✓" if prog['certificado_obtenido'] else "—"
            
            html += f"""
                    <tr>
                        <td>{curso_nombre}</td>
                        <td>{prog['lecciones_completadas']}</td>
                        <td>{prog['porcentaje_completo']:.1f}%</td>
                        <td>{certificado}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
            
            <div class="info-box">
                <h2>💡 Próximas Acciones</h2>
                <ul>
                    <li>Continúa con los cursos disponibles</li>
                    <li>Completa lecciones para obtener certificados</li>
                    <li>Consulta los recursos de aprendizaje</li>
                    <li>Únete a la comunidad educativa</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>Reporte generado automáticamente por Niwell Academy</p>
                <p>© 2026 NIWELL CUELLO - Todos los derechos reservados</p>
                <p>Para soporte: contacto@niwell.dev</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def generar_reporte_monetizacion(user_id: str) -> str:
        """Genera reporte de monetización y ROI"""
        
        plan = AcademyDatabase.obtener_plan_usuario(user_id)
        plan_info = PlanesSubscripcion.obtener_plan(plan)
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; border-bottom: 3px solid #28a745; padding-bottom: 10px; }}
                .info-box {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0; }}
                .metric {{ display: inline-block; width: 45%; margin: 10px 2%; padding: 15px; background: #fff; border: 1px solid #ddd; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #28a745; }}
                .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <h1>💰 Reporte de Monetización</h1>
            
            <div class="info-box">
                <h2>Plan Actual</h2>
                <div class="metric">
                    <div class="metric-value">${plan_info['precio'] if plan_info else 0}</div>
                    <div class="metric-label">Precio Mensual</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${(plan_info['precio'] if plan_info else 0) * 12}</div>
                    <div class="metric-label">Anual</div>
                </div>
            </div>
            
            <div class="info-box">
                <h2>📊 Uso de Herramientas</h2>
                <p>Con tu plan {plan_info['nombre'] if plan_info else 'Gratuito'}, tienes acceso a:</p>
                <ul>
                    <li>✓ API Unificada (Validación, Cálculos, Análisis)</li>
                    <li>✓ Sistema de Pagos (Stripe integrado)</li>
                    <li>✓ Caja Fuerte Encriptada (AES-256)</li>
                    <li>✓ Academia Educativa (Cursos y Lecciones)</li>
                    <li>✓ Generador de Reportes</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h2>🎯 Recomendaciones</h2>
                <ul>
                    <li>Actualiza a plan Profesional para acceso a certificados</li>
                    <li>Obtén soporte premium con plan Profesional o superior</li>
                    <li>Considera plan Empresarial para soluciones completas</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p>© 2026 NIWELL CUELLO - Todos los derechos reservados</p>
            </div>
        </body>
        </html>
        """
        
        return html
