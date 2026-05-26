"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   CAJA FUERTE SEGURA - VAULT SYSTEM                      ║
║                                                                           ║
║ © 2026 NIWELL CUELLO - TODOS LOS DERECHOS RESERVADOS                    ║
║                                                                           ║
║ LICENCIA COMERCIAL EXCLUSIVA                                             ║
║ Sistema de cifrado y autenticación de máximo nivel                       ║
║                                                                           ║
║ CONTACTO: contacto@niwell.dev                                            ║
║ SITIO WEB: www.niwell-api.com                                            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Sistema de Caja Fuerte Encriptada
- Autenticación con JWT
- Encriptación AES-256
- Solo el propietario puede acceder

VERSIÓN: 1.0.0
AUTOR: Niwell Cuello
"""

import os
import sqlite3
import json
import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
import bcrypt
from flask import request, jsonify

# Configuración
SECRET_KEY = os.getenv("VAULT_SECRET_KEY", "clave-super-secreta-cambiar-en-produccion")
CIPHER_KEY = os.getenv("VAULT_CIPHER_KEY")
DATABASE = "vault.db"
JWT_EXPIRY_HOURS = 24

# ============================================================================
# UTILIDADES DE ENCRIPTACIÓN
# ============================================================================

class Encryptor:
    """Encriptador AES-256 para datos sensibles"""
    
    @staticmethod
    def generar_clave():
        """Genera una clave de encriptación válida"""
        return Fernet.generate_key().decode()
    
    @staticmethod
    def encriptar(datos: str, clave: str) -> str:
        """Encripta datos con clave AES-256"""
        try:
            f = Fernet(clave.encode())
            return f.encrypt(datos.encode()).decode()
        except Exception as e:
            raise Exception(f"Error al encriptar: {str(e)}")
    
    @staticmethod
    def desencriptar(datos_encriptados: str, clave: str) -> str:
        """Desencripta datos con clave AES-256"""
        try:
            f = Fernet(clave.encode())
            return f.decrypt(datos_encriptados.encode()).decode()
        except Exception as e:
            raise Exception(f"Error al desencriptar: {str(e)}")

# ============================================================================
# UTILIDADES DE AUTENTICACIÓN
# ============================================================================

class AuthHandler:
    """Manejador de autenticación y sesiones"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash bcrypt de contraseña"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verificar_password(password: str, hash_guardado: str) -> bool:
        """Verifica contraseña contra hash"""
        return bcrypt.checkpw(password.encode(), hash_guardado.encode())
    
    @staticmethod
    def crear_token_jwt(user_id: str, expiry_hours: int = JWT_EXPIRY_HOURS) -> str:
        """Crea token JWT con expiración"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verificar_token_jwt(token: str) -> Optional[Dict]:
        """Verifica token JWT y retorna payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# ============================================================================
# BASE DE DATOS
# ============================================================================

class VaultDatabase:
    """Gestor de base de datos para la caja fuerte"""
    
    @staticmethod
    def inicializar():
        """Crea tablas si no existen"""
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Tabla de usuarios
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_ultimo_acceso TIMESTAMP
            )
        ''')
        
        # Tabla de secretos encriptados
        c.execute('''
            CREATE TABLE IF NOT EXISTS secretos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                datos_encriptados TEXT NOT NULL,
                tipo TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES usuarios(id),
                UNIQUE(user_id, nombre)
            )
        ''')
        
        # Tabla de auditoría
        c.execute('''
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                accion TEXT NOT NULL,
                detalles TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES usuarios(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def crear_usuario(user_id: str, email: str, password: str) -> bool:
        """Crea nuevo usuario en la caja fuerte"""
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            password_hash = AuthHandler.hash_password(password)
            c.execute('''
                INSERT INTO usuarios (id, email, password_hash)
                VALUES (?, ?, ?)
            ''', (user_id, email, password_hash))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def obtener_usuario(email: str) -> Optional[Dict]:
        """Obtiene usuario por email"""
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('SELECT id, email, password_hash FROM usuarios WHERE email = ?', (email,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'email': row[1],
                'password_hash': row[2]
            }
        return None
    
    @staticmethod
    def guardar_secreto(user_id: str, nombre: str, datos_encriptados: str, tipo: str = "general") -> bool:
        """Guarda secreto encriptado en la caja fuerte"""
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                INSERT OR REPLACE INTO secretos 
                (user_id, nombre, datos_encriptados, tipo, fecha_actualizacion)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, nombre, datos_encriptados, tipo))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def obtener_secreto(user_id: str, nombre: str) -> Optional[str]:
        """Obtiene secreto encriptado del usuario"""
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT datos_encriptados FROM secretos 
            WHERE user_id = ? AND nombre = ?
        ''', (user_id, nombre))
        
        row = c.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    @staticmethod
    def listar_secretos(user_id: str) -> list:
        """Lista todos los secretos del usuario (sin datos)"""
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT nombre, tipo, fecha_creacion, fecha_actualizacion 
            FROM secretos 
            WHERE user_id = ?
            ORDER BY fecha_actualizacion DESC
        ''', (user_id,))
        
        rows = c.fetchall()
        conn.close()
        
        return [{
            'nombre': row[0],
            'tipo': row[1],
            'fecha_creacion': row[2],
            'fecha_actualizacion': row[3]
        } for row in rows]
    
    @staticmethod
    def eliminar_secreto(user_id: str, nombre: str) -> bool:
        """Elimina secreto del usuario"""
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                DELETE FROM secretos 
                WHERE user_id = ? AND nombre = ?
            ''', (user_id, nombre))
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    @staticmethod
    def registrar_auditoria(user_id: str, accion: str, detalles: str = ""):
        """Registra acción en auditoría"""
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO auditoria (user_id, accion, detalles)
                VALUES (?, ?, ?)
            ''', (user_id, accion, detalles))
            
            conn.commit()
            conn.close()
        except Exception:
            pass

# ============================================================================
# DECORADORES
# ============================================================================

def requerir_autenticacion(f):
    """Decorador para proteger endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Buscar token en headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'Token inválido',
                    'timestamp': datetime.utcnow().isoformat()
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token requerido',
                'timestamp': datetime.utcnow().isoformat()
            }), 401
        
        payload = AuthHandler.verificar_token_jwt(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Token expirado o inválido',
                'timestamp': datetime.utcnow().isoformat()
            }), 401
        
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated_function
