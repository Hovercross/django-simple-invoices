#!/usr/bin/python

import os

from io import StringIO, BytesIO
from decimal import Decimal
from datetime import date
from collections import OrderedDict

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

from copy import copy, deepcopy

from invoices.models import FixedService

accentColor = colors.Color(red=.325, green=.484, blue=.612)

myFolder = os.path.dirname(os.path.realpath(__file__))
fontFolder = os.path.join(myFolder, "fonts")

for fontFile in os.listdir(fontFolder):
    fontName, extension = os.path.splitext(fontFile)
    if (extension) == ".ttf":
        pdfmetrics.registerFont(TTFont(fontName, os.path.join(fontFolder, fontFile)))

styles = getSampleStyleSheet()
normalStyle = copy(styles["Normal"])
#titleStyle = copy(styles["Title"])

tableNameStyle = copy(styles["Normal"])
tableNameStyle.fontSize = 16
tableNameStyle.fontName = "HelveticaNeue-Light"
tableNameStyle.textColor = accentColor
tableNameStyle.leftIndent = -6
tableNameStyle.leading = 22

tableHeaderStyle = copy(styles["Normal"])
tableHeaderStyle.fontSize = 10
tableHeaderStyle.fontName = "HelveticaNeue-Bold"
tableHeaderStyle.textColor = colors.white
#tableHeaderStyle.fontSize = 14

tableHeaderStyleRight = copy(tableHeaderStyle)
tableHeaderStyleRight.alignment = TA_RIGHT

tableItemStyle = copy(styles["Normal"])
tableItemStyleRight = copy(tableItemStyle)
tableItemStyleRight.alignment = TA_RIGHT

tableTotalStyle = copy(tableItemStyle)
tableTotalStyle.alignment = TA_RIGHT

invoiceSubTotalStyle = copy(tableItemStyle)
invoiceSubTotalStyle.alignment = TA_RIGHT
invoiceSubTotalStyle.fontName = "HelveticaNeue-Light"
invoiceSubTotalStyle.fontSize = 10

invoiceTotalStyle = copy(invoiceSubTotalStyle)
invoiceTotalStyle.fontName = "HelveticaNeue-Bold"

line_item_date_format = "%Y-%m-%d"

defaultTableStyle = [
    ('BACKGROUND', (0, 0), (-1, 0), accentColor),
    ('LINEBEFORE', (1, 0), (-1, 0), 1, colors.white),
    ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
    ('LINEABOVE', (0, 0), (-1, -2), .25, colors.grey),
]

def build_invoice_pdf(invoice, output):
    def onFirstPage(canvas, doc):
        canvas.saveState()
        canvas.setFont('HelveticaNeue-Bold', 13)
        canvas.setStrokeColor(accentColor)
        canvas.setFillColor(accentColor)
        
        canvas.line(.75 * inch, (11-.5)*inch, 7.75*inch, (11-.5)*inch)
        canvas.drawString(.75 * inch, (11-.75) * inch, "Adam M Peacock")

        canvas.setFont('HelveticaNeue-Light', 16)
        canvas.setFillColor(colors.black)        
        canvas.drawString(.75 * inch, 9.75 * inch, "INVOICE")
        
        canvas.setFont('HelveticaNeue-Light', 10)
        canvas.setFillColor(accentColor)
        canvas.drawString(.75 * inch, 9.45*inch, "(860) 309-0293")
        canvas.drawString(.75 * inch, 9.30*inch, "adam@thepeacock.net")
        
        canvas.setFillColor(colors.black)
        canvas.drawString(.75 * inch, 9 * inch, "94 West St, Apt 21")
        canvas.drawString(.75 * inch, 8.85 * inch, "Vernon, CT 06066")
        
        #Client area
        canvas.setFont('HelveticaNeue-Bold', 10)
        canvas.drawString(4.25 * inch, 9.75 * inch, invoice.client.name)
        
        canvas.setFont('HelveticaNeue-Light', 10)
        address_lines = invoice.client.address.splitlines()
        num_address_lines = len(address_lines)
        
        for i, address_line in enumerate(address_lines):
            canvas.drawString(4.25 * inch, (9.55 - i*.15) * inch, address_line)
        
        if invoice.date:
            canvas.drawString(4.25 * inch, (9.45 - (num_address_lines*.15)) * inch, "Invoice date: {:}".format(invoice.date.strftime("%B %d, %Y")))
            
        canvas.drawString(4.25 * inch, (9.30 - (num_address_lines*.15)) * inch, "Invoice number: {:}".format(invoice.id))
        canvas.drawString(4.25 * inch, (9.05 - (num_address_lines*.15)) * inch, "Please make checks payable to Adam M Peacock")
        canvas.restoreState()
    
    def onLaterPages(canvas, doc):
        canvas.saveState()
        canvas.setFont('HelveticaNeue-Bold', 13)
        canvas.setStrokeColor(accentColor)
        canvas.setFillColor(accentColor)
    
        canvas.line(.75 * inch, (11-.5)*inch, 7.75*inch, (11-.5)*inch)
        canvas.drawString(.75 * inch, (11-.75) * inch, "Adam M Peacock")

        canvas.setFont('HelveticaNeue-Light', 16)
        canvas.setFillColor(colors.black)        
        canvas.drawString(.75 * inch, 10 * inch, "INVOICE")
    
        #Client area
        canvas.setFont('HelveticaNeue-Bold', 10)
        canvas.drawString(4.25 * inch, 10.25 * inch, invoice.client.name)
        canvas.setFont('HelveticaNeue-Light', 10)
        canvas.drawString(4.25 * inch, 10.1 * inch, "Invoice number: {:s} (continued)".format(invoice.id))

        canvas.restoreState()
    
    fixed_services_total = Decimal(0)
    
    doc = SimpleDocTemplate(output, leftMargin = .75 * inch, rightMargin = .75 * inch, pagesize=(8.5*inch, 11*inch), topMargin=1.25*inch)
    story = [Spacer(1, 1.5 * inch)]
    
    #TODO: Generic
    #TODO: Hourly

    fixed_services = FixedService.objects.filter(invoice=invoice).order_by('date')
    #We have to iterate anyway, don't bother hitting the DB again
    
    if fixed_services:
        together = []
        
        together.append(Paragraph("Fixed Cost Services", tableNameStyle))
        
        table = [[
            Paragraph("Date", tableHeaderStyle), 
            Paragraph("Description", tableHeaderStyle), 
            Paragraph("Total", tableHeaderStyleRight)]]
        
        tableStyle = []
        tableStyle.extend(defaultTableStyle)
        
        for fixed_service in fixed_services:
            row = [
                fixed_service.date and Paragraph(fixed_service.date.strftime(line_item_date_format), tableItemStyle) or None,
                fixed_service.description and Paragraph(fixed_service.description, tableItemStyle) or None,
                fixed_service.total and Paragraph(fixed_service.display_total, tableItemStyleRight) or None,
            ]
                
            table.append(row)
                        
            fixed_services_total += Decimal(fixed_service.total)
        
        
        fixed_services_total = round(fixed_services_total, 2)
        table.append([
            None,
            Paragraph("Fixed Rate Services Total", tableTotalStyle),
            Paragraph("${:.2f}".format(fixed_services_total), tableTotalStyle)
        ])
        
        t = Table(table, colWidths=[1*inch, 5*inch,1*inch])
        t.setStyle(tableStyle)
        together.append(t)
        together.append(Spacer(1, .5*inch))
        story.append(KeepTogether(together))
        
    
    #TODO: Expense
    #TODO: Payment
    #TODO: Credit
    
    doc.build(story, onFirstPage=onFirstPage, onLaterPages=onLaterPages)