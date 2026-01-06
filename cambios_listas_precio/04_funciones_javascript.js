// =====================================================
// CAMBIOS JAVASCRIPT PARA productos.html
// =====================================================
// INSTRUCCIONES: 
// 1. Reemplazar la función calcularPrecio()
// 2. Agregar los event listeners para los nuevos márgenes
// 3. Modificar guardarProducto() y cargarProductoEnFormulario()
// =====================================================


// =====================================================
// FUNCIÓN calcularPrecio() - REEMPLAZAR LA EXISTENTE
// =====================================================
function calcularPrecio() {
    const costo = parseFloat(document.getElementById('costo').value) || 0;
    
    // Calcular precio Lista 1 (principal)
    const margen1 = parseFloat(document.getElementById('margen').value) || 0;
    const precio1 = costo * (1 + (margen1 / 100));
    document.getElementById('precio').value = precio1.toFixed(2);
    
    // Calcular precios Listas 2-5 (solo si tienen margen definido)
    for (let i = 2; i <= 5; i++) {
        const margenInput = document.getElementById(`margen${i}`);
        const precioInput = document.getElementById(`precio${i}`);
        
        if (margenInput && precioInput) {
            const margenValor = parseFloat(margenInput.value);
            if (!isNaN(margenValor) && margenValor >= 0) {
                const precioCalculado = costo * (1 + (margenValor / 100));
                precioInput.value = precioCalculado.toFixed(2);
            } else {
                precioInput.value = ''; // Limpiar si no hay margen
            }
        }
    }
    
    // Actualizar ejemplo visual
    const formulaEjemplo = document.getElementById('formulaEjemplo');
    if (formulaEjemplo) {
        formulaEjemplo.innerHTML = `
            <strong>Lista 1:</strong> $${costo.toFixed(2)} × (1 + ${margen1}%/100) = <span class="text-primary">$${precio1.toFixed(2)}</span>
        `;
    }
    
    console.log(`📊 Precios calculados - Costo: $${costo.toFixed(2)}, Lista1: $${precio1.toFixed(2)}`);
}


// =====================================================
// FUNCIÓN limpiarFormProducto() - REEMPLAZAR LA EXISTENTE
// =====================================================
function limpiarFormProducto() {
    document.getElementById('formProducto').reset();
    document.getElementById('productoId').value = '';
    document.getElementById('tituloModal').innerHTML = '<i class="fas fa-plus"></i> Nuevo Producto';
    document.getElementById('stockInicialContainer').style.display = 'block';
    document.getElementById('margen').value = '30';
    
    // Limpiar márgenes y precios adicionales
    for (let i = 2; i <= 5; i++) {
        const margenInput = document.getElementById(`margen${i}`);
        const precioInput = document.getElementById(`precio${i}`);
        if (margenInput) margenInput.value = '';
        if (precioInput) precioInput.value = '';
    }
    
    document.getElementById('precio').value = '0.00';
    document.getElementById('activo').checked = true;
    
    modoEdicion = false;
    calculoManual = false;
    productoActual = null;
}


// =====================================================
// FUNCIÓN cargarProductoEnFormulario() - REEMPLAZAR
// =====================================================
function cargarProductoEnFormulario(producto) {
    modoEdicion = true;
    calculoManual = false;
    productoActual = producto;
    
    document.getElementById('productoId').value = producto.id;
    document.getElementById('codigo').value = producto.codigo;
    document.getElementById('nombre').value = producto.nombre;
    document.getElementById('descripcion').value = producto.descripcion || '';
    document.getElementById('costo').value = producto.costo || 0;
    document.getElementById('categoria').value = producto.categoria || '';
    document.getElementById('iva').value = producto.iva || 21;
    document.getElementById('activo').checked = producto.activo;
    
    // Cargar margen y precio Lista 1
    document.getElementById('margen').value = producto.margen || 30;
    document.getElementById('precio').value = producto.precio || 0;
    
    // Cargar márgenes y precios Listas 2-5
    for (let i = 2; i <= 5; i++) {
        const margenInput = document.getElementById(`margen${i}`);
        const precioInput = document.getElementById(`precio${i}`);
        
        if (margenInput && precioInput) {
            const margenKey = `margen${i}`;
            const precioKey = `precio${i}`;
            
            if (producto[margenKey] !== null && producto[margenKey] !== undefined) {
                margenInput.value = producto[margenKey];
                precioInput.value = producto[precioKey] || '';
            } else {
                margenInput.value = '';
                precioInput.value = '';
            }
        }
    }
    
    // Ocultar stock inicial en edición
    document.getElementById('stockInicialContainer').style.display = 'none';
    
    // Actualizar título del modal
    document.getElementById('tituloModal').innerHTML = '<i class="fas fa-edit"></i> Editar Producto';
    
    console.log(`📝 Producto cargado: ${producto.codigo} - ${producto.nombre}`);
}


// =====================================================
// FUNCIÓN guardarProducto() - REEMPLAZAR
// =====================================================
function guardarProducto() {
    const form = document.getElementById('formProducto');
    
    // Validar formulario
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Validaciones principales
    const costo = parseFloat(document.getElementById('costo').value);
    const margen = parseFloat(document.getElementById('margen').value);
    
    if (costo <= 0) {
        alert('El costo debe ser mayor a 0');
        document.getElementById('costo').focus();
        return;
    }
    
    if (margen < 0) {
        alert('El margen de Lista 1 no puede ser negativo');
        document.getElementById('margen').focus();
        return;
    }
    
    // Recalcular precios antes de enviar
    calcularPrecio();
    
    // Recopilar datos del formulario
    const formData = {
        id: document.getElementById('productoId').value || null,
        codigo: document.getElementById('codigo').value.trim().toUpperCase(),
        nombre: document.getElementById('nombre').value.trim(),
        descripcion: document.getElementById('descripcion').value.trim(),
        costo: costo,
        margen: margen,
        precio: parseFloat(document.getElementById('precio').value),
        categoria: document.getElementById('categoria').value.trim(),
        iva: parseFloat(document.getElementById('iva').value),
        activo: document.getElementById('activo').checked
    };
    
    // Agregar márgenes de listas 2-5 (solo si tienen valor)
    for (let i = 2; i <= 5; i++) {
        const margenInput = document.getElementById(`margen${i}`);
        if (margenInput && margenInput.value !== '') {
            const margenValor = parseFloat(margenInput.value);
            if (!isNaN(margenValor) && margenValor >= 0) {
                formData[`margen${i}`] = margenValor;
            }
        }
    }
    
    // Solo incluir stock si es producto nuevo
    if (!formData.id) {
        formData.stock = parseInt(document.getElementById('stock').value) || 0;
    }
    
    // Validaciones adicionales
    if (!formData.codigo) {
        alert('El código es obligatorio');
        document.getElementById('codigo').focus();
        return;
    }
    
    if (!formData.nombre) {
        alert('El nombre es obligatorio');
        document.getElementById('nombre').focus();
        return;
    }
    
    // Mostrar indicador de carga
    const btnGuardar = document.querySelector('#modalProducto .btn-primary');
    const textoOriginal = btnGuardar.innerHTML;
    btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    btnGuardar.disabled = true;
    
    console.log('📤 Enviando datos:', formData);
    
    // Enviar datos al servidor
    fetch('/guardar_producto', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalProducto'));
            modal.hide();
            
            // Recargar la página para mostrar los cambios
            window.location.reload();
        } else {
            alert('Error: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión al guardar el producto');
    })
    .finally(() => {
        // Restaurar botón
        btnGuardar.innerHTML = textoOriginal;
        btnGuardar.disabled = false;
    });
}


// =====================================================
// EVENT LISTENERS - AGREGAR EN DOMContentLoaded
// =====================================================
// Agregar estos listeners dentro del bloque:
// document.addEventListener('DOMContentLoaded', function() { ... });
// =====================================================

// Event listener para costo - recalcula todas las listas
document.getElementById('costo').addEventListener('input', function() {
    calcularPrecio();
});

// Event listener para margen Lista 1
document.getElementById('margen').addEventListener('input', function() {
    calculoManual = true;
    calcularPrecio();
});

// Event listeners para márgenes Listas 2-5
for (let i = 2; i <= 5; i++) {
    const margenInput = document.getElementById(`margen${i}`);
    if (margenInput) {
        margenInput.addEventListener('input', function() {
            calcularPrecio();
        });
    }
}


// =====================================================
// FIN DE CAMBIOS JAVASCRIPT
// =====================================================
