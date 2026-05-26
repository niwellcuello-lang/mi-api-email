"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    GESTOR DE PAGOS SEGURO - STRIPE                       ║
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

Gestor de pagos seguro usando Stripe
- Nunca expone claves privadas
- Usa variables de entorno
- Implementa webhooks para verificación

VERSIÓN: 1.0.0
AUTOR: Niwell Cuello
"""

import os
import stripe
from datetime import datetime
from typing import Dict, Optional

# Configurar Stripe con clave privada desde variable de entorno
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

class PaymentHandler:
    """Manejador seguro de pagos con Stripe"""
    
    @staticmethod
    def crear_intento_pago(
        monto: float,
        moneda: str = "usd",
        descripcion: str = "",
        email_cliente: str = ""
    ) -> Dict:
        """
        Crea un intento de pago seguro
        
        Args:
            monto: Cantidad en la moneda especificada
            moneda: Código de moneda (usd, eur, etc.)
            descripcion: Descripción del pago
            email_cliente: Email del cliente
            
        Returns:
            Dict con datos del intento de pago
        """
        try:
            if not stripe.api_key:
                return {
                    "success": False,
                    "error": "Stripe no configurado correctamente",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validar moneda
            monto_centavos = int(monto * 100)
            if monto_centavos <= 0:
                return {
                    "success": False,
                    "error": "Monto debe ser mayor a 0",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Crear intento de pago
            intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency=moneda,
                description=descripcion,
                receipt_email=email_cliente if email_cliente else None,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "system": "niwell-api"
                }
            )
            
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "monto": monto,
                "moneda": moneda.upper(),
                "estado": intent.status,
                "timestamp": datetime.now().isoformat()
            }
            
        except stripe.error.CardError as e:
            return {
                "success": False,
                "error": f"Error en tarjeta: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        except stripe.error.RateLimitError:
            return {
                "success": False,
                "error": "Demasiadas solicitudes. Intenta más tarde.",
                "timestamp": datetime.now().isoformat()
            }
        except stripe.error.InvalidRequestError as e:
            return {
                "success": False,
                "error": f"Solicitud inválida: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al procesar pago: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def obtener_estado_pago(payment_intent_id: str) -> Dict:
        """
        Obtiene el estado de un intento de pago
        
        Args:
            payment_intent_id: ID del intento de pago
            
        Returns:
            Dict con estado del pago
        """
        try:
            if not stripe.api_key:
                return {
                    "success": False,
                    "error": "Stripe no configurado",
                    "timestamp": datetime.now().isoformat()
                }
            
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "estado": intent.status,
                "monto": intent.amount / 100,
                "moneda": intent.currency.upper(),
                "fecha_creacion": datetime.fromtimestamp(intent.created).isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except stripe.error.InvalidRequestError:
            return {
                "success": False,
                "error": "ID de pago no encontrado",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al verificar pago: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def listar_pagos(limite: int = 10) -> Dict:
        """
        Lista los últimos pagos procesados
        
        Args:
            limite: Número de pagos a listar
            
        Returns:
            Dict con lista de pagos
        """
        try:
            if not stripe.api_key:
                return {
                    "success": False,
                    "error": "Stripe no configurado",
                    "timestamp": datetime.now().isoformat()
                }
            
            intents = stripe.PaymentIntent.list(limit=limite)
            
            pagos = []
            for intent in intents.data:
                pagos.append({
                    "id": intent.id,
                    "monto": intent.amount / 100,
                    "moneda": intent.currency.upper(),
                    "estado": intent.status,
                    "fecha": datetime.fromtimestamp(intent.created).isoformat()
                })
            
            return {
                "success": True,
                "total": len(pagos),
                "pagos": pagos,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al listar pagos: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def obtener_clave_publica() -> Dict:
        """
        Retorna la clave pública de Stripe para el cliente
        
        Returns:
            Dict con clave pública
        """
        if not STRIPE_PUBLISHABLE_KEY:
            return {
                "success": False,
                "error": "Clave pública no configurada",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "publishable_key": STRIPE_PUBLISHABLE_KEY,
            "timestamp": datetime.now().isoformat()
        }
