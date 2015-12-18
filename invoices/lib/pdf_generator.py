#!/usr/bin/python

from datetime import date
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from invoices.models import HourlyService
from invoices.lib.pdf_styles import accent_color, line_item_date_format, table_item_style, table_item_style_right, table_header_style, table_header_style_right, table_name_style, default_table_style, table_total_style

class InvoicePDFBuilder(object):
    def __init__(self, invoice):
        self.invoice = invoice
        self.hourly_items = HourlyService.objects.filter(invoice=invoice).order_by('date')

        #Will be calculated by get_hourly_story_items so the math between uniform and non-uniform rates are consistent
        self.hourly_items_total = None
        
    def get_hourly_story_items(self):
        if not self.hourly_items:
            return []
        
        yield Paragraph("Hourly Services", table_name_style)
        
        uniform_rate = (len(set(self.hourly_items.values_list('rate'))) == 1)
        
        
        if not uniform_rate:
            table = [[
                Paragraph("Date", table_header_style), 
                Paragraph("Location", table_header_style), 
                Paragraph("Description", table_header_style), 
                Paragraph("Hours", table_header_style_right),
                Paragraph("Rate", table_header_style_right),
                Paragraph("Total", table_header_style_right),
            ]]
        else:
            table = [[
                Paragraph("Date", table_header_style), 
                Paragraph("Location", table_header_style), 
                Paragraph("Description", table_header_style), 
                Paragraph("Hours", table_header_style_right)
            ]]
            
            uniform_rate_value = self.hourly_items.values('rate')[0]['rate']
            print(uniform_rate_value)
            
        if not uniform_rate:
            self.hourly_items_total = Decimal(0)
        else:
            total_hours = Decimal(0)
            
        for hourly_item in self.hourly_items:
            if not uniform_rate:
                table.append([
                    hourly_item.date and Paragraph(hourly_item.date.strftime(line_item_date_format), table_item_style) or None,
                    hourly_item.location and Paragraph(hourly_item.location, table_item_style) or None,
                    hourly_item.description and Paragraph(hourly_item.description, table_item_style) or None,
                    hourly_item.hours and Paragraph("{:0.3f}".format(hourly_item.hours), table_item_style_right) or None,
                    hourly_item.rate and Paragraph("{:0.2f}".format(hourly_item.rate), table_item_style_right) or None,
                    Paragraph(hourly_item.display_total, table_item_style_right)
                ])
                
                self.hourly_items_total += hourly_item.total
                
            else:
                table.append([
                    hourly_item.date and Paragraph(hourly_item.date.strftime(line_item_date_format), table_item_style) or None,
                    hourly_item.location and Paragraph(hourly_item.description, table_item_style) or None,
                    hourly_item.description and Paragraph(hourly_item.description, table_item_style) or None,
                    hourly_item.hours and Paragraph("{:0.3f}".format(hourly_item.hours), table_item_style_right) or None,
                ])
                
                total_hours += hourly_item.hours
        
        if uniform_rate:
            self.hourly_items_total = Decimal(round(total_hours * uniform_rate_value, 2))
        
        table_style = []
        table_style.extend(default_table_style)
        
        if uniform_rate:
            table.append([
                Paragraph("Hourly Rate", table_total_style),
                None,
                None,
                Paragraph("${:.2f}".format(uniform_rate_value), table_total_style)
            ])
            
            col_widths = [1*inch, 1*inch, 4*inch, 1*inch]
            
            table.append([
                Paragraph("Hourly Services Total", table_total_style), 
                None,
                None,
                Paragraph("${:.2f}".format(self.hourly_items_total), table_total_style)])
            
            table_style.remove(('LINEABOVE', (0, -1), (-1, -1), 1, colors.black))
            table_style.remove(('LINEABOVE', (0, 0), (-1, -2), .25, colors.grey))
            table_style.append(('LINEABOVE', (0, -2), (-1, -2), 1, colors.black))
            table_style.append(('LINEABOVE', (0, 0), (-1, -3), .25, colors.grey))
            table_style.append(('SPAN', (0, -2), (-2, -2)))
            
        else:
            table.append([
                Paragraph("Hourly Services Total", table_total_style), 
                None,
                None,
                None,
                None,
                Paragraph("${:.2f}".format(self.hourly_items_total), table_total_style)])
            
            col_widths = [1*inch, 1*inch, 2.5*inch, .75*inch, .75*inch, 1*inch]
            
        table_item = Table(table, colWidths = col_widths)
        table_item.setStyle(TableStyle(table_style))
        
        yield table_item
        yield Spacer(1, .5*inch)
        
    def build_pdf(self, output):
        def onFirstPage(canvas, doc):
            canvas.saveState()
            canvas.setFont('HelveticaNeue-Bold', 13)
            canvas.setStrokeColor(accent_color)
            canvas.setFillColor(accent_color)
        
            canvas.line(.75 * inch, (11-.5)*inch, 7.75*inch, (11-.5)*inch)
            canvas.drawString(.75 * inch, (11-.75) * inch, "Adam M Peacock")

            canvas.setFont('HelveticaNeue-Light', 16)
            canvas.setFillColor(colors.black)        
            canvas.drawString(.75 * inch, 9.75 * inch, "INVOICE")
        
            canvas.setFont('HelveticaNeue-Light', 10)
            canvas.setFillColor(accent_color)
            canvas.drawString(.75 * inch, 9.45*inch, "(860) 309-0293")
            canvas.drawString(.75 * inch, 9.30*inch, "adam@thepeacock.net")
        
            canvas.setFillColor(colors.black)
            canvas.drawString(.75 * inch, 9 * inch, "94 West St, Apt 21")
            canvas.drawString(.75 * inch, 8.85 * inch, "Vernon, CT 06066")
        
            #Client area
            canvas.setFont('HelveticaNeue-Bold', 10)
            canvas.drawString(4.25 * inch, 9.75 * inch, self.invoice.client.name)
        
            canvas.setFont('HelveticaNeue-Light', 10)
            address_lines = self.invoice.client.address.splitlines()
            num_address_lines = len(address_lines)
        
            for i, address_line in enumerate(address_lines):
                canvas.drawString(4.25 * inch, (9.55 - i*.15) * inch, address_line)
        
            if self.invoice.date:
                canvas.drawString(4.25 * inch, (9.45 - (num_address_lines*.15)) * inch, "Invoice date: {:}".format(self.invoice.date.strftime("%B %d, %Y")))
            
            canvas.drawString(4.25 * inch, (9.30 - (num_address_lines*.15)) * inch, "Invoice number: {:}".format(self.invoice.id))
            canvas.drawString(4.25 * inch, (9.05 - (num_address_lines*.15)) * inch, "Please make checks payable to Adam M Peacock")
            canvas.restoreState()
        
        def onLaterPages(canvas, doc):
            canvas.saveState()
            canvas.setFont('HelveticaNeue-Bold', 13)
            canvas.setStrokeColor(accent_color)
            canvas.setFillColor(accent_color)
    
            canvas.line(.75 * inch, (11-.5)*inch, 7.75*inch, (11-.5)*inch)
            canvas.drawString(.75 * inch, (11-.75) * inch, "Adam M Peacock")

            canvas.setFont('HelveticaNeue-Light', 16)
            canvas.setFillColor(colors.black)        
            canvas.drawString(.75 * inch, 10 * inch, "INVOICE")
    
            #Client area
            canvas.setFont('HelveticaNeue-Bold', 10)
            canvas.drawString(4.25 * inch, 10.25 * inch, self.invoice.client.name)
            canvas.setFont('HelveticaNeue-Light', 10)
            canvas.drawString(4.25 * inch, 10.1 * inch, "Invoice number: {:s} (continued)".format(self.invoice.client.id))

            canvas.restoreState()
        
        doc = SimpleDocTemplate(output, leftMargin = .75 * inch, rightMargin = .75 * inch, pagesize=(8.5*inch, 11*inch), topMargin=1.25*inch)
        story = list(self.get_story())
        doc.build(story, onFirstPage=onFirstPage, onLaterPages=onLaterPages)

    def get_story(self):
        yield Spacer(1, 1.5 * inch)
        
        for hourly_story_item in self.get_hourly_story_items():
            yield hourly_story_item
        
