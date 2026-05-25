import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generar_pdf_cotizacion(cotizacion, solicitud):
    os.makedirs("uploads/cotizaciones", exist_ok=True)

    nombre_archivo = f"uploads/cotizaciones/cotizacion_{cotizacion.id_cotizacion}.pdf"

    c = canvas.Canvas(nombre_archivo, pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, 750, "COTIZACION FIXYA")

    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Solicitud ID: {solicitud.id_solicitud}")
    c.drawString(50, 680, f"Rut cliente: {solicitud.usuario_rut}")
    c.drawString(50, 660, f"Rut tecnico: {cotizacion.tecnico_usuario_rut}")
    c.drawString(50, 630, "Descripcion de cotizacion:")
    c.drawString(50, 610, (cotizacion.mensaje_cotizacion or "")[:90])
    c.drawString(50, 580, f"Monto: ${cotizacion.monto_estimado}")
    c.drawString(50, 550, f"Fecha: {cotizacion.fecha_cotizacion or ''}")
    c.drawString(50, 520, f"Fecha vigencia: {cotizacion.fecha_vigencia}")
    c.drawString(50, 490, "Problema:")
    c.drawString(50, 470, solicitud.descripcion_problema[:90])
    c.drawString(50, 420, "Firma tecnico:")
    c.line(50, 390, 250, 390)

    c.save()

    return f"/{nombre_archivo}"
