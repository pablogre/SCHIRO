"""
Módulo de Notas de Crédito para FactuFacil
Maneja toda la lógica de NC electrónicas con AFIP
"""

from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
from functools import wraps
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_, or_, func

# Blueprint para las rutas de NC
notas_credito_bp = Blueprint('notas_credito', __name__)

# Variables globales que se inicializarán
db = None
NotaCredito = None
DetalleNotaCredito = None
Factura = None
DetalleFactura = None
Cliente = None
Producto = None
ARCA_CONFIG = None
autorizar_comprobante_afip = None


def init_notas_credito(database, nota_credito_model, detalle_nc_model, factura_model, 
                       detalle_factura_model, cliente_model, producto_model, 
                       arca_config, autorizar_func):
    """
    Inicializar el módulo con las dependencias necesarias
    
    Args:
        database: Instancia de SQLAlchemy
        nota_credito_model: Modelo NotaCredito
        detalle_nc_model: Modelo DetalleNotaCredito
        factura_model: Modelo Factura
        detalle_factura_model: Modelo DetalleFactura
        cliente_model: Modelo Cliente
        producto_model: Modelo Producto
        arca_config: Configuración de ARCA/AFIP
        autorizar_func: Función para autorizar comprobantes en AFIP
    """
    global db, NotaCredito, DetalleNotaCredito, Factura, DetalleFactura
    global Cliente, Producto, ARCA_CONFIG, autorizar_comprobante_afip
    
    db = database
    NotaCredito = nota_credito_model
    DetalleNotaCredito = detalle_nc_model
    Factura = factura_model
    DetalleFactura = detalle_factura_model
    Cliente = cliente_model
    Producto = producto_model
    ARCA_CONFIG = arca_config
    autorizar_comprobante_afip = autorizar_func
    
    return notas_credito_bp


def login_required(f):
    """Decorador para verificar autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# RUTAS DE VISTAS
# ============================================================================

@notas_credito_bp.route('/notas_credito')
@login_required
def listar_notas_credito():
    """Vista principal de Notas de Crédito"""
    return render_template('notas_credito.html')


@notas_credito_bp.route('/notas_credito/detalle/<int:nc_id>')
@login_required
def nota_credito_detalle(nc_id):
    """Vista de detalle de una nota de crédito específica"""
    return render_template('nota_credito_detalle.html', nc_id=nc_id)


# ============================================================================
# API: BÚSQUEDA Y FILTRADO
# ============================================================================

@notas_credito_bp.route('/api/notas_credito/buscar', methods=['GET'])
@login_required
def api_buscar_notas_credito():
    """API para buscar y filtrar notas de crédito"""
    try:
        # Obtener parámetros de filtro
        numero = request.args.get('numero', '').strip()
        cliente_id = request.args.get('cliente_id', '').strip()
        estado = request.args.get('estado', '').strip()
        fecha_desde = request.args.get('fecha_desde', '').strip()
        fecha_hasta = request.args.get('fecha_hasta', '').strip()
        
        # Construir query base
        query = db.session.query(NotaCredito).join(
            Cliente, NotaCredito.cliente_id == Cliente.id
        ).join(
            Factura, NotaCredito.factura_id == Factura.id
        )
        
        # Aplicar filtros
        if numero:
            query = query.filter(NotaCredito.numero.like(f'%{numero}%'))
        
        if cliente_id:
            query = query.filter(NotaCredito.cliente_id == int(cliente_id))
        
        if estado:
            if estado == 'autorizada':
                query = query.filter(NotaCredito.cae.isnot(None))
            elif estado == 'pendiente':
                query = query.filter(
                    NotaCredito.cae.is_(None),
                    NotaCredito.error_afip.is_(None)
                )
            elif estado == 'error':
                query = query.filter(NotaCredito.error_afip.isnot(None))
        
        if fecha_desde:
            query = query.filter(NotaCredito.fecha >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(NotaCredito.fecha <= fecha_hasta)
        
        # Ordenar por fecha descendente
        query = query.order_by(NotaCredito.fecha.desc())
        
        # Ejecutar query
        notas = query.all()
        
        # Formatear resultados
        resultados = []
        for nc in notas:
            resultados.append({
                'id': nc.id,
                'numero': nc.numero,
                'fecha': nc.fecha.strftime('%d/%m/%Y'),
                'cliente': nc.cliente.nombre,
                'cliente_id': nc.cliente.id,
                'factura_numero': nc.factura.numero,
                'factura_id': nc.factura.id,
                'tipo_comprobante': nc.tipo_comprobante,
                'total': float(nc.total),
                'cae': nc.cae,
                'cae_vencimiento': nc.vto_cae.strftime('%d/%m/%Y') if nc.vto_cae else None,
                'error_afip': nc.error_afip,
                'estado': 'Autorizada' if nc.cae else ('Error AFIP' if nc.error_afip else 'Pendiente')
            })
        
        return jsonify({
            'success': True,
            'notas': resultados,
            'total': len(resultados)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notas_credito_bp.route('/api/notas_credito/<int:nc_id>', methods=['GET'])
@login_required
def api_detalle_nota_credito(nc_id):
    """API para obtener el detalle completo de una nota de crédito"""
    try:
        nc = NotaCredito.query.get_or_404(nc_id)
        
        # Obtener detalles de productos
        detalles = []
        for detalle in nc.detalles:
            detalles.append({
                'producto': detalle.producto.nombre,
                'codigo': detalle.producto.codigo,
                'cantidad': float(detalle.cantidad),
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.subtotal),
                'iva': float(detalle.porcentaje_iva),
                'total': float(detalle.subtotal) + float(detalle.importe_iva)
            })
        
        resultado = {
            'id': nc.id,
            'numero': nc.numero,
            'fecha': nc.fecha.strftime('%d/%m/%Y %H:%M:%S'),
            'tipo_comprobante': nc.tipo_comprobante,
            'cliente': {
                'id': nc.cliente.id,
                'razon_social': nc.cliente.nombre,
                'cuit': nc.cliente.documento if nc.cliente.tipo_documento == 'CUIT' else '',
                'domicilio': nc.cliente.direccion or ''
            },
            'factura': {
                'id': nc.factura.id,
                'numero': nc.factura.numero,
                'fecha': nc.factura.fecha.strftime('%d/%m/%Y')
            },
            'subtotal': float(nc.subtotal),
            'iva': float(nc.iva),
            'total': float(nc.total),
            'cae': nc.cae,
            'cae_vencimiento': nc.vto_cae.strftime('%d/%m/%Y') if nc.vto_cae else None,
            'error_afip': nc.error_afip,
            'observaciones': nc.motivo,
            'detalles': detalles,
            'estado': 'Autorizada' if nc.cae else ('Error AFIP' if nc.error_afip else 'Pendiente')
        }
        
        return jsonify({
            'success': True,
            'nota_credito': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notas_credito_bp.route('/api/notas_credito/estadisticas', methods=['GET'])
@login_required
def api_estadisticas_notas_credito():
    """API para obtener estadísticas de notas de crédito"""
    try:
        fecha_desde = request.args.get('fecha_desde', '').strip()
        fecha_hasta = request.args.get('fecha_hasta', '').strip()
        
        query = NotaCredito.query
        
        if fecha_desde:
            query = query.filter(NotaCredito.fecha >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(NotaCredito.fecha <= fecha_hasta)
        
        todas = query.all()
        
        # Calcular estadísticas
        total_nc = len(todas)
        autorizadas = sum(1 for nc in todas if nc.cae)
        pendientes = sum(1 for nc in todas if not nc.cae and not nc.error_afip)
        con_error = sum(1 for nc in todas if nc.error_afip)
        monto_total = sum(float(nc.total) for nc in todas if nc.cae)
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'total': total_nc,
                'autorizadas': autorizadas,
                'pendientes': pendientes,
                'con_error': con_error,
                'monto_total': monto_total
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API: EMISIÓN DE NOTA DE CRÉDITO
# ============================================================================

@notas_credito_bp.route('/api/emitir_nota_credito/<int:factura_id>', methods=['POST'])
@login_required
def emitir_nota_credito(factura_id):
    """Emitir una Nota de Crédito electrónica para anular una factura"""
    try:
        # Validar factura
        factura = Factura.query.get_or_404(factura_id)
        
        if factura.estado != 'autorizada':
            return jsonify({
                'success': False,
                'error': f'No se puede emitir NC de una factura en estado: {factura.estado}'
            }), 400
        
        # Verificar NC previa
        nc_existente = NotaCredito.query.filter_by(factura_id=factura.id).first()
        if nc_existente:
            return jsonify({
                'success': False,
                'error': f'Esta factura ya tiene una Nota de Crédito: {nc_existente.numero}'
            }), 400
        
        # Obtener motivo
        data = request.get_json()
        motivo = data.get('motivo', '').strip()
        
        if not motivo:
            return jsonify({
                'success': False,
                'error': 'Debe ingresar un motivo para la Nota de Crédito'
            }), 400
        
        print(f"\n{'='*70}")
        print(f"📝 EMITIENDO NOTA DE CRÉDITO")
        print(f"{'='*70}")
        print(f"Factura: {factura.numero}")
        print(f"Motivo: {motivo}")
        
        # Mapeo de tipos
        tipo_nc_map = {
            '01': '03', '1': '03',
            '06': '08', '6': '08',
            '11': '13',
            '51': '53'
        }
        
        tipo_nc = tipo_nc_map.get(str(factura.tipo_comprobante))
        
        if not tipo_nc:
            return jsonify({
                'success': False,
                'error': f'Tipo de factura no soportado: {factura.tipo_comprobante}'
            }), 400
        
        print(f"Tipo NC: {tipo_nc}")
        
        # Obtener próximo número
        punto_venta = ARCA_CONFIG.PUNTO_VENTA
        
        ultima_nc = NotaCredito.query.filter_by(
            tipo_comprobante=tipo_nc,
            punto_venta=punto_venta
        ).order_by(NotaCredito.id.desc()).first()
        
        if ultima_nc and ultima_nc.numero:
            proximo_num = int(ultima_nc.numero.split('-')[1]) + 1
        else:
            proximo_num = 1
        
        numero_nc = f"{punto_venta:04d}-{proximo_num:08d}"
        print(f"Número NC: {numero_nc}")
        
        # Crear NC (sin guardar aún)
        nota_credito = NotaCredito(
            numero=numero_nc,
            tipo_comprobante=tipo_nc,
            punto_venta=punto_venta,
            fecha=datetime.now(),
            factura_id=factura.id,
            factura_numero=factura.numero,
            cliente_id=factura.cliente_id,
            usuario_id=session['user_id'],
            subtotal=factura.subtotal,
            iva=factura.iva,
            total=factura.total,
            estado='pendiente',
            motivo=motivo
        )
        
        db.session.add(nota_credito)
        db.session.flush()  # Obtener ID sin hacer commit
        
        # Copiar items
        items_factura = DetalleFactura.query.filter_by(factura_id=factura.id).all()
        
        for item in items_factura:
            detalle_nc = DetalleNotaCredito(
                nota_credito_id=nota_credito.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                subtotal=item.subtotal,
                porcentaje_iva=item.porcentaje_iva,
                importe_iva=item.importe_iva
            )
            db.session.add(detalle_nc)
        
        print(f"Items copiados: {len(items_factura)}")
        
        # ====================================================================
        # AUTORIZAR EN AFIP (CRÍTICO)
        # ====================================================================
        try:
            print("\n📡 Enviando a AFIP/ARCA...")
            
            resultado = autorizar_comprobante_afip(
                comprobante_id=nota_credito.id,
                tipo_comprobante='nota_credito'
            )
            
            if resultado['success']:
                # ✅ AUTORIZADA POR AFIP
                nota_credito.estado = 'autorizada'
                nota_credito.cae = resultado['cae']
                nota_credito.vto_cae = datetime.strptime(resultado['vto_cae'], '%Y%m%d').date()
                nota_credito.fecha_autorizacion = datetime.now()
                nota_credito.error_afip = None
                print(f"✅ NC Autorizada - CAE: {resultado['cae']}")
            else:
                # ❌ AFIP RECHAZÓ (sin excepción)
                nota_credito.estado = 'error_afip'
                nota_credito.error_afip = resultado.get('error', 'Error desconocido')
                print(f"❌ Error AFIP: {resultado.get('error')}")
        
        except Exception as e_afip:
            # ❌ EXCEPCIÓN AL LLAMAR A AFIP
            print(f"❌ Excepción en AFIP: {str(e_afip)}")
            nota_credito.estado = 'error_afip'
            nota_credito.error_afip = str(e_afip)
        
        # ====================================================================
        # DECISIÓN: GUARDAR O DESCARTAR
        # ====================================================================
        
        if nota_credito.estado == 'autorizada':
            # ✅ ÉXITO: Reintegrar stock y anular factura
            print("\n📦 Reintegrando stock...")
            
            productos_reintegrados = []
            for item in items_factura:
                producto = Producto.query.get(item.producto_id)
                
                if producto:
                    stock_anterior = producto.stock
                    producto.stock += item.cantidad
                    productos_reintegrados.append({
                        'codigo': producto.codigo,
                        'cantidad': float(item.cantidad),
                        'stock_anterior': float(stock_anterior),
                        'stock_nuevo': float(producto.stock)
                    })
                    print(f"   📦 {producto.codigo}: {stock_anterior} → {producto.stock} (+{item.cantidad})")
            
            # Marcar factura como anulada
            factura.estado = 'anulada'
            
            # Guardar TODO
            db.session.commit()
            
            print(f"✅ Stock reintegrado: {len(productos_reintegrados)} productos")
            print(f"✅ Factura {factura.numero} anulada")
            print(f"\n{'='*70}")
            print(f"✅ NOTA DE CRÉDITO AUTORIZADA Y GUARDADA")
            print(f"{'='*70}\n")
            
            return jsonify({
                'success': True,
                'message': f'Nota de Crédito {numero_nc} emitida y autorizada por AFIP correctamente',
                'nota_credito': {
                    'id': nota_credito.id,
                    'numero': nota_credito.numero,
                    'estado': nota_credito.estado,
                    'cae': nota_credito.cae,
                    'vto_cae': nota_credito.vto_cae.isoformat() if nota_credito.vto_cae else None,
                    'total': float(nota_credito.total)
                },
                'factura_anulada': True,
                'productos_reintegrados': len(productos_reintegrados)
            })
        
        else:
            # ❌ ERROR: AFIP rechazó - DESCARTAR TODO
            db.session.rollback()
            
            error_mensaje = nota_credito.error_afip or 'Error desconocido en AFIP'
            
            print(f"\n{'='*70}")
            print(f"❌ NC NO AUTORIZADA - DESCARTANDO CAMBIOS")
            print(f"❌ Error: {error_mensaje}")
            print(f"✅ Factura {factura.numero} mantiene estado: {factura.estado}")
            print(f"{'='*70}\n")
            
            return jsonify({
                'success': False,
                'error': f'AFIP rechazó la Nota de Crédito: {error_mensaje}',
                'detalle': {
                    'error_afip': error_mensaje,
                    'factura_numero': factura.numero,
                    'factura_estado': factura.estado,
                    'mensaje': 'La factura NO fue anulada. No se realizaron cambios en el sistema.'
                }
            }), 400
        
    except Exception as e:
        # ❌ ERROR GENERAL - ROLLBACK
        db.session.rollback()
        print(f"\n❌ ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error interno al emitir NC: {str(e)}'
        }), 500