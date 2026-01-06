# FactuFacil - Implementación de 5 Listas de Precios

## 📋 Resumen de Cambios

Este paquete contiene las modificaciones necesarias para agregar **5 listas de precios** a FactuFacil, permitiendo definir diferentes márgenes de ganancia para cada producto.

### Archivos incluidos:

| Archivo | Descripción |
|---------|-------------|
| `01_agregar_columnas.sql` | Script SQL para agregar columnas a la BD |
| `02_cambios_app_py.py` | Modificaciones para el backend (app.py) |
| `03_formulario_producto.html` | Nuevo formulario de alta de productos |
| `04_funciones_javascript.js` | Funciones JS actualizadas |

---

## 🚨 IMPORTANTE: HACER BACKUP ANTES DE EMPEZAR

```bash
# Backup de la base de datos
mysqldump -u usuario -p carnave > backup_carnave_$(date +%Y%m%d).sql

# Backup de los archivos
cp app.py app.py.backup
cp templates/productos.html templates/productos.html.backup
```

---

## 📝 Pasos de Implementación

### Paso 1: Ejecutar el Script SQL

Primero agregar las columnas a la base de datos:

```bash
mysql -u usuario -p carnave < 01_agregar_columnas.sql
```

O ejecutar manualmente en phpMyAdmin/MySQL Workbench.

**Columnas que se agregan:**
- `producto`: margen2, margen3, margen4, margen5, precio2, precio3, precio4, precio5
- `cliente`: lista_precio (INT, default 1)

---

### Paso 2: Modificar app.py

Abrir `app.py` y aplicar los cambios del archivo `02_cambios_app_py.py`:

#### 2.1 En el modelo Producto (línea ~269, después de `margen`):
```python
# === LISTAS DE PRECIOS MÚLTIPLES ===
margen2 = db.Column(Numeric(5, 2), nullable=True)
precio2 = db.Column(Numeric(10, 2), nullable=True)
margen3 = db.Column(Numeric(5, 2), nullable=True)
precio3 = db.Column(Numeric(10, 2), nullable=True)
margen4 = db.Column(Numeric(5, 2), nullable=True)
precio4 = db.Column(Numeric(10, 2), nullable=True)
margen5 = db.Column(Numeric(5, 2), nullable=True)
precio5 = db.Column(Numeric(10, 2), nullable=True)
```

#### 2.2 En el modelo Cliente (línea ~254, después de `tipo_precio`):
```python
lista_precio = db.Column(db.Integer, default=1)
```

#### 2.3 En el método `to_dict()` del Producto:
Agregar los campos de las listas adicionales al diccionario de retorno.

#### 2.4 Agregar el método `obtener_precio_lista()`:
Este método permite obtener el precio según la lista seleccionada.

#### 2.5 Reemplazar la función `guardar_producto()`:
La nueva versión procesa los 5 márgenes y calcula los 5 precios.

---

### Paso 3: Modificar productos.html

#### 3.1 Reemplazar la sección de "Costos y Precios":
Buscar líneas 222-268 aproximadamente y reemplazar con el contenido de `03_formulario_producto.html`.

#### 3.2 Actualizar las funciones JavaScript:
En la sección `<script>`, reemplazar las funciones con las del archivo `04_funciones_javascript.js`:
- `calcularPrecio()`
- `limpiarFormProducto()`
- `cargarProductoEnFormulario()`
- `guardarProducto()`

#### 3.3 Agregar event listeners para los nuevos márgenes.

---

## ✅ Verificación

Después de aplicar los cambios:

1. **Reiniciar el servidor Flask**
2. **Ir a Productos → Nuevo Producto**
3. **Verificar que aparezcan los 5 campos de margen**
4. **Probar crear un producto con múltiples márgenes**
5. **Editar un producto existente y verificar que cargue los valores**

---

## 🔮 Próximos Pasos (Fase 2)

Una vez funcionando el alta de productos, podemos agregar:

1. **Selector de lista en facturación**: Al agregar producto al carrito, elegir con qué lista facturar.

2. **Lista por defecto en cliente**: Que cada cliente tenga una lista asignada y se use automáticamente.

3. **Visualización en tabla de productos**: Mostrar las 5 columnas de precios o un resumen.

4. **Actualización masiva de márgenes**: Poder cambiar un margen para todos los productos de una categoría.

---

## ⚠️ Notas Importantes

- Las listas 2-5 son **opcionales**. Si no se definen, el sistema usará el precio de Lista 1.
- El campo `precio` (Lista 1) sigue siendo el precio principal del sistema.
- Los cambios son **retrocompatibles**: los productos existentes seguirán funcionando.
- El cliente tiene un campo `lista_precio` para asignarle una lista por defecto (1-5).

---

## 🆘 Si algo sale mal

```bash
# Restaurar backup de BD
mysql -u usuario -p carnave < backup_carnave_YYYYMMDD.sql

# Restaurar archivos
cp app.py.backup app.py
cp templates/productos.html.backup templates/productos.html
```

---

**Creado para FactuFacil - Diciembre 2024**
