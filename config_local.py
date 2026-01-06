#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración local del sistema POS AFIP
Archivo generado automáticamente el 2025-09-04 13:02:41
"""

class Config:
    """Configuración de Flask"""
    SECRET_KEY = 'tu_clave_secreta_20250904'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://pos_user:pos_password@localhost/schiro'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración adicional
    DEBUG = True
    TESTING = False

class ARCAConfig:
    """Configuración de AFIP/ARCA"""
    
    # Datos de la empresa
    CUIT = '20292618310'  # Noelia '27333429433'

    PUNTO_VENTA = 2       # Noelia  PUNTO_VENTA = 2
    
    # Certificados digitales
    CERT_PATH = 'certificados/certificado.crt'
    KEY_PATH = 'certificados/private.key'
    
    # Ambiente (True = Homologación, False = Producción)
    USE_HOMOLOGACION = False
    
    # URLs de servicios AFIP
    @property
    def WSAA_URL(self):
        if self.USE_HOMOLOGACION:
            return 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl'
        else:
            return 'https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl'
    
    @property
    def WSFEv1_URL(self):
        if self.USE_HOMOLOGACION:
            return 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL'
        else:
            return 'https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL'
    
    # Cache de tokens
    TOKEN_CACHE_FILE = 'cache/token_afip.json'
    
    # Logging
    LOG_FILE = 'logs/afip.log'
    LOG_LEVEL = 'DEBUG' if USE_HOMOLOGACION else 'INFO'
