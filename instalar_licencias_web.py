# instalar_licencias_web.py - Instalador versión web

"""
Instalador del sistema de licencias - Versión con interfaz web
Modifica app.py y crea template HTML automáticamente
"""

import os
import sys
import shutil
from datetime import datetime

def crear_backup():
    """Crea backup de app.py"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'app_backup_{timestamp}.py'
    
    try:
        shutil.copy2('app.py', backup_name)
        print(f"✅ Backup creado: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return None

def crear_template_html():
    """Crea el template HTML de bloqueo"""
    
    # Verificar que existe la carpeta templates
    if not os.path.exists('templates'):
        print("❌ No se encontró la carpeta 'templates'")
        print("   Debe existir la carpeta templates/ en el directorio actual")
        return False
    
    # Leer el contenido del template
    template_html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Bloqueado - FactuFacil</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .bloqueo-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 90%;
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .bloqueo-header {
            padding: 40px 40px 30px;
            text-align: center;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .bloqueo-header.mora {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            color: #333;
        }
        .bloqueo-header.error {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            color: #333;
        }
        .bloqueo-icon {
            font-size: 80px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        .bloqueo-body { padding: 40px; }
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .contacto-item {
            display: flex;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .contacto-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        .contacto-item i {
            font-size: 24px;
            margin-right: 15px;
            color: #667eea;
            width: 30px;
        }
        .btn-custom {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            color: white;
        }
    </style>
</head>
<body>
    <div class="bloqueo-card">
        <div class="bloqueo-header {% if licencia_info.tipo_bloqueo == 'mora' %}mora{% elif licencia_info.tipo_bloqueo == 'error' %}error{% endif %}">
            {% if licencia_info.tipo_bloqueo == 'bloqueado' or licencia_info.tipo_bloqueo == 'no_encontrada' %}
                <div class="bloqueo-icon"><i class="fas fa-lock"></i></div>
                <h1 class="mb-0"><strong>Acceso Bloqueado</strong></h1>
            {% elif licencia_info.tipo_bloqueo == 'mora' %}
                <div class="bloqueo-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <h1 class="mb-0"><strong>Mantenimiento Vencido</strong></h1>
            {% elif licencia_info.tipo_bloqueo == 'error' %}
                <div class="bloqueo-icon"><i class="fas fa-wifi"></i></div>
                <h1 class="mb-0"><strong>Error de Conexión</strong></h1>
            {% endif %}
        </div>
        <div class="bloqueo-body">
            {% if licencia_info.razon_social %}
            <div class="info-box">
                <h5><i class="fas fa-building me-2"></i>{{ licencia_info.razon_social }}</h5>
                {% if licencia_info.fecha_vencimiento %}
                <p class="mb-0 text-muted"><small><i class="far fa-calendar me-2"></i>Vencimiento: {{ licencia_info.fecha_vencimiento }}</small></p>
                {% endif %}
            </div>
            {% endif %}
            <div class="my-4">
                <p class="lead">{{ licencia_info.mensaje }}</p>
                {% if licencia_info.tipo_bloqueo == 'mora' %}
                <p class="text-muted">Para continuar recibiendo soporte técnico, debe regularizar su situación.</p>
                {% elif licencia_info.tipo_bloqueo == 'bloqueado' %}
                <p class="text-muted">Para reactivar su licencia, contacte con soporte.</p>
                {% endif %}
            </div>
            <h5 class="mb-3"><i class="fas fa-headset me-2"></i>Contacto</h5>
            <div class="contacto-item">
                <i class="fas fa-envelope"></i>
                <div><strong>Email</strong><br><a href="mailto:{{ licencia_info.contacto.email }}">{{ licencia_info.contacto.email }}</a></div>
            </div>
            <div class="contacto-item">
                <i class="fas fa-phone"></i>
                <div><strong>WhatsApp</strong><br><a href="https://wa.me/{{ licencia_info.contacto.telefono.replace('+', '').replace(' ', '').replace('-', '') }}" target="_blank">{{ licencia_info.contacto.telefono }}</a></div>
            </div>
            <div class="contacto-item">
                <i class="fas fa-globe"></i>
                <div><strong>Web</strong><br><a href="https://{{ licencia_info.contacto.web }}" target="_blank">{{ licencia_info.contacto.web }}</a></div>
            </div>
            {% if licencia_info.tipo_bloqueo == 'mora' %}
            <div class="text-center mt-4">
                <a href="/" class="btn btn-custom"><i class="fas fa-arrow-right me-2"></i>Continuar al Sistema</a>
                <p class="text-muted mt-2"><small>Puede continuar temporalmente</small></p>
            </div>
            {% else %}
            <div class="text-center mt-4">
                <a href="/verificar_licencia_reload" class="btn btn-custom"><i class="fas fa-redo me-2"></i>Verificar Nuevamente</a>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>'''
    
    try:
        with open('templates/licencia_bloqueada.html', 'w', encoding='utf-8') as f:
            f.write(template_html)
        print("✅ Template HTML creado: templates/licencia_bloqueada.html")
        return True
    except Exception as e:
        print(f"❌ Error creando template: {e}")
        return False

def modificar_app_py():
    """Modifica app.py para agregar verificación web de licencias"""
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # 1. Agregar imports
        codigo_imports = """
# ================ SISTEMA DE VERIFICACIÓN DE LICENCIAS (WEB) ================
from verificador_licencias_web import verificar_licencia
from functools import wraps
"""
        
        if 'from caja import init_caja_system' in contenido and 'verificador_licencias_web' not in contenido:
            contenido = contenido.replace(
                'from caja import init_caja_system',
                'from caja import init_caja_system' + codigo_imports
            )
            print("✅ Imports agregados")
        
        # 2. Agregar verificación
        codigo_verificacion = """

# ================ VERIFICACIÓN DE LICENCIA AL INICIO ================
print(f"\\n{'='*60}")
print(f"🔐 VERIFICANDO LICENCIA DEL SISTEMA")
print(f"{'='*60}")
CUIT_SISTEMA = ARCA_CONFIG.CUIT
print(f"CUIT: {CUIT_SISTEMA}")
resultado_licencia = verificar_licencia(CUIT_SISTEMA)
if resultado_licencia['tipo_bloqueo'] == 'bloqueado':
    print(f"🔴 Sistema bloqueado")
elif resultado_licencia['tipo_bloqueo'] == 'mora':
    print(f"🟡 Advertencia de mora")
else:
    print(f"✅ Licencia válida: {resultado_licencia.get('razon_social', '')}")
print(f"{'='*60}\\n")
app.config['LICENCIA_INFO'] = resultado_licencia
"""
        
        if 'ARCA_CONFIG = DefaultARCAConfig()' in contenido and 'VERIFICACIÓN DE LICENCIA AL INICIO' not in contenido:
            contenido = contenido.replace(
                'ARCA_CONFIG = DefaultARCAConfig()',
                'ARCA_CONFIG = DefaultARCAConfig()' + codigo_verificacion
            )
            print("✅ Verificación agregada")
        
        # 3. Agregar decorador y rutas
        codigo_rutas = """

def requiere_licencia_activa(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        licencia_info = app.config.get('LICENCIA_INFO', {})
        if licencia_info.get('tipo_bloqueo') in ['bloqueado', 'no_encontrada', 'error']:
            return redirect(url_for('licencia_bloqueada'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/licencia_bloqueada')
def licencia_bloqueada():
    return render_template('licencia_bloqueada.html', 
                         licencia_info=app.config.get('LICENCIA_INFO', {}))

@app.route('/verificar_licencia_reload')
def verificar_licencia_reload():
    resultado = verificar_licencia(ARCA_CONFIG.CUIT)
    app.config['LICENCIA_INFO'] = resultado
    if resultado['tipo_bloqueo'] in ['sin_bloqueo', 'mora']:
        return redirect(url_for('index'))
    return redirect(url_for('licencia_bloqueada'))

"""
        
        if 'app.run(debug=True' in contenido and 'licencia_bloqueada' not in contenido:
            contenido = contenido.replace('app.run(debug=True', codigo_rutas + '\napp.run(debug=True')
            print("✅ Rutas y decorador agregados")
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return True
        
    except Exception as e:
        print(f"❌ Error modificando app.py: {e}")
        return False

def main():
    print("="*70)
    print("  INSTALADOR DEL SISTEMA DE LICENCIAS - Versión Web")
    print("="*70)
    
    # Verificar archivos
    print("\n1️⃣ Verificando archivos...")
    if not os.path.exists('app.py'):
        print("❌ No se encontró app.py")
        return
    if not os.path.exists('verificador_licencias_web.py'):
        print("❌ No se encontró verificador_licencias_web.py")
        return
    if not os.path.exists('templates'):
        print("❌ No existe la carpeta templates/")
        return
    print("✅ Archivos encontrados")
    
    # Backup
    print("\n2️⃣ Creando backup...")
    backup = crear_backup()
    
    # Crear template
    print("\n3️⃣ Creando template HTML...")
    if not crear_template_html():
        print("❌ Error creando template")
        return
    
    # Modificar app.py
    print("\n4️⃣ Modificando app.py...")
    if modificar_app_py():
        print("\n" + "="*70)
        print("✅ INSTALACIÓN COMPLETADA")
        print("="*70)
        print("\n📋 ARCHIVOS CREADOS:")
        print("   - templates/licencia_bloqueada.html")
        print("\n📝 PRÓXIMOS PASOS:")
        print("   1. Editar verificador_licencias_web.py (URL y contacto)")
        print("   2. Probar: python app.py")
        print("   3. Abrir navegador y probar bloqueo")
        print("="*70 + "\n")
    else:
        print("\n❌ Error en instalación")

if __name__ == '__main__':
    main()