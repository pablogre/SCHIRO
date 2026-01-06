-- =====================================================
-- SCRIPT SQL: Agregar columnas para 5 listas de precios
-- FactuFacil - Múltiples Márgenes de Ganancia
-- =====================================================
-- IMPORTANTE: Ejecutar este script ANTES de actualizar el código
-- Hacer BACKUP de la base de datos antes de ejecutar
-- =====================================================

-- Verificar estructura actual (ejecutar esto primero para ver qué tenés)
-- DESCRIBE producto;

-- =====================================================
-- AGREGAR COLUMNAS DE MÁRGENES (margen ya existe como Lista 1)
-- =====================================================

-- Margen Lista 2 (ej: Mayorista)
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS margen2 DECIMAL(5,2) DEFAULT NULL;

-- Margen Lista 3 (ej: Distribuidor)
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS margen3 DECIMAL(5,2) DEFAULT NULL;

-- Margen Lista 4 (ej: Especial)
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS margen4 DECIMAL(5,2) DEFAULT NULL;

-- Margen Lista 5 (ej: Promocional)
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS margen5 DECIMAL(5,2) DEFAULT NULL;

-- =====================================================
-- AGREGAR COLUMNAS DE PRECIOS (precio ya existe como Lista 1)
-- =====================================================

-- Precio Lista 2
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS precio2 DECIMAL(10,2) DEFAULT NULL;

-- Precio Lista 3
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS precio3 DECIMAL(10,2) DEFAULT NULL;

-- Precio Lista 4
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS precio4 DECIMAL(10,2) DEFAULT NULL;

-- Precio Lista 5
ALTER TABLE producto 
ADD COLUMN IF NOT EXISTS precio5 DECIMAL(10,2) DEFAULT NULL;

-- =====================================================
-- AGREGAR LISTA DE PRECIO POR DEFECTO AL CLIENTE
-- =====================================================

ALTER TABLE cliente 
ADD COLUMN IF NOT EXISTS lista_precio INT DEFAULT 1;

-- =====================================================
-- VERIFICAR QUE SE AGREGARON LAS COLUMNAS
-- =====================================================

-- Verificar producto
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'producto' 
AND COLUMN_NAME LIKE 'margen%' OR COLUMN_NAME LIKE 'precio%'
ORDER BY COLUMN_NAME;

-- Verificar cliente
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'cliente' 
AND COLUMN_NAME = 'lista_precio';

-- =====================================================
-- OPCIONAL: Inicializar precios existentes con valores actuales
-- (Esto copia el precio actual a todas las listas)
-- =====================================================

-- UPDATE producto SET 
--     precio2 = precio,
--     precio3 = precio,
--     precio4 = precio,
--     precio5 = precio,
--     margen2 = margen,
--     margen3 = margen,
--     margen4 = margen,
--     margen5 = margen
-- WHERE precio2 IS NULL;

SELECT '✅ Columnas agregadas correctamente' AS resultado;
