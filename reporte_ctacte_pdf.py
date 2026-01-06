# reporte_ctacte_pdf.py - Generador de reportes PDF para cuentas corrientes

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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
        
        # Teléfono
        self.setFont('Helvetica', 8)
        self.drawString(1.2*inch, 0.4*inch, "Tel: 336-4537093")
        
        # Website
        self.drawString(2.5*inch, 0.4*inch, "https://FactuFacil.ar")
        
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

def generar_pdf_cuentas_corrientes(clientes, resumen):
    """
    Genera un PDF profesional del reporte de cuentas corrientes
    
    Args:
        clientes: Lista de clientes con sus saldos y movimientos
        resumen: Diccionario con totales y estadísticas
    
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
    
    # Estilos para celdas
    style_cell = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
        wordWrap='CJK',
        splitLongWords=True,
        textColor=colors.HexColor('#2d3748')
    )
    
    style_cell_center = ParagraphStyle(
        'CellTextCenter',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2d3748')
    )
    
    style_cell_right = ParagraphStyle(
        'CellTextRight',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#2d3748')
    )
    
    # Estilo para encabezados de tabla (BLANCO)
    style_header = ParagraphStyle(
        'HeaderText',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    style_header_right = ParagraphStyle(
        'HeaderTextRight',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_RIGHT,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    # ==================== ENCABEZADO ====================
    
    # Título principal
    titulo = Paragraph("REPORTE DE CUENTAS CORRIENTES", style_title)
    elements.append(titulo)
    
    # Fecha de generación
    fecha_generacion = Paragraph(
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        style_subtitle
    )
    elements.append(fecha_generacion)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== RESUMEN EJECUTIVO ====================
    
    elements.append(Paragraph("RESUMEN GENERAL", style_section))
    
    # Tabla de resumen
    datos_resumen = [
        ['Total Adeudado:', f"${resumen['total_adeudado']:,.2f}"],
        ['Clientes con Deuda:', f"{resumen['clientes_con_deuda']}"],
        ['Total de Clientes:', f"{resumen['total_clientes']}"],
        ['Movimientos Pendientes:', f"{resumen['total_movimientos']}"]
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
    
    # ==================== DETALLE DE CLIENTES ====================
    
    elements.append(Paragraph("DETALLE POR CLIENTE", style_section))
    elements.append(Spacer(1, 0.1*inch))
    
    # Encabezados de tabla con texto BLANCO
    encabezados = [
        Paragraph('<b>Cliente</b>', style_header),
        Paragraph('<b>Documento</b>', style_header),
        Paragraph('<b>Mov. Pend.</b>', style_header_right),
        Paragraph('<b>Saldo Pendiente</b>', style_header_right),
        Paragraph('<b>Última Oper.</b>', style_header),
        Paragraph('<b>Estado</b>', style_header)
    ]
    
    # Iniciar datos de tabla
    data = [encabezados]
    
    # Agregar clientes
    print(f"📊 Exportando {len(clientes)} clientes al PDF")
    
    for cliente in clientes:
        # Determinar estado
        estado = "DEBE" if cliente['saldo_pendiente'] > 0 else "AL DÍA"
        
        # Formatear última operación
        ultima_op = cliente['ultima_operacion'] if cliente['ultima_operacion'] else 'Sin ops.'
        if ultima_op != 'Sin ops.':
            try:
                # Intentar formatear la fecha si es un objeto datetime o string
                if isinstance(ultima_op, str):
                    # Asumir formato YYYY-MM-DD o YYYY-MM-DD HH:MM:SS
                    if ' ' in ultima_op:
                        fecha_obj = datetime.strptime(ultima_op, '%Y-%m-%d %H:%M:%S')
                    else:
                        fecha_obj = datetime.strptime(ultima_op, '%Y-%m-%d')
                    ultima_op = fecha_obj.strftime('%d/%m/%Y')
            except:
                pass
        
        # Usar Paragraph para cada celda
        fila = [
            Paragraph(cliente['nombre'], style_cell),
            Paragraph(cliente['documento'] if cliente['documento'] else 'S/D', style_cell_center),
            Paragraph(str(cliente['movimientos_pendientes']), style_cell_right),
            Paragraph(f"${cliente['saldo_pendiente']:,.2f}", style_cell_right),
            Paragraph(ultima_op, style_cell_center),
            Paragraph(estado, style_cell_center)
        ]
        
        data.append(fila)
    
    # Configurar anchos de columna optimizados
    col_widths = [
        2.2 * inch,   # Cliente
        1.0 * inch,   # Documento
        0.8 * inch,   # Mov. Pendientes
        1.2 * inch,   # Saldo Pendiente
        1.0 * inch,   # Última Operación
        0.7 * inch    # Estado
    ]
    
    # Crear tabla
    tabla_clientes = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de tabla
    tabla_style = [
        # Encabezado con fondo azul
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Datos
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 1), (-1, -1), 4),
        ('RIGHTPADDING', (0, 1), (-1, -1), 4),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
    ]
    
    # Aplicar colores según estado (filas con deuda en amarillo claro)
    for idx, cliente in enumerate(clientes, start=1):
        if cliente['saldo_pendiente'] > 0:
            # Fondo amarillo para clientes que deben
            tabla_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#fef5e7')))
            
            # Columna de saldo en rojo
            tabla_style.append(('TEXTCOLOR', (3, idx), (3, idx), colors.HexColor('#c0392b')))
            
            # Estado "DEBE" con fondo rojo
            tabla_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#c0392b')))
            tabla_style.append(('TEXTCOLOR', (5, idx), (5, idx), colors.white))
        else:
            # Estado "AL DÍA" con fondo verde
            tabla_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#27ae60')))
            tabla_style.append(('TEXTCOLOR', (5, idx), (5, idx), colors.white))
    
    tabla_clientes.setStyle(TableStyle(tabla_style))
    
    elements.append(tabla_clientes)
    
    # ==================== TOTALES ====================
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabla de totales
    datos_totales = [
        [
            Paragraph('<b>TOTALES</b>', style_header),
            Paragraph('', style_header),
            Paragraph('', style_header_right),
            Paragraph(f'<b>${resumen["total_adeudado"]:,.2f}</b>', style_header_right),
            Paragraph(f'<b>{resumen["clientes_con_deuda"]} clientes con deuda</b>', style_header),
            Paragraph('', style_header)
        ]
    ]
    
    tabla_totales = Table(datos_totales, colWidths=col_widths)
    tabla_totales.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
        ('ALIGN', (4, 0), (4, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0'))
    ]))
    
    elements.append(tabla_totales)
    
    # ==================== GENERAR PDF ====================
    
    # Construir documento con canvas personalizado
    doc.build(elements, canvasmaker=FooterCanvas)
    
    # Obtener contenido del buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    print(f"✅ PDF de cuentas corrientes generado exitosamente: {len(pdf_bytes)} bytes")
    
    return pdf_bytes