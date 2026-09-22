# app/services/pdf_service.py
# Servicio para generar PDFs con ReportLab

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import io


# Colores HERMES
HERMES_GOLD = colors.HexColor('#d4af37')
HERMES_DARK = colors.HexColor('#1a1a1a')
HERMES_GRAY = colors.HexColor('#666666')
HERMES_LIGHT = colors.HexColor('#f5f5f5')


def generar_pdf_factura(factura):
    """Genera un PDF de una factura y devuelve los bytes."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f'Factura {factura.numero}',
        author='HERMES Business Control Center',
    )

    styles = getSampleStyleSheet()
    elementos = []

    # === Estilos ===
    style_logo = ParagraphStyle(
        'Logo',
        fontSize=36,
        textColor=HERMES_GOLD,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=0,
        spaceBefore=0,
        leading=48,
    )
    style_subtitle = ParagraphStyle(
        'Subtitle',
        fontSize=9,
        textColor=HERMES_GRAY,
        alignment=TA_CENTER,
        spaceAfter=25,
        spaceBefore=0,
        leading=12,
    )
    style_title = ParagraphStyle(
        'Title',
        fontSize=20,
        textColor=HERMES_DARK,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=20,
        leading=26,
    )
    style_label = ParagraphStyle(
        'Label',
        fontSize=10,
        textColor=HERMES_GRAY,
        fontName='Helvetica-Bold',
        leading=14,
    )
    style_value = ParagraphStyle(
        'Value',
        fontSize=11,
        textColor=HERMES_DARK,
        leading=14,
    )
    style_total = ParagraphStyle(
        'Total',
        fontSize=22,
        textColor=HERMES_GOLD,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        leading=26,
    )
    style_footer = ParagraphStyle(
        'Footer',
        fontSize=8,
        textColor=HERMES_GRAY,
        alignment=TA_CENTER,
        leading=11,
    )

    # === Encabezado ===
    elementos.append(Paragraph('HERMES', style_logo))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph('BUSINESS CONTROL CENTER', style_subtitle))
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(Paragraph(f'FACTURA {factura.numero}', style_title))
    elementos.append(Spacer(1, 0.5 * cm))

    # === Datos del cliente ===
    cliente_nombre = factura.cliente.nombre if factura.cliente else '-'
    cliente_email = factura.cliente.email if factura.cliente else '-'
    cliente_telefono = factura.cliente.telefono if factura.cliente else '-'
    cliente_ciudad = factura.cliente.ciudad if factura.cliente else '-'

    fecha_emision = factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else '-'
    fecha_vencimiento = factura.fecha_vencimiento.strftime('%d/%m/%Y') if factura.fecha_vencimiento else '-'

    data_datos = [
        [Paragraph('<b>Cliente:</b>', style_label), Paragraph(cliente_nombre, style_value)],
        [Paragraph('<b>Email:</b>', style_label), Paragraph(cliente_email, style_value)],
        [Paragraph('<b>Telefono:</b>', style_label), Paragraph(cliente_telefono, style_value)],
        [Paragraph('<b>Ciudad:</b>', style_label), Paragraph(cliente_ciudad, style_value)],
        [Paragraph('<b>Fecha emision:</b>', style_label), Paragraph(fecha_emision, style_value)],
        [Paragraph('<b>Fecha vencimiento:</b>', style_label), Paragraph(fecha_vencimiento, style_value)],
        [Paragraph('<b>Estado:</b>', style_label), Paragraph(factura.estado, style_value)],
    ]

    tabla_datos = Table(data_datos, colWidths=[4 * cm, 12 * cm])
    tabla_datos.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e5e5e5')),
    ]))
    elementos.append(tabla_datos)
    elementos.append(Spacer(1, 1 * cm))

    # === Concepto ===
    elementos.append(Paragraph('<b>CONCEPTO</b>', style_label))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(factura.concepto or '-', style_value))
    elementos.append(Spacer(1, 1 * cm))

    # === Total ===
    data_total = [
        [Paragraph('<b>TOTAL A PAGAR</b>', style_value), Paragraph(f'${factura.total:.2f}', style_total)],
    ]
    tabla_total = Table(data_total, colWidths=[10 * cm, 6 * cm])
    tabla_total.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HERMES_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('LINEBEFORE', (0, 0), (0, 0), 4, HERMES_GOLD),
    ]))
    elementos.append(tabla_total)
    elementos.append(Spacer(1, 1.5 * cm))

    # === Pie ===
    elementos.append(Paragraph(
        f'Factura generada el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}',
        style_footer
    ))
    elementos.append(Paragraph(
        'HERMES Business Control Center - Sistema de gestion empresarial',
        style_footer
    ))

    doc.build(elementos)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
