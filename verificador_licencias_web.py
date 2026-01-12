# verificador_licencias_web.py - Verificador con interfaz web

"""
Sistema de verificación de licencias con interfaz web
En lugar de bloquear en consola, redirige a página de bloqueo
"""

import requests
import json
from datetime import datetime

# ============== CONFIGURACIÓN ==============
URL_LICENCIAS = URL_LICENCIAS = "https://gist.githubusercontent.com/pablogre/77854e5d55d01018af8a4cab8ab5cc30/raw"   ##"https://gist.githubusercontent.com/pablogre/77854e5d55d01018af8a4cab8ab5cc30/raw/licencias.json"

# Información de contacto para mensajes
CONTACTO_EMAIL = "pablogustavore@gmail.com"
CONTACTO_TELEFONO = "+54 9 336 4537093"
CONTACTO_WEB = "pablore.com.ar"

# Modo prueba: si es True, permite acceso aunque falle la verificación
MODO_PRUEBA = False

# Timeout de la petición HTTP (segundos)
TIMEOUT = 10
# ============================================


def descargar_licencias():
    """
    Descarga el archivo de licencias desde el servidor
    
    Returns:
        dict: Contenido del JSON o None si hay error
    """
    try:
        response = requests.get(URL_LICENCIAS, timeout=TIMEOUT, verify=True)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error al descargar licencias: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout al conectar con el servidor (>{TIMEOUT}s)")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión con el servidor")
        return None
    except json.JSONDecodeError:
        print("❌ Error al procesar el archivo de licencias")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None


def verificar_licencia(cuit):
    """
    Verifica el estado de la licencia para un CUIT
    
    Args:
        cuit (str): CUIT del cliente a verificar
        
    Returns:
        dict: {
            'valida': bool,
            'activo': bool,
            'mora': bool,
            'razon_social': str,
            'mensaje': str,
            'tipo_bloqueo': str  # 'sin_bloqueo', 'mora', 'bloqueado', 'error'
        }
    """
    resultado = {
        'valida': False,
        'activo': False,
        'mora': False,
        'razon_social': '',
        'mensaje': '',
        'tipo_bloqueo': 'error',
        'contacto': {
            'email': CONTACTO_EMAIL,
            'telefono': CONTACTO_TELEFONO,
            'web': CONTACTO_WEB
        }
    }
    
    print(f"🔐 Verificando licencia para CUIT: {cuit}")
    print(f"📡 Verificando licencias...")
    
    # Descargar archivo de licencias
    licencias = descargar_licencias()
    
    if licencias is None:
        # Error al descargar
        if MODO_PRUEBA:
            print("⚠️ MODO PRUEBA: Permitiendo acceso sin verificación")
            resultado['valida'] = True
            resultado['activo'] = True
            resultado['tipo_bloqueo'] = 'sin_bloqueo'
            resultado['mensaje'] = "Modo prueba - Sin verificación"
        else:
            resultado['tipo_bloqueo'] = 'error'
            resultado['mensaje'] = "No se pudo verificar la licencia del sistema. Verifique su conexión a internet."
        return resultado
    
    # Buscar el CUIT en las licencias
    if cuit not in licencias.get('clientes', {}):
        resultado['tipo_bloqueo'] = 'no_encontrada'
        resultado['mensaje'] = f"No se encontró una licencia válida para este sistema (CUIT: {cuit})."
        return resultado
    
    # Obtener datos del cliente
    cliente = licencias['clientes'][cuit]
    resultado['razon_social'] = cliente.get('razon_social', 'Sin nombre')
    resultado['activo'] = cliente.get('activo', False)
    resultado['mora'] = cliente.get('mora', False)
    resultado['fecha_vencimiento'] = cliente.get('fecha_vencimiento', '')
    resultado['observaciones'] = cliente.get('observaciones', '')
    
    # Verificar si está activo
    if not resultado['activo']:
        resultado['valida'] = False
        resultado['tipo_bloqueo'] = 'bloqueado'
        resultado['mensaje'] = "El sistema se encuentra desactivado."
        return resultado
    
    # Verificar mora
    if resultado['mora']:
        resultado['valida'] = True  # Puede usar el sistema pero con advertencia
        resultado['tipo_bloqueo'] = 'mora'
        resultado['mensaje'] = "Su período de mantenimiento del sistema se encuentra vencido."
        return resultado
    
    # Todo OK
    resultado['valida'] = True
    resultado['activo'] = True
    resultado['tipo_bloqueo'] = 'sin_bloqueo'
    resultado['mensaje'] = f"Licencia válida"
    
    print(f"✅ Licencia válida: {resultado['razon_social']}")
    
    return resultado


# Test del módulo
if __name__ == '__main__':
    import sys
    
    print("="*60)
    print("  VERIFICADOR DE LICENCIAS - TEST")
    print("="*60)
    
    # CUIT de prueba
    cuit_test = "27333429433"
    
    if len(sys.argv) > 1:
        cuit_test = sys.argv[1]
    
    resultado = verificar_licencia(cuit_test)
    
    print("\n" + "="*60)
    print("RESULTADO:")
    print("="*60)
    print(f"Válida: {resultado['valida']}")
    print(f"Activo: {resultado['activo']}")
    print(f"Mora: {resultado['mora']}")
    print(f"Tipo Bloqueo: {resultado['tipo_bloqueo']}")
    print(f"Razón Social: {resultado['razon_social']}")
    print(f"Mensaje: {resultado['mensaje']}")
    print("="*60)