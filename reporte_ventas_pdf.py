# reporte_ventas_pdf.py - Generador de reportes PDF para ventas

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os

class FooterCanvas(canvas.Canvas):
    """Canvas personalizado para agregar pie de página en todas las páginas"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_footer(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_footer(self, page_count):
        """Dibuja el pie de página con información de FactuFacil"""
        page_width = letter[0]
        page_height = letter[1]
        
        # Línea separadora
        self.setStrokeColor(colors.HexColor('#cbd5e0'))
        self.setLineWidth(0.5)
        self.line(0.5*inch, 0.6*inch, page_width - 0.5*inch, 0.6*inch)
        
        # Configurar fuente
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#4a5568'))
        
        # Texto izquierdo: FactuFacil
        self.setFont('Helvetica-Bold', 9)
        self.drawString(0.5*inch, 0.4*inch, "FactuFacil")
        
        # Icono de teléfono (usando símbolo Unicode)
        self.setFont('Helvetica', 8)
        self.drawString(1.2*inch, 0.4*inch, "📞 336-4537093")
        
        # Icono de mundo (usando símbolo Unicode)
        self.drawString(2.5*inch, 0.4*inch, "🌐 https://FactuFacil.ar")
        
        # Texto derecho: Número de página
        self.setFont('Helvetica', 8)
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(page_width - 0.5*inch, 0.4*inch, page_text)
        
        # Línea inferior con marca de agua
        self.setFont('Helvetica', 7)
        self.setFillColor(colors.HexColor('#a0aec0'))
        self.drawCentredString(
            page_width / 2, 
            0.25*inch, 
            "Sistema de Gestión POS Argentina - FactuFacil"
        )

def generar_pdf_reporte_ventas(productos, resumen, parametros):
    """
    Genera un PDF profesional del reporte de ventas
    
    Args:
        productos: Lista de productos con sus ventas
        resumen: Diccionario con totales y estadísticas
        parametros: Parámetros del reporte (fechas, filtros)
    
    Returns:
        bytes: Contenido del PDF en bytes
    """
    
    # Crear buffer en memoria
    buffer = BytesIO()
    
    # Configurar documento con canvas personalizado
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.8*inch  # Más espacio para el pie de página
    )
    
    # Contenedor de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo para título
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    style_subtitle = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    # Estilo para sección
    style_section = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Estilos para celdas con wrapping automático
    style_cell = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        alignment=TA_LEFT,
        wordWrap='CJK',
        splitLongWords=True,
        textColor=colors.HexColor('#2d3748')
    )
    
    style_cell_center = ParagraphStyle(
        'CellTextCenter',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2d3748')
    )
    
    style_cell_right = ParagraphStyle(
        'CellTextRight',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#2d3748')
    )
    
    # Estilo para encabezados de tabla (BLANCO)
    style_header = ParagraphStyle(
        'HeaderText',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.white,  # ✅ TEXTO BLANCO
        fontName='Helvetica-Bold'
    )
    
    style_header_right = ParagraphStyle(
        'HeaderTextRight',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_RIGHT,
        textColor=colors.white,  # ✅ TEXTO BLANCO
        fontName='Helvetica-Bold'
    )
    
    # ==================== ENCABEZADO ====================
    
    # Título principal
    titulo = Paragraph("REPORTE DE VENTAS POR PRODUCTO", style_title)
    elements.append(titulo)
    
    # Información del período
    fecha_desde = parametros.get('fecha_desde', 'N/A')
    fecha_hasta = parametros.get('fecha_hasta', 'N/A')
    
    periodo = Paragraph(
        f"<b>Período:</b> {fecha_desde} al {fecha_hasta}",
        style_subtitle
    )
    elements.append(periodo)
    
    # Fecha de generación
    fecha_generacion = Paragraph(
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        style_subtitle
    )
    elements.append(fecha_generacion)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== RESUMEN EJECUTIVO ====================
    
    elements.append(Paragraph("RESUMEN DEL PERÍODO", style_section))
    
    # Tabla de resumen
    datos_resumen = [
        ['Total de Productos:', f"{resumen['total_productos']}"],
        ['Unidades Vendidas:', f"{resumen['total_unidades_reales']:,.2f}"],
        ['Total Vendido:', f"${resumen['total_ventas']:,.2f}"],
        ['Promedio por Producto:', f"${resumen['promedio_por_producto']:,.2f}"]
    ]
    
    tabla_resumen = Table(datos_resumen, colWidths=[3*inch, 2*inch])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0'))
    ]))
    
    elements.append(tabla_resumen)
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== DETALLE DE PRODUCTOS ====================
    
    elements.append(Paragraph("DETALLE DE PRODUCTOS", style_section))
    elements.append(Spacer(1, 0.1*inch))
    
    # Encabezados de tabla con texto BLANCO
    encabezados = [
        Paragraph('<b>Código</b>', style_header),
        Paragraph('<b>Producto</b>', style_header),
        Paragraph('<b>Cat.</b>', style_header),
        Paragraph('<b>Cantidad</b>', style_header_right),
        Paragraph('<b>Precio Prom.</b>', style_header_right),
        Paragraph('<b>Total Vendido</b>', style_header_right),
        Paragraph('<b>%</b>', style_header_right)
    ]
    
    # Iniciar datos de tabla
    data = [encabezados]
    
    # Agregar productos
    print(f"📊 Exportando {len(productos)} productos al PDF")
    
    for producto in productos:
        # Calcular porcentaje
        porcentaje = (producto['total_vendido'] / resumen['total_ventas'] * 100) if resumen['total_ventas'] > 0 else 0
        
        # Usar Paragraph para cada celda con wrapping automático
        fila = [
            Paragraph(str(producto['codigo']), style_cell),
            Paragraph(producto['nombre'], style_cell),
            Paragraph(producto['categoria'] or 'N/A', style_cell_center),
            Paragraph(f"{producto['cantidad_real']:,.2f}", style_cell_right),
            Paragraph(f"${producto['precio_promedio']:,.2f}", style_cell_right),
            Paragraph(f"${producto['total_vendido']:,.2f}", style_cell_right),
            Paragraph(f"{porcentaje:.1f}%", style_cell_right)
        ]
        
        data.append(fila)
    
    # Configurar anchos de columna optimizados
    col_widths = [
        0.7 * inch,   # Código
        2.4 * inch,   # Producto
        0.6 * inch,   # Categoría
        0.8 * inch,   # Cantidad
        0.9 * inch,   # Precio Promedio
        1.0 * inch,   # Total Vendido
        0.5 * inch    # Porcentaje
    ]
    
    # Crear tabla
    tabla_productos = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de tabla
    tabla_productos.setStyle(TableStyle([
        # Encabezado con fondo azul
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Datos
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 1), (-1, -1), 3),
        ('RIGHTPADDING', (0, 1), (-1, -1), 3),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
    ]))
    
    elements.append(tabla_productos)
    
    # ==================== GENERAR PDF ====================
    
    # Construir documento con canvas personalizado
    doc.build(elements, canvasmaker=FooterCanvas)
    
    # Obtener contenido del buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    print(f"✅ PDF generado exitosamente: {len(pdf_bytes)} bytes")
    
    return pdf_bytes