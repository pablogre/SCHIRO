#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stock_audit.py - MÓDULO DE AUDITORÍA DE STOCK
═══════════════════════════════════════════════════════════════════════════════
Registra todos los movimientos de stock para seguimiento y reportes.
NO MODIFICA el comportamiento existente, solo REGISTRA.
═══════════════════════════════════════════════════════════════════════════════
"""

from flask import Blueprint, jsonify, request, session, render_template
from sqlalchemy import text
from datetime import datetime, timedelta

stock_audit_bp = Blueprint('stock_audit', __name__)


def registrar_movimiento_stock(db, producto_id, tipo, cantidad, signo, 
                                stock_anterior, stock_nuevo, 
                                referencia_tipo=None, referencia_id=None,
                                motivo=None, usuario_id=None, usuario_nombre=None,
                                codigo_producto=None, nombre_producto=None):
    """
    Registra un movimiento de stock en la tabla de auditoría.
    Esta función SOLO registra, no modifica stock.
    
    Tipos válidos:
    - 'venta': Venta normal facturada
    - 'venta_fiada': Venta en cuenta corriente
    - 'ajuste_entrada': Entrada manual de stock
    - 'ajuste_salida': Salida manual de stock
    - 'ajuste_manual': Corrección/ajuste directo
    - 'devolucion': Devolución de producto
    - 'combo': Descuento por venta de combo
    """
    try:
        query = """
            INSERT INTO stock_movimiento 
            (producto_id, codigo_producto, nombre_producto, tipo, cantidad, signo,
             stock_anterior, stock_nuevo, referencia_tipo, referencia_id, 
             motivo, usuario_id, usuario_nombre, fecha)
            VALUES 
            (:producto_id, :codigo, :nombre, :tipo, :cantidad, :signo,
             :stock_anterior, :stock_nuevo, :ref_tipo, :ref_id,
             :motivo, :usuario_id, :usuario_nombre, NOW())
        """
        
        db.session.execute(text(query), {
            'producto_id': producto_id,
            'codigo': codigo_producto,
            'nombre': nombre_producto,
            'tipo': tipo,
            'cantidad': abs(float(cantidad)),  # Siempre positivo
            'signo': signo,  # '+' o '-'
            'stock_anterior': float(stock_anterior) if stock_anterior is not None else None,
            'stock_nuevo': float(stock_nuevo) if stock_nuevo is not None else None,
            'ref_tipo': referencia_tipo,
            'ref_id': referencia_id,
            'motivo': motivo,
            'usuario_id': usuario_id,
            'usuario_nombre': usuario_nombre
        })
        db.session.commit()
        
        print(f"📋 AUDIT: {codigo_producto} | {tipo} | {signo}{cantidad} | {stock_anterior} → {stock_nuevo}")
        return True
        
    except Exception as e:
        print(f"⚠️ Error registrando movimiento stock: {str(e)}")
        # No hacer rollback aquí para no afectar la transacción principal
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS DE CONSULTA
# ═══════════════════════════════════════════════════════════════════════════════

@stock_audit_bp.route('/stock_audit')
def vista_stock_audit():
    """Vista principal de auditoría de stock"""
    return render_template('stock_audit.html')


@stock_audit_bp.route('/api/stock_audit/movimientos')
def api_movimientos_stock():
    """Obtener movimientos de stock con filtros"""
    from flask import current_app
    db = current_app.extensions['sqlalchemy'].db
    
    try:
        # Parámetros de filtro
        producto_id = request.args.get('producto_id', type=int)
        codigo = request.args.get('codigo', '').strip()
        tipo = request.args.get('tipo', '').strip()
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        limit = request.args.get('limit', 100, type=int)
        
        # Query base
        query = """
            SELECT 
                id, producto_id, codigo_producto, nombre_producto,
                tipo, cantidad, signo, stock_anterior, stock_nuevo,
                referencia_tipo, referencia_id, motivo,
                usuario_nombre, fecha
            FROM stock_movimiento
            WHERE 1=1
        """
        params = {}
        
        if producto_id:
            query += " AND producto_id = :producto_id"
            params['producto_id'] = producto_id
            
        if codigo:
            query += " AND codigo_producto LIKE :codigo"
            params['codigo'] = f"%{codigo}%"
            
        if tipo:
            query += " AND tipo = :tipo"
            params['tipo'] = tipo
            
        if fecha_desde:
            query += " AND DATE(fecha) >= :fecha_desde"
            params['fecha_desde'] = fecha_desde
            
        if fecha_hasta:
            query += " AND DATE(fecha) <= :fecha_hasta"
            params['fecha_hasta'] = fecha_hasta
        
        query += " ORDER BY fecha DESC LIMIT :limit"
        params['limit'] = limit
        
        result = db.session.execute(text(query), params)
        
        movimientos = []
        for row in result:
            movimientos.append({
                'id': row.id,
                'producto_id': row.producto_id,
                'codigo': row.codigo_producto,
                'nombre': row.nombre_producto,
                'tipo': row.tipo,
                'cantidad': float(row.cantidad),
                'signo': row.signo,
                'stock_anterior': float(row.stock_anterior) if row.stock_anterior else None,
                'stock_nuevo': float(row.stock_nuevo) if row.stock_nuevo else None,
                'referencia_tipo': row.referencia_tipo,
                'referencia_id': row.referencia_id,
                'motivo': row.motivo,
                'usuario': row.usuario_nombre,
                'fecha': row.fecha.strftime('%d/%m/%Y %H:%M') if row.fecha else ''
            })
        
        return jsonify({
            'success': True,
            'movimientos': movimientos,
            'total': len(movimientos)
        })
        
    except Exception as e:
        print(f"Error obteniendo movimientos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_audit_bp.route('/api/stock_audit/reporte_producto/<int:producto_id>')
def api_reporte_producto(producto_id):
    """Reporte detallado de movimientos de un producto"""
    from flask import current_app
    db = current_app.extensions['sqlalchemy'].db
    
    try:
        # Info del producto
        query_producto = """
            SELECT id, codigo, nombre, stock FROM producto WHERE id = :id
        """
        result = db.session.execute(text(query_producto), {'id': producto_id})
        producto = result.fetchone()
        
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        # Resumen de movimientos
        query_resumen = """
            SELECT 
                tipo,
                signo,
                COUNT(*) as cantidad_movimientos,
                SUM(cantidad) as total_cantidad
            FROM stock_movimiento
            WHERE producto_id = :producto_id
            GROUP BY tipo, signo
            ORDER BY tipo
        """
        result = db.session.execute(text(query_resumen), {'producto_id': producto_id})
        
        resumen = []
        total_entradas = 0
        total_salidas = 0
        
        for row in result:
            cantidad = float(row.total_cantidad)
            if row.signo == '+':
                total_entradas += cantidad
            else:
                total_salidas += cantidad
                
            resumen.append({
                'tipo': row.tipo,
                'signo': row.signo,
                'movimientos': row.cantidad_movimientos,
                'total': cantidad
            })
        
        # Últimos movimientos
        query_ultimos = """
            SELECT 
                tipo, cantidad, signo, stock_anterior, stock_nuevo,
                referencia_tipo, referencia_id, motivo, usuario_nombre, fecha
            FROM stock_movimiento
            WHERE producto_id = :producto_id
            ORDER BY fecha DESC
            LIMIT 50
        """
        result = db.session.execute(text(query_ultimos), {'producto_id': producto_id})
        
        ultimos = []
        for row in result:
            ultimos.append({
                'tipo': row.tipo,
                'cantidad': float(row.cantidad),
                'signo': row.signo,
                'stock_anterior': float(row.stock_anterior) if row.stock_anterior else None,
                'stock_nuevo': float(row.stock_nuevo) if row.stock_nuevo else None,
                'referencia': f"{row.referencia_tipo} #{row.referencia_id}" if row.referencia_id else '-',
                'motivo': row.motivo or '-',
                'usuario': row.usuario_nombre or '-',
                'fecha': row.fecha.strftime('%d/%m/%Y %H:%M') if row.fecha else ''
            })
        
        return jsonify({
            'success': True,
            'producto': {
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'stock_actual': float(producto.stock)
            },
            'resumen': resumen,
            'total_entradas': total_entradas,
            'total_salidas': total_salidas,
            'balance': total_entradas - total_salidas,
            'ultimos_movimientos': ultimos
        })
        
    except Exception as e:
        print(f"Error generando reporte: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_audit_bp.route('/api/stock_audit/resumen_diario')
def api_resumen_diario():
    """Resumen de movimientos por día"""
    from flask import current_app
    db = current_app.extensions['sqlalchemy'].db
    
    try:
        dias = request.args.get('dias', 7, type=int)
        
        query = """
            SELECT 
                DATE(fecha) as dia,
                tipo,
                signo,
                COUNT(*) as movimientos,
                SUM(cantidad) as total
            FROM stock_movimiento
            WHERE fecha >= DATE_SUB(NOW(), INTERVAL :dias DAY)
            GROUP BY DATE(fecha), tipo, signo
            ORDER BY dia DESC, tipo
        """
        
        result = db.session.execute(text(query), {'dias': dias})
        
        resumen = {}
        for row in result:
            dia = row.dia.strftime('%Y-%m-%d')
            if dia not in resumen:
                resumen[dia] = {'entradas': 0, 'salidas': 0, 'detalle': []}
            
            cantidad = float(row.total)
            if row.signo == '+':
                resumen[dia]['entradas'] += cantidad
            else:
                resumen[dia]['salidas'] += cantidad
                
            resumen[dia]['detalle'].append({
                'tipo': row.tipo,
                'signo': row.signo,
                'movimientos': row.movimientos,
                'total': cantidad
            })
        
        return jsonify({
            'success': True,
            'dias': dias,
            'resumen': resumen
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_audit_bp.route('/api/stock_audit/discrepancias')
def api_discrepancias():
    """Detectar posibles discrepancias de stock"""
    from flask import current_app
    db = current_app.extensions['sqlalchemy'].db
    
    try:
        # Productos con movimientos recientes donde el stock calculado no coincide
        query = """
            SELECT 
                p.id,
                p.codigo,
                p.nombre,
                p.stock as stock_actual,
                (
                    SELECT stock_nuevo 
                    FROM stock_movimiento sm 
                    WHERE sm.producto_id = p.id 
                    ORDER BY sm.fecha DESC 
                    LIMIT 1
                ) as ultimo_stock_registrado,
                (
                    SELECT COUNT(*) 
                    FROM stock_movimiento sm 
                    WHERE sm.producto_id = p.id
                ) as total_movimientos
            FROM producto p
            WHERE p.activo = 1
            HAVING ultimo_stock_registrado IS NOT NULL 
               AND ABS(stock_actual - ultimo_stock_registrado) > 0.01
            ORDER BY ABS(stock_actual - ultimo_stock_registrado) DESC
            LIMIT 50
        """
        
        result = db.session.execute(text(query))
        
        discrepancias = []
        for row in result:
            discrepancias.append({
                'id': row.id,
                'codigo': row.codigo,
                'nombre': row.nombre,
                'stock_actual': float(row.stock_actual),
                'ultimo_registrado': float(row.ultimo_stock_registrado) if row.ultimo_stock_registrado else None,
                'diferencia': float(row.stock_actual) - float(row.ultimo_stock_registrado) if row.ultimo_stock_registrado else None,
                'movimientos': row.total_movimientos
            })
        
        return jsonify({
            'success': True,
            'discrepancias': discrepancias,
            'total': len(discrepancias)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# INICIALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def init_stock_audit(app):
    """Inicializa el módulo de auditoría de stock"""
    app.register_blueprint(stock_audit_bp)
    print("✅ Módulo STOCK AUDIT inicializado")