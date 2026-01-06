# estadisticas.py
from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import calendar
from functools import wraps

# Crear blueprint para estadísticas
estadisticas_bp = Blueprint('estadisticas', __name__)

# Decorador personalizado para verificar sesión (compatible con tu app.py)
def login_required(f):
    """Decorador personalizado para verificar sesión"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_estadisticas(db, Factura, DetalleFactura, Producto):
    """
    Inicializar el blueprint con las dependencias necesarias
    
    Args:
        db: Instancia de SQLAlchemy
        Factura: Modelo de Factura
        DetalleFactura: Modelo de DetalleFactura  
        Producto: Modelo de Producto
    """
    
    @estadisticas_bp.route('/api/estadisticas_ventas')
    def estadisticas_ventas():
        try:
            # Obtener parámetros
            ano = request.args.get('ano', datetime.now().year, type=int)
            
            # Consulta para ventas por mes del año especificado
            ventas_mensuales = db.session.query(
                extract('month', Factura.fecha).label('mes'),
                func.count(Factura.id).label('cantidad_ventas'),
                func.sum(Factura.total).label('total_ventas'),
                func.avg(Factura.total).label('promedio_venta')
            ).filter(
                extract('year', Factura.fecha) == ano,
                Factura.estado != 'cancelada'
            ).group_by(
                extract('month', Factura.fecha)
            ).order_by('mes').all()
            
            # Crear estructura de datos completa (todos los 12 meses)
            datos_mensuales = []
            ventas_dict = {v.mes: v for v in ventas_mensuales}
            
            for mes in range(1, 13):
                venta_mes = ventas_dict.get(mes)
                datos_mensuales.append({
                    'mes': mes,
                    'nombre_mes': calendar.month_name[mes],
                    'nombre_corto': calendar.month_abbr[mes],
                    'cantidad_ventas': int(venta_mes.cantidad_ventas) if venta_mes else 0,
                    'total_ventas': float(venta_mes.total_ventas) if venta_mes else 0.0,
                    'promedio_venta': float(venta_mes.promedio_venta) if venta_mes else 0.0
                })
            
            # Estadísticas generales del año
            total_ano = sum(m['total_ventas'] for m in datos_mensuales)
            total_ventas_ano = sum(m['cantidad_ventas'] for m in datos_mensuales)
            promedio_mensual = total_ano / 12 if total_ano > 0 else 0
            
            # Mes con mayores ventas
            mes_mayor = max(datos_mensuales, key=lambda x: x['total_ventas'])
            mes_menor = min(datos_mensuales, key=lambda x: x['total_ventas'])
            
            # Comparación con año anterior
            ano_anterior = ano - 1
            total_ano_anterior = db.session.query(
                func.sum(Factura.total)
            ).filter(
                extract('year', Factura.fecha) == ano_anterior,
                Factura.estado != 'cancelada'
            ).scalar() or 0
            
            crecimiento = 0
            if total_ano_anterior > 0:
                crecimiento = ((total_ano - total_ano_anterior) / total_ano_anterior) * 100
            
            return jsonify({
                'success': True,
                'ano': ano,
                'datos_mensuales': datos_mensuales,
                'resumen': {
                    'total_ventas_ano': total_ventas_ano,
                    'total_dinero_ano': round(total_ano, 2),
                    'promedio_mensual': round(promedio_mensual, 2),
                    'mes_mayor': {
                        'mes': mes_mayor['nombre_mes'],
                        'total': mes_mayor['total_ventas']
                    },
                    'mes_menor': {
                        'mes': mes_menor['nombre_mes'],
                        'total': mes_menor['total_ventas']
                    },
                    'crecimiento_anual': round(crecimiento, 1),
                    'total_ano_anterior': round(total_ano_anterior, 2)
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @estadisticas_bp.route('/api/comparacion_anos')
    def comparacion_anos():
        try:
            anos = request.args.getlist('anos', type=int)
            if not anos:
                # Por defecto: año actual y anterior
                ano_actual = datetime.now().year
                anos = [ano_actual - 1, ano_actual]
            
            datos_comparacion = []
            
            for ano in anos:
                ventas_ano = db.session.query(
                    extract('month', Factura.fecha).label('mes'),
                    func.sum(Factura.total).label('total')
                ).filter(
                    extract('year', Factura.fecha) == ano,
                    Factura.estado != 'cancelada'
                ).group_by(
                    extract('month', Factura.fecha)
                ).all()
                
                # Crear array con todos los meses
                ventas_mensuales = [0] * 12
                for venta in ventas_ano:
                    ventas_mensuales[venta.mes - 1] = float(venta.total)
                
                datos_comparacion.append({
                    'ano': ano,
                    'ventas_mensuales': ventas_mensuales,
                    'total_ano': sum(ventas_mensuales)
                })
            
            return jsonify({
                'success': True,
                'datos': datos_comparacion,
                'meses': [calendar.month_abbr[i] for i in range(1, 13)]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @estadisticas_bp.route('/api/top_productos_mes')
    def top_productos_mes():
        try:
            mes = request.args.get('mes', type=int)
            ano = request.args.get('ano', type=int)
            limite = request.args.get('limite', 10, type=int)
            
            nombres_meses = [
                '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ]
            
            # Consulta usando SQLAlchemy en lugar de SQL crudo
            top_productos = db.session.query(
                Producto.codigo,
                Producto.nombre,
                func.sum(DetalleFactura.cantidad).label('cantidad_vendida'),
                func.sum(DetalleFactura.cantidad * DetalleFactura.precio_unitario).label('total_vendido')
            ).join(
                DetalleFactura, Producto.id == DetalleFactura.producto_id
            ).join(
                Factura, DetalleFactura.factura_id == Factura.id
            ).filter(
                extract('month', Factura.fecha) == mes,
                extract('year', Factura.fecha) == ano,
                Factura.estado == 'autorizada'
            ).group_by(
                Producto.id, Producto.codigo, Producto.nombre
            ).order_by(
                func.sum(DetalleFactura.cantidad).desc()
            ).limit(limite).all()
            
            productos = []
            for producto in top_productos:
                productos.append({
                    'codigo': producto.codigo,
                    'nombre': producto.nombre,
                    'cantidad_vendida': int(producto.cantidad_vendida),
                    'total_vendido': float(producto.total_vendido)
                })
            
            return jsonify({
                'success': True,
                'productos': productos,
                'nombre_mes': nombres_meses[mes] if 1 <= mes <= 12 else f'Mes {mes}'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @estadisticas_bp.route('/api/ventas_diarias')
    def ventas_diarias():
        """Estadísticas de ventas por día (últimos 30 días)"""
        try:
            dias = request.args.get('dias', 30, type=int)
            fecha_inicio = datetime.now() - timedelta(days=dias-1)
            
            ventas_diarias = db.session.query(
                func.date(Factura.fecha).label('fecha'),
                func.count(Factura.id).label('cantidad_ventas'),
                func.sum(Factura.total).label('total_ventas')
            ).filter(
                Factura.fecha >= fecha_inicio,
                Factura.estado != 'cancelada'
            ).group_by(
                func.date(Factura.fecha)
            ).order_by('fecha').all()
            
            # Crear estructura completa de días
            datos_diarios = []
            ventas_dict = {str(v.fecha): v for v in ventas_diarias}
            
            for i in range(dias):
                fecha = (fecha_inicio + timedelta(days=i)).date()
                fecha_str = str(fecha)
                venta_dia = ventas_dict.get(fecha_str)
                
                datos_diarios.append({
                    'fecha': fecha_str,
                    'fecha_formateada': fecha.strftime('%d/%m'),
                    'dia_semana': fecha.strftime('%A'),
                    'cantidad_ventas': int(venta_dia.cantidad_ventas) if venta_dia else 0,
                    'total_ventas': float(venta_dia.total_ventas) if venta_dia else 0.0
                })
            
            return jsonify({
                'success': True,
                'datos_diarios': datos_diarios,
                'periodo': f'Últimos {dias} días'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @estadisticas_bp.route('/api/resumen_dashboard')
    def resumen_dashboard():
        """Resumen general para el dashboard"""
        try:
            # Ventas de hoy
            hoy = datetime.now().date()
            ventas_hoy = db.session.query(
                func.count(Factura.id).label('cantidad'),
                func.sum(Factura.total).label('total')
            ).filter(
                func.date(Factura.fecha) == hoy,
                Factura.estado != 'cancelada'
            ).first()
            
            # Ventas del mes actual
            mes_actual = datetime.now().month
            ano_actual = datetime.now().year
            ventas_mes = db.session.query(
                func.count(Factura.id).label('cantidad'),
                func.sum(Factura.total).label('total')
            ).filter(
                extract('month', Factura.fecha) == mes_actual,
                extract('year', Factura.fecha) == ano_actual,
                Factura.estado != 'cancelada'
            ).first()
            
            # Top 5 productos del mes
            top_productos = db.session.query(
                Producto.nombre,
                func.sum(DetalleFactura.cantidad).label('cantidad_vendida')
            ).join(
                DetalleFactura, Producto.id == DetalleFactura.producto_id
            ).join(
                Factura, DetalleFactura.factura_id == Factura.id
            ).filter(
                extract('month', Factura.fecha) == mes_actual,
                extract('year', Factura.fecha) == ano_actual,
                Factura.estado != 'cancelada'
            ).group_by(
                Producto.id, Producto.nombre
            ).order_by(
                func.sum(DetalleFactura.cantidad).desc()
            ).limit(5).all()
            
            return jsonify({
                'success': True,
                'ventas_hoy': {
                    'cantidad': int(ventas_hoy.cantidad) if ventas_hoy.cantidad else 0,
                    'total': float(ventas_hoy.total) if ventas_hoy.total else 0.0
                },
                'ventas_mes': {
                    'cantidad': int(ventas_mes.cantidad) if ventas_mes.cantidad else 0,
                    'total': float(ventas_mes.total) if ventas_mes.total else 0.0
                },
                'top_productos': [
                    {
                        'nombre': p.nombre,
                        'cantidad': float(p.cantidad_vendida)
                    } for p in top_productos
                ]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @estadisticas_bp.route('/api/reporte_medios_pago_completo')
    def reporte_medios_pago_completo():
        """Reporte completo de medios de pago con estadísticas detalladas"""
        try:
            fecha_desde = request.args.get('desde')
            fecha_hasta = request.args.get('hasta')
            
            if not fecha_desde or not fecha_hasta:
                return jsonify({
                    'success': False,
                    'error': 'Debe proporcionar fechas desde y hasta'
                }), 400
            
            # Convertir strings a datetime
            try:
                desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
                hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
            
            # IMPORTAR MedioPago dinámicamente desde el contexto
            from flask import current_app
            MedioPago = current_app.config.get('MEDIO_PAGO_MODEL')
            
            # Si no está configurado, intentar importar directamente
            if not MedioPago:
                try:
                    from app import MedioPago
                except ImportError:
                    return jsonify({
                        'success': False,
                        'error': 'Modelo MedioPago no disponible'
                    }), 500
            
            # 1. ESTADÍSTICAS GENERALES
            estadisticas_generales = db.session.query(
                func.count(Factura.id).label('cantidad_tickets'),
                func.sum(Factura.total).label('total_general'),
                func.sum(Factura.subtotal).label('total_neto'),
                func.sum(Factura.iva).label('total_iva'),
                func.avg(Factura.total).label('ticket_promedio')
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).first()
            
            # 2. IVA DISCRIMINADO POR ALÍCUOTA
            iva_discriminado = db.session.query(
                DetalleFactura.porcentaje_iva.label('alicuota'),
                func.sum(DetalleFactura.importe_iva).label('total_iva')
            ).join(
                Factura, DetalleFactura.factura_id == Factura.id
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).group_by(
                DetalleFactura.porcentaje_iva
            ).order_by(
                DetalleFactura.porcentaje_iva
            ).all()
            
            # 3. MEDIOS DE PAGO
            medios_pago = db.session.query(
                MedioPago.medio_pago,
                func.count(MedioPago.id).label('cantidad'),
                func.sum(MedioPago.importe).label('total')
            ).join(
                Factura, MedioPago.factura_id == Factura.id
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).group_by(
                MedioPago.medio_pago
            ).order_by(
                func.sum(MedioPago.importe).desc()
            ).all()
            
            # Formatear IVA discriminado
            iva_detalle = []
            for iva in iva_discriminado:
                if iva.alicuota and iva.total_iva:
                    iva_detalle.append({
                        'alicuota': float(iva.alicuota),
                        'total': round(float(iva.total_iva), 2)
                    })
            
            # Formatear medios de pago
            medios_pago_lista = []
            for medio in medios_pago:
                medios_pago_lista.append({
                    'medio_pago': medio.medio_pago,
                    'cantidad': int(medio.cantidad),
                    'total': round(float(medio.total), 2),
                    'porcentaje': 0
                })
            
            # Calcular porcentajes
            total_general = float(estadisticas_generales.total_general or 0)
            if total_general > 0:
                for medio in medios_pago_lista:
                    medio['porcentaje'] = round((medio['total'] / total_general) * 100, 1)
            
            # Preparar respuesta
            return jsonify({
                'success': True,
                'periodo': {
                    'desde': fecha_desde,
                    'hasta': fecha_hasta,
                    'desde_formateado': desde_dt.strftime('%d/%m/%Y'),
                    'hasta_formateado': hasta_dt.strftime('%d/%m/%Y')
                },
                'estadisticas': {
                    'cantidad_tickets': int(estadisticas_generales.cantidad_tickets or 0),
                    'total_general': round(total_general, 2),
                    'total_neto': round(float(estadisticas_generales.total_neto or 0), 2),
                    'total_iva': round(float(estadisticas_generales.total_iva or 0), 2),
                    'ticket_promedio': round(float(estadisticas_generales.ticket_promedio or 0), 2)
                },
                'iva_discriminado': iva_detalle,
                'medios_pago': medios_pago_lista
            })
            
        except Exception as e:
            import traceback
            print(f"❌ Error en reporte_medios_pago_completo: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }), 500
    
    @estadisticas_bp.route('/api/estadisticas_periodo')
    def estadisticas_periodo():
        """Estadísticas resumidas para cualquier período"""
        try:
            fecha_desde = request.args.get('desde')
            fecha_hasta = request.args.get('hasta')
            
            if not fecha_desde or not fecha_hasta:
                return jsonify({
                    'success': False,
                    'error': 'Debe proporcionar fechas desde y hasta'
                }), 400
            
            desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            
            # Consulta rápida
            stats = db.session.query(
                func.count(Factura.id).label('tickets'),
                func.sum(Factura.total).label('total'),
                func.sum(Factura.subtotal).label('neto'),
                func.sum(Factura.iva).label('iva'),
                func.avg(Factura.total).label('promedio')
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).first()
            
            return jsonify({
                'success': True,
                'tickets': int(stats.tickets or 0),
                'total': round(float(stats.total or 0), 2),
                'neto': round(float(stats.neto or 0), 2),
                'iva': round(float(stats.iva or 0), 2),
                'promedio': round(float(stats.promedio or 0), 2)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @estadisticas_bp.route('/estadisticas/imprimir_estadisticas')
    @login_required
    def imprimir_estadisticas():
        """Genera vista para imprimir/exportar a PDF las estadísticas"""
        try:
            fecha_desde = request.args.get('desde')
            fecha_hasta = request.args.get('hasta')
            
            if not fecha_desde or not fecha_hasta:
                return "<h3>Error: Debe especificar rango de fechas</h3>", 400
            
            # Convertir fechas
            desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            
            # Importar MedioPago
            from flask import current_app
            MedioPago = current_app.config.get('MEDIO_PAGO_MODEL')
            if not MedioPago:
                from app import MedioPago
            
            # 1. ESTADÍSTICAS GENERALES
            estadisticas_generales = db.session.query(
                func.count(Factura.id).label('cantidad_tickets'),
                func.sum(Factura.total).label('total_general'),
                func.sum(Factura.subtotal).label('total_neto'),
                func.sum(Factura.iva).label('total_iva'),
                func.avg(Factura.total).label('ticket_promedio')
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).first()
            
            # 2. MEDIOS DE PAGO
            medios_pago = db.session.query(
                MedioPago.medio_pago,
                func.count(MedioPago.id).label('cantidad'),
                func.sum(MedioPago.importe).label('total')
            ).join(
                Factura, MedioPago.factura_id == Factura.id
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).group_by(
                MedioPago.medio_pago
            ).order_by(
                func.sum(MedioPago.importe).desc()
            ).all()
            
            # 3. IVA DISCRIMINADO
            iva_discriminado = db.session.query(
                DetalleFactura.porcentaje_iva.label('alicuota'),
                func.sum(DetalleFactura.importe_iva).label('total_iva')
            ).join(
                Factura, DetalleFactura.factura_id == Factura.id
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).group_by(
                DetalleFactura.porcentaje_iva
            ).order_by(
                DetalleFactura.porcentaje_iva
            ).all()
            
            # 4. TOP 10 PRODUCTOS
            top_productos = db.session.query(
                Producto.codigo,
                Producto.nombre,
                func.sum(DetalleFactura.cantidad).label('cantidad_vendida'),
                func.sum(DetalleFactura.subtotal).label('total_vendido')
            ).join(
                DetalleFactura, Producto.id == DetalleFactura.producto_id
            ).join(
                Factura, DetalleFactura.factura_id == Factura.id
            ).filter(
                Factura.fecha >= desde_dt,
                Factura.fecha <= hasta_dt,
                Factura.estado != 'cancelada'
            ).group_by(
                Producto.id, Producto.codigo, Producto.nombre
            ).order_by(
                func.sum(DetalleFactura.cantidad).desc()
            ).limit(10).all()
            
            # Formatear datos
            total_general = float(estadisticas_generales.total_general or 0)
            
            medios_pago_lista = []
            for medio in medios_pago:
                medios_pago_lista.append({
                    'medio': medio.medio_pago,
                    'cantidad': int(medio.cantidad),
                    'total': float(medio.total),
                    'porcentaje': round((float(medio.total) / total_general * 100), 1) if total_general > 0 else 0
                })
            
            iva_lista = []
            for iva in iva_discriminado:
                if iva.alicuota and iva.total_iva:
                    iva_lista.append({
                        'alicuota': float(iva.alicuota),
                        'total': float(iva.total_iva)
                    })
            
            productos_lista = []
            for prod in top_productos:
                productos_lista.append({
                    'codigo': prod.codigo,
                    'nombre': prod.nombre,
                    'cantidad': float(prod.cantidad_vendida),
                    'total': float(prod.total_vendido)
                })
            
            # Generar HTML
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Reporte de Estadísticas - {fecha_desde} al {fecha_hasta}</title>
                <style>
                    @media print {{
                        @page {{ margin: 1cm; }}
                        body {{ margin: 0; }}
                    }}
                    
                    body {{
                        font-family: 'Arial', sans-serif;
                        margin: 20px;
                        color: #333;
                        background: #f5f5f5;
                    }}
                    
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background: white;
                        padding: 30px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                    
                    h1 {{
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }}
                    
                    .header {{
                        margin-bottom: 30px;
                    }}
                    
                    .header-row {{
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 15px;
                        padding: 15px;
                        background: #ecf0f1;
                        border-radius: 5px;
                    }}
                    
                    .header-item {{
                        text-align: center;
                        flex: 1;
                    }}
                    
                    .header-label {{
                        font-size: 12px;
                        color: #7f8c8d;
                        text-transform: uppercase;
                    }}
                    
                    .header-value {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin-top: 5px;
                    }}
                    
                    .section {{
                        margin-bottom: 30px;
                        page-break-inside: avoid;
                    }}
                    
                    h2 {{
                        color: #34495e;
                        background: #3498db;
                        color: white;
                        padding: 10px 15px;
                        border-radius: 5px;
                        margin-bottom: 15px;
                    }}
                    
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    
                    th {{
                        background: #34495e;
                        color: white;
                        padding: 12px;
                        text-align: left;
                        font-weight: bold;
                    }}
                    
                    td {{
                        padding: 10px 12px;
                        border-bottom: 1px solid #ecf0f1;
                    }}
                    
                    tr:hover {{
                        background: #f8f9fa;
                    }}
                    
                    .text-right {{
                        text-align: right;
                    }}
                    
                    .text-center {{
                        text-align: center;
                    }}
                    
                    .total-row {{
                        font-weight: bold;
                        background: #f1c40f !important;
                        color: #2c3e50;
                    }}
                    
                    .footer {{
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 2px solid #bdc3c7;
                        text-align: center;
                        color: #7f8c8d;
                        font-size: 12px;
                    }}
                    
                    .print-button {{
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #27ae60;
                        color: white;
                        padding: 15px 30px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                        z-index: 1000;
                    }}
                    
                    .print-button:hover {{
                        background: #229954;
                    }}
                    
                    @media print {{
                        .print-button {{
                            display: none;
                        }}
                        body {{
                            background: white;
                        }}
                        .container {{
                            box-shadow: none;
                        }}
                    }}
                    
                    .badge {{
                        display: inline-block;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 12px;
                        font-weight: bold;
                    }}
                    
                    .badge-efectivo {{ background: #2ecc71; color: white; }}
                    .badge-credito {{ background: #3498db; color: white; }}
                    .badge-debito {{ background: #9b59b6; color: white; }}
                    .badge-mercado_pago {{ background: #f1c40f; color: #2c3e50; }}
                </style>
            </head>
            <body>
                <button class="print-button" onclick="window.print()">🖨️ Imprimir / Guardar PDF</button>
                
                <div class="container">
                    <h1>📊 Reporte de Estadísticas de Ventas</h1>
                    
                    <div class="header">
                        <!-- Primera fila: Período y Total Ventas -->
                        <div class="header-row">
                            <div class="header-item">
                                <div class="header-label">Período</div>
                                <div class="header-value">{desde_dt.strftime('%d/%m/%Y')} - {hasta_dt.strftime('%d/%m/%Y')}</div>
                            </div>
                            <div class="header-item">
                                <div class="header-label">Total Ventas</div>
                                <div class="header-value">${total_general:,.2f}</div>
                            </div>
                        </div>
                        
                        <!-- Segunda fila: Total Tickets y Ticket Promedio -->
                        <div class="header-row">
                            <div class="header-item">
                                <div class="header-label">Total Tickets</div>
                                <div class="header-value">{int(estadisticas_generales.cantidad_tickets or 0)}</div>
                            </div>
                            <div class="header-item">
                                <div class="header-label">Ticket Promedio</div>
                                <div class="header-value">${float(estadisticas_generales.ticket_promedio or 0):,.2f}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- MEDIOS DE PAGO -->
                    <div class="section">
                        <h2>💳 Medios de Pago</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Medio de Pago</th>
                                    <th class="text-center">Cantidad</th>
                                    <th class="text-right">Total</th>
                                    <th class="text-right">Porcentaje</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            
            for medio in medios_pago_lista:
                badge_class = f"badge badge-{medio['medio']}"
                html += f"""
                                <tr>
                                    <td><span class="{badge_class}">{medio['medio'].upper()}</span></td>
                                    <td class="text-center">{medio['cantidad']}</td>
                                    <td class="text-right">${medio['total']:,.2f}</td>
                                    <td class="text-right">{medio['porcentaje']}%</td>
                                </tr>
                """
            
            html += f"""
                                <tr class="total-row">
                                    <td><strong>TOTAL</strong></td>
                                    <td class="text-center"><strong>{sum(m['cantidad'] for m in medios_pago_lista)}</strong></td>
                                    <td class="text-right"><strong>${total_general:,.2f}</strong></td>
                                    <td class="text-right"><strong>100%</strong></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- IVA DISCRIMINADO -->
                    <div class="section">
                        <h2>📋 IVA Discriminado</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Alícuota</th>
                                    <th class="text-right">Total IVA</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            
            total_iva = 0
            for iva in iva_lista:
                total_iva += iva['total']
                html += f"""
                                <tr>
                                    <td>IVA {iva['alicuota']}%</td>
                                    <td class="text-right">${iva['total']:,.2f}</td>
                                </tr>
                """
            
            html += f"""
                                <tr class="total-row">
                                    <td><strong>TOTAL IVA</strong></td>
                                    <td class="text-right"><strong>${total_iva:,.2f}</strong></td>
                                </tr>
                                <tr>
                                    <td><strong>NETO (sin IVA)</strong></td>
                                    <td class="text-right"><strong>${float(estadisticas_generales.total_neto or 0):,.2f}</strong></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- TOP 10 PRODUCTOS -->
                    <div class="section">
                        <h2>🏆 Top 10 Productos Más Vendidos</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Código</th>
                                    <th>Producto</th>
                                    <th class="text-right">Cantidad</th>
                                    <th class="text-right">Total Vendido</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            
            for i, prod in enumerate(productos_lista, 1):
                html += f"""
                                <tr>
                                    <td><strong>#{i}</strong> {prod['codigo']}</td>
                                    <td>{prod['nombre']}</td>
                                    <td class="text-right">{prod['cantidad']:,.0f}</td>
                                    <td class="text-right">${prod['total']:,.2f}</td>
                                </tr>
                """
            
            html += f"""
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Reporte generado el:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                        <p>Sistema de Punto de Venta - FactuFacil</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return f"""
            <h3>Error generando reporte</h3>
            <p>{str(e)}</p>
            <pre>{error_detail}</pre>
            """, 500

    return estadisticas_bp