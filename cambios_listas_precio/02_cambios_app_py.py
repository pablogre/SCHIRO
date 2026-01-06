# =====================================================
# CAMBIOS PARA app.py - FactuFacil Listas de Precios
# =====================================================
# INSTRUCCIONES: Buscar y reemplazar las secciones indicadas
# =====================================================

# =====================================================
# CAMBIO 1: MODELO PRODUCTO
# =====================================================
# Buscar la clase Producto (aproximadamente línea 256)
# Agregar estos campos DESPUÉS de la línea:
#     margen = db.Column(Numeric(5, 2), default=30.00)
# =====================================================

    # === LISTAS DE PRECIOS MÚLTIPLES ===
    # Lista 1: margen y precio existentes (no tocar)
    # Lista 2
    margen2 = db.Column(Numeric(5, 2), nullable=True)
    precio2 = db.Column(Numeric(10, 2), nullable=True)
    # Lista 3
    margen3 = db.Column(Numeric(5, 2), nullable=True)
    precio3 = db.Column(Numeric(10, 2), nullable=True)
    # Lista 4
    margen4 = db.Column(Numeric(5, 2), nullable=True)
    precio4 = db.Column(Numeric(10, 2), nullable=True)
    # Lista 5
    margen5 = db.Column(Numeric(5, 2), nullable=True)
    precio5 = db.Column(Numeric(10, 2), nullable=True)


# =====================================================
# CAMBIO 2: MODELO CLIENTE
# =====================================================
# Buscar la clase Cliente (aproximadamente línea 245)
# Agregar este campo DESPUÉS de:
#     tipo_precio = db.Column(db.String(10), default='venta')
# =====================================================

    lista_precio = db.Column(db.Integer, default=1)  # 1-5, lista de precio por defecto


# =====================================================
# CAMBIO 3: MÉTODO to_dict() DEL PRODUCTO
# =====================================================
# Buscar el método to_dict() dentro de la clase Producto
# Agregar estas líneas dentro del return (antes del cierre })
# =====================================================

            # Listas de precios múltiples
            'margen2': float(self.margen2) if self.margen2 else None,
            'precio2': float(self.precio2) if self.precio2 else None,
            'margen3': float(self.margen3) if self.margen3 else None,
            'precio3': float(self.precio3) if self.precio3 else None,
            'margen4': float(self.margen4) if self.margen4 else None,
            'precio4': float(self.precio4) if self.precio4 else None,
            'margen5': float(self.margen5) if self.margen5 else None,
            'precio5': float(self.precio5) if self.precio5 else None,


# =====================================================
# CAMBIO 4: MÉTODO obtener_precio_lista() - NUEVO
# =====================================================
# Agregar este método DENTRO de la clase Producto
# (después del método to_dict() por ejemplo)
# =====================================================

    def obtener_precio_lista(self, numero_lista=1):
        """Obtener precio según la lista de precios seleccionada"""
        precios = {
            1: self.precio,
            2: self.precio2 if self.precio2 else self.precio,
            3: self.precio3 if self.precio3 else self.precio,
            4: self.precio4 if self.precio4 else self.precio,
            5: self.precio5 if self.precio5 else self.precio,
        }
        return float(precios.get(numero_lista, self.precio))
    
    def obtener_margen_lista(self, numero_lista=1):
        """Obtener margen según la lista de precios seleccionada"""
        margenes = {
            1: self.margen,
            2: self.margen2 if self.margen2 else self.margen,
            3: self.margen3 if self.margen3 else self.margen,
            4: self.margen4 if self.margen4 else self.margen,
            5: self.margen5 if self.margen5 else self.margen,
        }
        return float(margenes.get(numero_lista, self.margen))


# =====================================================
# CAMBIO 5: FUNCIÓN guardar_producto()
# =====================================================
# REEMPLAZAR COMPLETAMENTE la función guardar_producto()
# (aproximadamente línea 2255-2345)
# =====================================================

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    """Crear o actualizar un producto con costo y múltiples márgenes"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.json
        
        # Validar datos requeridos
        if not data.get('codigo', '').strip():
            return jsonify({'error': 'El código es obligatorio'}), 400
        
        if not data.get('nombre', '').strip():
            return jsonify({'error': 'El nombre es obligatorio'}), 400
        
        # Validar costo
        try:
            costo = float(data.get('costo', 0))
            if costo <= 0:
                return jsonify({'error': 'El costo debe ser mayor a 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Costo inválido'}), 400
        
        # Validar margen principal (Lista 1)
        try:
            margen = float(data.get('margen', 30))
            if margen < 0:
                return jsonify({'error': 'El margen no puede ser negativo'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Margen inválido'}), 400
        
        # Calcular precio Lista 1
        precio_calculado = costo * (1 + (margen / 100))
        
        # Procesar márgenes adicionales (Listas 2-5)
        margenes = {'margen': margen}
        precios = {'precio': precio_calculado}
        
        for i in range(2, 6):
            margen_key = f'margen{i}'
            precio_key = f'precio{i}'
            
            margen_valor = data.get(margen_key)
            if margen_valor is not None and margen_valor != '':
                try:
                    margen_float = float(margen_valor)
                    if margen_float >= 0:
                        margenes[margen_key] = margen_float
                        precios[precio_key] = costo * (1 + (margen_float / 100))
                except (ValueError, TypeError):
                    pass  # Si es inválido, no lo guardamos
        
        producto_id = data.get('id')
        codigo = data['codigo'].strip().upper()
        
        # Verificar que el código no exista (excepto si es el mismo producto)
        producto_existente = Producto.query.filter_by(codigo=codigo).first()
        if producto_existente and (not producto_id or producto_existente.id != int(producto_id)):
            return jsonify({'error': f'Ya existe un producto con el código {codigo}'}), 400
        
        if producto_id:  # Editar producto existente
            producto = Producto.query.get_or_404(producto_id)
            accion = 'actualizado'
        else:  # Crear nuevo producto
            producto = Producto()
            accion = 'creado'
        
        # Actualizar datos del producto
        producto.codigo = codigo
        producto.nombre = data['nombre'].strip()
        producto.descripcion = data.get('descripcion', '').strip() or None
        producto.costo = Decimal(str(round(costo, 2)))
        producto.categoria = data.get('categoria', '').strip() or None
        producto.iva = Decimal(str(data.get('iva', 21)))
        producto.activo = bool(data.get('activo', True))
        producto.fecha_modificacion = datetime.now()
        
        # Guardar margen y precio Lista 1
        producto.margen = Decimal(str(round(margen, 2)))
        producto.precio = Decimal(str(round(precio_calculado, 2)))
        
        # Guardar márgenes y precios Listas 2-5
        for i in range(2, 6):
            margen_key = f'margen{i}'
            precio_key = f'precio{i}'
            
            if margen_key in margenes:
                setattr(producto, margen_key, Decimal(str(round(margenes[margen_key], 2))))
                setattr(producto, precio_key, Decimal(str(round(precios[precio_key], 2))))
            else:
                # Si no se proporciona, dejamos None (usará Lista 1 por defecto)
                setattr(producto, margen_key, None)
                setattr(producto, precio_key, None)
        
        # Solo actualizar stock si es producto nuevo
        if not producto_id:
            producto.stock = int(data.get('stock', 0))
        
        # Guardar en base de datos
        if not producto_id:
            db.session.add(producto)
        
        db.session.commit()
        
        print(f"✅ Producto {accion}: {codigo}")
        print(f"   Costo: ${costo:.2f}")
        print(f"   Lista 1: Margen {margen}% → Precio ${precio_calculado:.2f}")
        for i in range(2, 6):
            if f'margen{i}' in margenes:
                print(f"   Lista {i}: Margen {margenes[f'margen{i}']}% → Precio ${precios[f'precio{i}']:.2f}")
        
        return jsonify({
            'success': True,
            'message': f'Producto {accion} correctamente',
            'producto_id': producto.id,
            'producto_codigo': producto.codigo,
            'precio_calculado': round(precio_calculado, 2),
            'costo': round(costo, 2),
            'margen': round(margen, 2),
            'precios': {f'precio{i}': round(precios.get(f'precio{i}', 0), 2) for i in range(1, 6) if f'precio{i}' in precios or i == 1}
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error guardando producto: {str(e)}")
        return jsonify({'error': f'Error al guardar producto: {str(e)}'}), 500


# =====================================================
# CAMBIO 6: RUTA api/producto_detalle
# =====================================================
# Buscar la ruta /api/producto_detalle/<int:producto_id>
# Asegurarse que el return incluya los nuevos campos
# El método to_dict() ya los incluye si agregaste el CAMBIO 3
# =====================================================


# =====================================================
# FIN DE CAMBIOS PARA app.py
# =====================================================
