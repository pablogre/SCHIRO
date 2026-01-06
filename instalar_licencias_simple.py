# instalar_licencias_simple.py - Instalador automático (versión simple)

"""
Instalador del sistema de licencias (versión simple con JSON)
Modifica app.py automáticamente
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

def modificar_app_py():
    """Modifica app.py para agregar verificación de licencias"""
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # 1. Agregar imports (después de "from caja import init_caja_system")
        codigo_imports = """
# ================ SISTEMA DE VERIFICACIÓN DE LICENCIAS ================
from verificador_licencias_simple import verificar_licencia
import sys
"""
        
        if 'from caja import init_caja_system' in contenido and 'verificador_licencias_simple' not in contenido:
            contenido = contenido.replace(
                'from caja import init_caja_system',
                'from caja import init_caja_system' + codigo_imports
            )
            print("✅ Imports agregados")
        else:
            print("⚠️ Imports ya existen o no se encontró la línea de inserción")
        
        # 2. Agregar verificación (después de "ARCA_CONFIG = DefaultARCAConfig()")
        codigo_verificacion = """

# ================ VERIFICACIÓN DE LICENCIA AL INICIO ================
print(f"\\n{'='*60}")
print(f"🔐 VERIFICANDO LICENCIA DEL SISTEMA")
print(f"{'='*60}")

# Obtener CUIT desde la configuración
CUIT_SISTEMA = ARCA_CONFIG.CUIT
print(f"CUIT: {CUIT_SISTEMA}")

# Verificar licencia
resultado_licencia = verificar_licencia(CUIT_SISTEMA)

# Evaluar resultado
if not resultado_licencia['valida']:
    # Sistema bloqueado
    print(f"\\n{resultado_licencia['mensaje']}")
    print(f"\\n{'='*60}\\n")
    input("Presione ENTER para salir...")
    sys.exit(1)

elif resultado_licencia['mora']:
    # En mora - mostrar advertencia pero permitir uso
    print(f"\\n⚠️ ADVERTENCIA:")
    print(resultado_licencia['mensaje'])
    print(f"\\n{'='*60}\\n")

else:
    # Todo OK
    print(f"✅ {resultado_licencia['mensaje']}")
    print(f"{'='*60}\\n")

# Guardar info de licencia para usar en templates
app.config['LICENCIA_INFO'] = resultado_licencia
"""
        
        if 'ARCA_CONFIG = DefaultARCAConfig()' in contenido and 'VERIFICACIÓN DE LICENCIA AL INICIO' not in contenido:
            contenido = contenido.replace(
                'ARCA_CONFIG = DefaultARCAConfig()',
                'ARCA_CONFIG = DefaultARCAConfig()' + codigo_verificacion
            )
            print("✅ Verificación de licencia agregada")
        else:
            print("⚠️ Verificación ya existe o no se encontró la línea de inserción")
        
        # 3. Agregar ruta de verificación manual (antes de app.run())
        codigo_ruta = """
@app.route('/verificar_licencia')
def verificar_licencia_manual():
    '''Verificar estado de licencia manualmente (solo admin)'''
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Solo admin
    usuario = Usuario.query.get(session['user_id'])
    if usuario.rol != 'admin':
        flash('No tiene permisos para ver esta información', 'error')
        return redirect(url_for('index'))
    
    try:
        resultado = verificar_licencia(ARCA_CONFIG.CUIT)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

"""
        
        if 'app.run(debug=True' in contenido and 'verificar_licencia_manual' not in contenido:
            contenido = contenido.replace(
                'app.run(debug=True',
                codigo_ruta + '\napp.run(debug=True'
            )
            print("✅ Ruta de verificación agregada")
        else:
            print("⚠️ Ruta ya existe o no se encontró app.run()")
        
        # Guardar cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return True
        
    except Exception as e:
        print(f"❌ Error modificando app.py: {e}")
        return False

def main():
    print("="*70)
    print("  INSTALADOR DEL SISTEMA DE LICENCIAS (Versión Simple)")
    print("="*70)
    
    # Verificar archivos
    print("\n1️⃣ Verificando archivos...")
    
    if not os.path.exists('app.py'):
        print("❌ No se encontró app.py en el directorio actual")
        return
    
    if not os.path.exists('verificador_licencias_simple.py'):
        print("❌ No se encontró verificador_licencias_simple.py")
        return
    
    print("✅ Archivos encontrados")
    
    # Crear backup
    print("\n2️⃣ Creando backup...")
    backup = crear_backup()
    
    if not backup:
        respuesta = input("¿Continuar sin backup? (s/N): ")
        if respuesta.lower() != 's':
            print("Instalación cancelada")
            return
    
    # Modificar app.py
    print("\n3️⃣ Modificando app.py...")
    
    if modificar_app_py():
        print("\n" + "="*70)
        print("✅ INSTALACIÓN COMPLETADA")
        print("="*70)
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("-"*70)
        print("1. Editar verificador_licencias_simple.py:")
        print("   - Cambiar URL_LICENCIAS a tu URL real")
        print("   - Configurar tus datos de contacto")
        print()
        print("2. Subir el archivo licencias.json a tu servidor:")
        print("   - Ubicación: https://pablore.com.ar/licencias/licencias.json")
        print("   - O la URL que hayas configurado")
        print()
        print("3. Agregar tus clientes al archivo licencias.json")
        print()
        print("4. Probar: python verificador_licencias_simple.py")
        print()
        print("5. Iniciar FactuFacil: python app.py")
        print("-"*70)
        
        print("\n💡 MODO PRUEBA:")
        print("   Para probar sin bloquear, edita verificador_licencias_simple.py")
        print("   y cambia: MODO_PRUEBA = True")
        print("="*70 + "\n")
        
    else:
        print("\n❌ Error en la instalación")
        if backup:
            print(f"Puede restaurar el backup: {backup}")

if __name__ == '__main__':
    main()