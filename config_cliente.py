#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config_cliente.py - CONFIGURACIÓN CENTRALIZADA
═══════════════════════════════════════════════════════════════════════════════
Este es el ÚNICO archivo que necesitas modificar para configurar un cliente.
Todo lo demás se configura automáticamente desde aquí.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
from datetime import timedelta

# ═══════════════════════════════════════════════════════════════════════════════
# 🏢 DATOS DEL CLIENTE - CAMBIAR AQUÍ SOLAMENTE
# ═══════════════════════════════════════════════════════════════════════════════


#CUIT = '27333429433'                    # ← CUIT del cliente    
#RAZON_SOCIAL = 'NOELIA FREDIANI   '     # ← Razón social del cliente
#PUNTO_VENTA = 4                         # ← Punto de venta AFIP  Noelia: 4 


#CUIT = '20292618310'                    # ← CUIT del cliente    
#RAZON_SOCIAL = 'GILES HERNAN DARIO'     # ← Razón social del cliente
#PUNTO_VENTA = 2                         # ← Punto de venta AFIP  Noelia: 4 


# ═══ DATOS FISCALES ═══
CUIT = '20291687297'                    # ← CUIT del cliente     Noelia: 20203852100
RAZON_SOCIAL = 'Schiro Diego Raul'       # ← Razón social del cliente
PUNTO_VENTA = 9                         # ← Punto de venta AFIP  Noelia: 3

# ═══ BASE DE DATOS ═══
DB_HOST = 'localhost'                   # ← Host de MySQL
DB_USER = 'pos_user'                    # ← Usuario MySQL
DB_PASSWORD = 'pos_password'            # ← Contraseña MySQL
DB_NAME = 'schiro'                     # ← Nombre de la base de datos

# ═══ AMBIENTE AFIP ═══
USE_HOMOLOGACION = False                # ← True = Pruebas, False = Producción

# ═══ CERTIFICADOS AFIP ═══
CERT_PATH = 'certificados/certificado.crt'  # ← Ruta del certificado
KEY_PATH = 'certificados/private.key'       # ← Ruta de la clave privada

# ═══════════════════════════════════════════════════════════════════════════════
# FIN DE CONFIGURACIÓN - NO MODIFICAR DEBAJO DE ESTA LÍNEA
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN AUTOMÁTICA
# ═══════════════════════════════════════════════════════════════════════════════

class Config:
    """Configuración de Flask y Base de Datos"""
    
    # Clave secreta (auto-generada desde CUIT)
    SECRET_KEY = os.environ.get('SECRET_KEY') or f'factufacil_{CUIT}_2025'
    
    # Configuración MySQL
    MYSQL_HOST = DB_HOST
    MYSQL_USER = DB_USER
    MYSQL_PASSWORD = DB_PASSWORD
    MYSQL_DATABASE = DB_NAME
    
    # URI de SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Debug
    DEBUG = True
    TESTING = False


class ARCAConfig:
    """Configuración para AFIP/ARCA"""
    
    # Datos de la empresa (desde arriba)
    CUIT = CUIT
    PUNTO_VENTA = PUNTO_VENTA
    RAZON_SOCIAL = RAZON_SOCIAL
    
    # Rutas de certificados
    CERT_PATH = CERT_PATH
    KEY_PATH = KEY_PATH
    
    # Ambiente
    USE_HOMOLOGACION = USE_HOMOLOGACION
    
    # URLs de AFIP (automáticas según ambiente)
    WSAA_URL_HOMO = 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms'
    WSFEv1_URL_HOMO = 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL'
    WSAA_URL_PROD = 'https://wsaa.afip.gov.ar/ws/services/LoginCms'
    WSFEv1_URL_PROD = 'https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL'
    
    @property
    def WSAA_URL(self):
        return self.WSAA_URL_HOMO if self.USE_HOMOLOGACION else self.WSAA_URL_PROD
    
    @property
    def WSFEv1_URL(self):
        return self.WSFEv1_URL_HOMO if self.USE_HOMOLOGACION else self.WSFEv1_URL_PROD
    
    # Archivo de cache para tokens
    TOKEN_CACHE_FILE = 'cache/token_arca.json'
    
    # Tipos de comprobante
    TIPOS_COMPROBANTE = {
        '01': 'Factura A',
        '02': 'Nota de Débito A',
        '03': 'Nota de Crédito A',
        '06': 'Factura B',
        '07': 'Nota de Débito B',
        '08': 'Nota de Crédito B',
        '11': 'Factura C',
        '12': 'Nota de Débito C',
        '13': 'Nota de Crédito C',
    }
    
    # Tipos de documento
    TIPOS_DOCUMENTO = {
        '80': 'CUIT',
        '86': 'CUIL',
        '96': 'DNI',
        '99': 'Sin identificar/venta global diaria'
    }
    
    # Condiciones IVA
    CONDICIONES_IVA = {
        'IVA_RESPONSABLE_INSCRIPTO': 1,
        'IVA_RESPONSABLE_NO_INSCRIPTO': 2,
        'IVA_NO_RESPONSABLE': 3,
        'IVA_SUJETO_EXENTO': 4,
        'CONSUMIDOR_FINAL': 5,
        'RESPONSABLE_MONOTRIBUTO': 6,
        'SUJETO_NO_CATEGORIZADO': 7,
        'PROVEEDOR_DEL_EXTERIOR': 8,
        'CLIENTE_DEL_EXTERIOR': 9,
        'IVA_LIBERADO_LEY_19640': 10,
        'IVA_RESPONSABLE_INSCRIPTO_AGENTE_PERCEPCION': 11,
        'PEQUENO_CONTRIBUYENTE_EVENTUAL': 12,
        'MONOTRIBUTISTA_SOCIAL': 13,
        'PEQUENO_CONTRIBUYENTE_EVENTUAL_SOCIAL': 14
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDACIÓN DE CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def validar_configuracion():
    """Valida que la configuración sea correcta"""
    errores = []
    
    # Validar CUIT
    if not CUIT or len(CUIT) != 11:
        errores.append(f"❌ CUIT inválido: '{CUIT}' (debe tener 11 dígitos)")
    
    # Validar punto de venta
    if not isinstance(PUNTO_VENTA, int) or PUNTO_VENTA <= 0:
        errores.append(f"❌ PUNTO_VENTA inválido: {PUNTO_VENTA} (debe ser número positivo)")
    
    # Validar razón social
    if not RAZON_SOCIAL or len(RAZON_SOCIAL) < 3:
        errores.append(f"❌ RAZON_SOCIAL inválida: '{RAZON_SOCIAL}'")
    
    # Validar certificados
    if not os.path.exists(CERT_PATH):
        errores.append(f"⚠️ Certificado no encontrado: {CERT_PATH}")
    
    if not os.path.exists(KEY_PATH):
        errores.append(f"⚠️ Clave privada no encontrada: {KEY_PATH}")
    
    return errores


def mostrar_configuracion():
    """Muestra la configuración actual"""
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "CONFIGURACIÓN DEL CLIENTE" + " "*33 + "║")
    print("╠" + "═"*78 + "╣")
    print(f"║ CUIT:            {CUIT:<59} ║")
    print(f"║ Razón Social:    {RAZON_SOCIAL:<59} ║")
    print(f"║ Punto de Venta:  {PUNTO_VENTA:<59} ║")
    print(f"║ Base de Datos:   {DB_NAME}@{DB_HOST:<49} ║")
    print(f"║ Ambiente:        {'HOMOLOGACIÓN (Pruebas)' if USE_HOMOLOGACION else 'PRODUCCIÓN':<59} ║")
    print("╚" + "═"*78 + "╝")
    
    # Validar
    errores = validar_configuracion()
    if errores:
        print("\n⚠️  ADVERTENCIAS:")
        for error in errores:
            print(f"   {error}")
    else:
        print("\n✅ Configuración válida")


# Si se ejecuta directamente, mostrar configuración
if __name__ == '__main__':
    mostrar_configuracion()