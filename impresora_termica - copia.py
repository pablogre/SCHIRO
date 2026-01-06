import os
import platform
from datetime import datetime
import win32print
import win32api
import tempfile
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImpresoraTermica:
    def __init__(self, nombre_impresora=None, ancho_mm=80):
        # Para impresoras térmicas de 80mm, el ancho típico es 42-48 caracteres
        if ancho_mm == 80:
            self.ancho = 42  # Caracteres por línea para 80mm
        elif ancho_mm == 58:
            self.ancho = 32  # Caracteres por línea para 58mm
        else:
            self.ancho = ancho_mm  # Si se especifica directamente
            
        self.ancho_mm = ancho_mm
        self.nombre_impresora = nombre_impresora or self._buscar_impresora_termica()
        
        print(f"🖨️ Configuración: {ancho_mm}mm = {self.ancho} caracteres por línea")

    def _buscar_impresora_termica(self):
        """Buscar impresora térmica automáticamente - EPSON TM-m30II prioritaria"""
        try:
            impresoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            
            # ORDEN DE PRIORIDAD: EPSON TM-m30II PRIMERO
            nombres_termicas_prioritarios = [
                'EPSON TM-m30II Receipt',
                'epson tm-m30ii receipt',
                'tm-m30ii receipt',
                'EPSON TM-T20II Receipt5', 
                'TMT20',
            ]
            
            # Buscar EPSON TM-m30II primero (prioritario)
            for impresora in impresoras:
                nombre = impresora[2].lower()
                for prioritario in nombres_termicas_prioritarios:
                    if prioritario.lower() in nombre:
                        print(f"🖨️ ✅ EPSON detectada: {impresora[2]}")
                        print(f"🎯 Esta impresora térmica profesional será usada")
                        return impresora[2]
            
            # Si no encuentra EPSON, buscar otras térmicas
            nombres_termicas_secundarios = [
                'tm-t(203dpi)',
                'tm-t20',
                'pos-58', 'pos58',
                'tm-m30ii', 'tm-m30', 'epson tm-m30',
                'thermal', 'receipt', 'pos', 'tm-', 'rp-', 'sp-',
                'termica', 'ticket', 'epson', 'star', 'citizen',
                'xprinter', 'godex', 'zebra', 'bixolon'
            ]
            
            for impresora in impresoras:
                nombre = impresora[2].lower()
                for termico in nombres_termicas_secundarios:
                    if termico in nombre:
                        print(f"🖨️ ⚠️ Impresora térmica secundaria detectada: {impresora[2]}")
                        print(f"💡 Recomendación: Usar EPSON TM-m30II si está disponible")
                        return impresora[2]
            
            # Si no encuentra térmica, usar impresora por defecto
            try:
                impresora_default = win32print.GetDefaultPrinter()
                print(f"🖨️ 📄 Usando impresora por defecto: {impresora_default}")
                print(f"⚠️ Esta puede no ser una impresora térmica")
                return impresora_default
            except:
                print("❌ No se pudo obtener impresora por defecto")
                return None
            
        except Exception as e:
            print(f"❌ Error detectando impresora: {e}")
            return None
            
    def centrar_texto(self, texto, ancho=None):
        """Centrar texto en el ancho especificado"""
        ancho = ancho or self.ancho
        if len(texto) >= ancho:
            return texto[:ancho]
        espacios = (ancho - len(texto)) // 2
        return " " * espacios + texto
    
    def justificar_texto(self, izquierda, derecha, ancho=None):
        """Justificar texto a izquierda y derecha"""
        ancho = ancho or self.ancho
        espacios_necesarios = ancho - len(izquierda) - len(derecha)
        if espacios_necesarios <= 0:
            return (izquierda + derecha)[:ancho]
        return izquierda + " " * espacios_necesarios + derecha
    
    def linea_separadora(self, caracter="-", ancho=None):
        """Crear línea separadora"""
        ancho = ancho or self.ancho
        return caracter * ancho
    
    def truncar_texto(self, texto, max_chars):
        """Truncar texto si es muy largo"""
        if len(texto) <= max_chars:
            return texto
        return texto[:max_chars-3] + "..."

    def formatear_factura_termica(self, factura):
        """Formatear factura para impresión térmica de 80mm"""
        lineas = []
        
        print("🔍 DEBUG - Iniciando formateo de factura")
        
        try:
            # ENCABEZADO
            lineas.append("")
            lineas.append("              \x1B\x45\x01\x1B\x21\x30CARNAVE\x1B\x21\x00\x1B\x45\x00")
            lineas.append("")
            lineas.append(self.centrar_texto("CUIT: 20-29261831-0"))  # Noelia'27-33342943-3'
            lineas.append(self.centrar_texto("IVA: Responsable Inscrípto"))
            lineas.append(self.centrar_texto("Dir: De la Nacion 749"))
            lineas.append(self.centrar_texto("La Esquina de Siempre"))
            lineas.append("")
            
            # TIPO DE COMPROBANTE
            tipo_cbte = self._obtener_tipo_comprobante(factura.tipo_comprobante)
            lineas.append(self.centrar_texto(f"=== {tipo_cbte} ==="))
            lineas.append(self.centrar_texto(f"Nro: {factura.numero}"))
            lineas.append("")
            
            # FECHA Y HORA
            fecha_str = factura.fecha.strftime("%d/%m/%Y %H:%M")
            lineas.append(f"Fecha: {fecha_str}")
            
            # VENDEDOR
            vendedor = "Sistema"
            if hasattr(factura, 'usuario') and factura.usuario:
                vendedor = factura.usuario.nombre
            vendedor_corto = self.truncar_texto(vendedor, 20)
            lineas.append(f"Vendedor: {vendedor_corto}")
            
            lineas.append(self.linea_separadora())
            
            # CLIENTE
            if hasattr(factura, 'cliente') and factura.cliente:
                nombre_cliente = self.truncar_texto(factura.cliente.nombre, self.ancho)
                lineas.append(f"Cliente: {nombre_cliente}")
                if hasattr(factura.cliente, 'documento') and factura.cliente.documento:
                    tipo_doc = getattr(factura.cliente, 'tipo_documento', 'DNI') or "DNI"
                    lineas.append(f"{tipo_doc}: {factura.cliente.documento}")
            else:
                lineas.append("Cliente: Consumidor Final")
            
            lineas.append(self.linea_separadora())
            
            # ENCABEZADO DE PRODUCTOS
            lineas.append("PRODUCTO         CANT  P.U    TOTAL")
            lineas.append(self.linea_separadora())
            
            # PRODUCTOS
            if hasattr(factura, 'detalles') and factura.detalles:
                for detalle in factura.detalles:
                    max_nombre = 17
                    cant_space = 5
                    precio_space = 7
                    total_space = 8
                    
                    if hasattr(detalle, 'producto') and detalle.producto:
                        nombre_producto = getattr(detalle.producto, 'nombre', 'Producto')
                    else:
                        nombre_producto = 'Producto'
                    
                    nombre = self.truncar_texto(nombre_producto, max_nombre)
                    
                    try:
                        cant_str = f"{float(detalle.cantidad):.3f}"
                        precio_str = f"{float(detalle.precio_unitario):,.2f}"
                        total_str = f"{float(detalle.subtotal):,.2f}"
                    except (ValueError, AttributeError):
                        cant_str = "1"
                        precio_str = "0"
                        total_str = "0"
                    
                    linea = f"{nombre:<{max_nombre}} {cant_str:>{cant_space}} {precio_str:>{precio_space}} {total_str:>{total_space}}"
                    lineas.append(linea[:self.ancho])
            else:
                lineas.append("Sin productos")
            
            lineas.append(self.linea_separadora())
            
            # TOTALES
            try:
                subtotal = float(getattr(factura, 'subtotal', 0))
                iva_total = float(getattr(factura, 'iva', 0))
                total = float(getattr(factura, 'total', 0))
                
                lineas.append(self.justificar_texto("SUBTOTAL:", f"${subtotal:,.2f}"))
                
                if hasattr(factura, 'detalles') and factura.detalles:
                    iva_por_alicuota = {}
                    
                    for detalle in factura.detalles:
                        if hasattr(detalle, 'porcentaje_iva') and detalle.porcentaje_iva is not None:
                            porcentaje = float(detalle.porcentaje_iva)
                        else:
                            porcentaje = float(detalle.producto.iva) if hasattr(detalle, 'producto') and detalle.producto else 21.0
                        
                        subtotal_detalle = float(detalle.subtotal)
                        iva_detalle = round((subtotal_detalle * porcentaje / 100), 2)
                        
                        if porcentaje not in iva_por_alicuota:
                            iva_por_alicuota[porcentaje] = 0
                        iva_por_alicuota[porcentaje] += iva_detalle
                    
                    for porcentaje in sorted(iva_por_alicuota.keys()):
                        importe_iva = iva_por_alicuota[porcentaje]
                        if importe_iva > 0:
                            if porcentaje == 0:
                                etiqueta = "EXENTO:"
                            else:
                                etiqueta = f"IVA {porcentaje:g}%:"
                            lineas.append(self.justificar_texto(etiqueta, f"${importe_iva:,.2f}"))
                else:
                    if iva_total > 0:
                        lineas.append(self.justificar_texto("IVA 21%:", f"${iva_total:,.2f}"))
                
                subtotal_mas_iva = subtotal + iva_total
                if total < subtotal_mas_iva:
                    descuento = subtotal_mas_iva - total
                    if descuento > 0:
                        lineas.append(self.justificar_texto("DESCUENTO:", f"-${descuento:.2f}"))
                        
                lineas.append(self.linea_separadora())
                lineas.append(self.justificar_texto("TOTAL:", f"${total:,.2f}"))
                
            except (ValueError, AttributeError):
                lineas.append(self.justificar_texto("TOTAL:", "$0.00"))
            
            lineas.append(self.linea_separadora())
            
            # INFORMACIÓN AFIP
            cae = getattr(factura, 'cae', None)
            if cae:
                lineas.append("")
                lineas.append("Transparencia Fiscal al Consumidor - Ley 27.743")
                lineas.append("")
                lineas.append(self.centrar_texto("*** AUTORIZADO AFIP ***"))
                lineas.append("")
                
                cae_texto = f"CAE: {cae}"
                if len(cae_texto) > self.ancho:
                    lineas.append("CAE:")
                    lineas.append(f"  {cae}")
                else:
                    lineas.append(cae_texto)
                    
                vto_cae = getattr(factura, 'vto_cae', None)
                if vto_cae:
                    try:
                        if hasattr(vto_cae, 'strftime'):
                            vto_str = vto_cae.strftime("%d/%m/%Y")
                        else:
                            vto_str = str(vto_cae)
                        lineas.append(f"Vto CAE: {vto_str}")
                    except Exception:
                        lineas.append(f"Vto CAE: {vto_cae}")
                
                lineas.append("")
                lineas.append(self.centrar_texto("Verificar en:"))
                lineas.append(self.centrar_texto("www.arca.gob.ar"))
                
            else:
                lineas.append("")
                lineas.append("Transparencia Fiscal al Consumidor - Ley 27.743")
                lineas.append("")
                lineas.append(self.centrar_texto("*** NO AUTORIZADO ***"))
                lineas.append(self.centrar_texto("VERIFICAR AFIP"))
            
            # PIE DE PÁGINA
            lineas.append("")
            lineas.append(self.centrar_texto("Gracias por elegirnos"))
            lineas.append("")
            lineas.append("")
            lineas.append("")
            lineas.append("")
            lineas.append("")
            lineas.append("")
            lineas.append("\x1B\x69")
            
        except Exception as e:
            print(f"❌ Error en formatear_factura_termica: {e}")
            import traceback
            traceback.print_exc()
            
            lineas = [
                "",
                self.centrar_texto("*** ERROR EN FACTURA ***"),
                "",
                f"Error: {str(e)}",
                "",
                self.centrar_texto("Contactar soporte"),
                "",
                "",
                ""
            ]
        
        return "\n".join(lineas)

    def imprimir_factura_con_qr_web(self, factura):
        """Imprimir factura y mostrar QR en navegador"""
        try:
            resultado_impresion = self.imprimir_factura(factura)
            info_qr = {'valido': False, 'mensaje': 'QR deshabilitado en impresión'}
            
            return {
                'impresion_exitosa': resultado_impresion,
                'qr_info': info_qr
            }
        except Exception as e:
            print(f"❌ Error en impresión con QR: {e}")
            return {
                'impresion_exitosa': False,
                'qr_info': {'valido': False, 'mensaje': str(e)}
            }

    def _obtener_tipo_comprobante(self, tipo):
        """Obtener descripción del tipo de comprobante"""
        tipos = {
            '01': 'FACTURA A', '1': 'FACTURA A',
            '06': 'FACTURA B', '6': 'FACTURA B',
            '11': 'FACTURA C', '11': 'FACTURA C',
            '03': 'NOTA CRED A', '3': 'NOTA CRED A',
            '08': 'NOTA CRED B', '8': 'NOTA CRED B',
            '13': 'NOTA CRED C', '13': 'NOTA CRED C'
        }
        
        tipo_str = str(tipo)
        
        if tipo_str in tipos:
            return tipos[tipo_str]
        elif tipo_str.zfill(2) in tipos:
            return tipos[tipo_str.zfill(2)]
        else:
            return f'CBTE {tipo}'

    def imprimir_factura(self, factura):
        """Imprimir factura con método RAW"""
        try:
            if not self.nombre_impresora:
                raise Exception("No se encontró impresora térmica")
            
            print(f"🖨️ INICIANDO IMPRESIÓN - Factura: {getattr(factura, 'numero', 'SIN_NUMERO')}")
            
            contenido = self.formatear_factura_termica(factura)
            print(f"📄 Contenido formateado: {len(contenido)} caracteres")
            
            hPrinter = win32print.OpenPrinter(self.nombre_impresora)
            
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, (f"Factura_{getattr(factura, 'numero', 'XXX')}", None, "RAW"))
                
                try:
                    win32print.StartPagePrinter(hPrinter)
                    
                    init_cmd = b'\x1B\x40'
                    datos_bytes = init_cmd + contenido.encode('cp850', errors='replace')
                    datos_bytes += b'\n\n\x1B\x69'
                    
                    win32print.WritePrinter(hPrinter, datos_bytes)
                    win32print.EndPagePrinter(hPrinter)
                    
                    print("✅ *** IMPRESIÓN EXITOSA ***")
                    return True
                    
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
                
        except Exception as e:
            print(f"❌ ERROR GENERAL: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_impresion(self):
        """Test de impresión con método RAW"""
        try:
            if not self.nombre_impresora:
                raise Exception("No se encontró impresora")
                
            print(f"🧪 INICIANDO TEST - Impresora: {self.nombre_impresora}")
            
            contenido_test = """
=== PRUEBA DE IMPRESION ===

Test de sistema POS
Fecha: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """

Impresora detectada:
""" + self.nombre_impresora + """

------------------------------------------
ESTADO: FUNCIONANDO CORRECTAMENTE
------------------------------------------

*** EXITO ***




"""
            
            hPrinter = win32print.OpenPrinter(self.nombre_impresora)
            
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("POS_Test", None, "RAW"))
                
                try:
                    win32print.StartPagePrinter(hPrinter)
                    
                    init_cmd = b'\x1B\x40'
                    datos_bytes = init_cmd + contenido_test.encode('cp850', errors='replace')
                    datos_bytes += b'\n\n\x1B\x69'
                    
                    win32print.WritePrinter(hPrinter, datos_bytes)
                    win32print.EndPagePrinter(hPrinter)
                    
                    print("✅ *** TEST EXITOSO ***")
                    return True
                    
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verificar_estado(self):
        """Verificar el estado de la impresora"""
        try:
            if not self.nombre_impresora:
                return {
                    'disponible': False,
                    'error': 'Impresora no detectada',
                    'nombre': None,
                    'ancho_mm': self.ancho_mm,
                    'caracteres_linea': self.ancho
                }
            
            try:
                handle = win32print.OpenPrinter(self.nombre_impresora)
                info = win32print.GetPrinter(handle, 2)
                win32print.ClosePrinter(handle)
                
                estado = info['Status']
                estado_texto = "Lista" if estado == 0 else f"Estado: {estado}"
                
                return {
                    'disponible': True,
                    'nombre': self.nombre_impresora,
                    'estado': estado_texto,
                    'ancho_mm': self.ancho_mm,
                    'caracteres_linea': self.ancho
                }
            except Exception as e:
                return {
                    'disponible': True,
                    'nombre': self.nombre_impresora,
                    'estado': 'Disponible (estado no verificable)',
                    'ancho_mm': self.ancho_mm,
                    'caracteres_linea': self.ancho,
                    'warning': str(e)
                }
                
        except Exception as e:
            logger.error(f"Error al verificar estado: {e}")
            return {
                'disponible': False,
                'error': str(e),
                'nombre': self.nombre_impresora,
                'ancho_mm': self.ancho_mm,
                'caracteres_linea': self.ancho
            }

    @staticmethod
    def listar_impresoras():
        """Listar todas las impresoras disponibles"""
        try:
            print("🖨️ Impresoras disponibles:")
            impresoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            for i, impresora in enumerate(impresoras, 1):
                print(f"   {i}. {impresora[2]}")
            
            try:
                impresoras_red = win32print.EnumPrinters(win32print.PRINTER_ENUM_NETWORK)
                if impresoras_red:
                    print("\n🌐 Impresoras de red:")
                    for i, impresora in enumerate(impresoras_red, 1):
                        print(f"   {i}. {impresora[2]}")
            except:
                pass
                
        except Exception as e:
            print(f"❌ Error listando impresoras: {e}")

    def imprimir_cartel_precio(self, producto, tiene_ofertas=False):
        """Imprimir cartel de precio individual para producto"""
        try:
            if not self.nombre_impresora:
                print("❌ Impresora no disponible para carteles")
                return False
            
            print(f"🏷️ Imprimiendo cartel para: {producto.codigo}")
            
            precio = float(producto.precio)
            nombre_corto = producto.nombre[:30] if len(producto.nombre) > 30 else producto.nombre
            
            contenido = []
            
            # contenido.append("=" * self.ancho)  # ✅ COMENTADO
            contenido.append(self.centrar_texto("PRECIO DE VENTA"))
            # contenido.append("=" * self.ancho)  # ✅ COMENTADO
            
            if tiene_ofertas:
                contenido.append("")
                contenido.append("*" * self.ancho)
                contenido.append(self.centrar_texto("¡OFERTA ESPECIAL!"))
                contenido.append("*" * self.ancho)
            
            contenido.append("")
            contenido.append(self.centrar_texto(nombre_corto))
            
            contenido.append("")
            contenido.append("-" * self.ancho)
            
            precio_texto = f"$ {precio:.2f}"
            ancho_precio = self.ancho // 2
            espacios = (ancho_precio - len(precio_texto)) // 2
            precio_centrado = " " * espacios + precio_texto
            contenido.append("\x1B\x21\x30" + precio_centrado + "\x1B\x21\x00")
            contenido.append("")
                        
            contenido.append("-" * self.ancho)
            
            # codigo_texto = f"Codigo: {producto.codigo}"
            # contenido.append(self.centrar_texto(codigo_texto))
            
            if tiene_ofertas:
                if producto.es_combo and hasattr(producto, 'calcular_ahorro_combo'):
                    ahorro = producto.calcular_ahorro_combo()
                    if ahorro > 0:
                        contenido.append("")
                        ahorro_texto = f"Ahorro: $ {ahorro:.2f}"
                        contenido.append(self.centrar_texto(ahorro_texto))
            
            contenido.append("")
            # contenido.append("=" * self.ancho)  # ✅ COMENTADO
            
            # fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            # contenido.append(self.centrar_texto(fecha_hora))
            
            # contenido.append("=" * self.ancho)  # ✅ COMENTADO
            contenido.extend([""] * 3)
            
            texto_completo = "\n".join(contenido)
            
            print("📄 Enviando cartel a impresora...")
            
            hPrinter = win32print.OpenPrinter(self.nombre_impresora)
            
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, (f"Cartel_{producto.codigo}", None, "RAW"))
                
                try:
                    win32print.StartPagePrinter(hPrinter)
                    
                    init_cmd = b'\x1B\x40'
                    datos_bytes = init_cmd + texto_completo.encode('cp850', errors='replace')
                    datos_bytes += b'\n\n\x1B\x69'
                    
                    win32print.WritePrinter(hPrinter, datos_bytes)
                    win32print.EndPagePrinter(hPrinter)
                    
                    print(f"✅ *** CARTEL IMPRESO: {producto.codigo} ***")
                    return True
                    
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            
        except Exception as e:
            print(f"❌ Error imprimiendo cartel para {producto.codigo}: {e}")
            import traceback
            traceback.print_exc()
            return False


# ============================================
# AQUÍ TERMINA LA CLASE - TODO LO DE ABAJO VA SIN INDENTACIÓN
# ============================================

# Instancia global de la impresora (80mm = 42 caracteres)
impresora_termica = ImpresoraTermica(ancho_mm=80)

# *** FUNCIONES PARA USAR EN FLASK ***
def obtener_estado_impresora():
    """Función para endpoint Flask"""
    return impresora_termica.verificar_estado()

def imprimir_factura_termica(datos_factura):
    """Función para endpoint Flask - recibe datos en formato dict"""
    try:
        class FacturaSimulada:
            def __init__(self, datos):
                self.numero = datos.get('numero', '0001-00000001')
                self.tipo_comprobante = datos.get('tipo_comprobante', '11')
                self.fecha = datetime.now()
                self.subtotal = datos.get('subtotal', 0)
                self.iva = datos.get('iva', 0)
                self.total = datos.get('total', 0)
                self.cae = datos.get('cae', None)
                self.vto_cae = datos.get('vto_cae', None)
                
                class ClienteSimulado:
                    def __init__(self, cliente_data):
                        if cliente_data:
                            self.nombre = cliente_data.get('nombre', 'Consumidor Final')
                            self.documento = cliente_data.get('documento', None)
                            self.tipo_documento = cliente_data.get('tipo_documento', 'DNI')
                        else:
                            self.nombre = 'Consumidor Final'
                            self.documento = None
                            self.tipo_documento = None
                
                self.cliente = ClienteSimulado(datos.get('cliente'))
                
                class UsuarioSimulado:
                    def __init__(self):
                        self.nombre = 'Sistema'
                
                self.usuario = UsuarioSimulado()
                
                class DetalleSimulado:
                    def __init__(self, item_data):
                        self.cantidad = item_data.get('cantidad', 1)
                        self.precio_unitario = item_data.get('precio_unitario', 0)
                        self.subtotal = item_data.get('subtotal', 0)
                        
                        class ProductoSimulado:
                            def __init__(self, item_data):
                                self.nombre = item_data.get('nombre', 'Producto')
                        
                        self.producto = ProductoSimulado(item_data)
                
                self.detalles = [DetalleSimulado(item) for item in datos.get('items', [])]
        
        factura_sim = FacturaSimulada(datos_factura)
        resultado = impresora_termica.imprimir_factura(factura_sim)
        
        if resultado:
            return {
                'success': True,
                'mensaje': f'Factura impresa correctamente en {impresora_termica.nombre_impresora}'
            }
        else:
            return {
                'success': False,
                'error': 'Error al imprimir factura'
            }
            
    except Exception as e:
        logger.error(f"Error en imprimir_factura_termica: {e}")
        return {
            'success': False,
            'error': str(e)
        }