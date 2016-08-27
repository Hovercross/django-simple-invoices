#!/usr/bin/python

from datetime import date
from decimal import Decimal
from io import BytesIO

from django.db.models import Sum

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

from invoices.models import HourlyService, FixedService, Expense, Payment, Credit, RelatedPDF
from invoices.lib.pdf_styles import accent_color, line_item_date_format, table_item_style, table_item_style_right, table_header_style, table_header_style_right, table_name_style, default_table_style, table_total_style

class InvoicePDFBuilder(object):
    def __init__(self, invoice):
        self.invoice = invoice
        
        self.hourly_services = HourlyService.objects.filter(invoice=invoice)
        self.fixed_services = FixedService.objects.filter(invoice=invoice)
        self.expenses = Expense.objects.filter(invoice=invoice)
        self.payments = Payment.objects.filter(invoice=invoice)
        self.credits = Credit.objects.filter(invoice=invoice)
        
        self.pdf_includes = RelatedPDF.objects.filter(invoice=invoice)
    
    #Returns the top section end, broken to it's own method so I can run this without actually drawing anything
    def on_first_page(self, canvas=None):
        def noop(*args, **kwargs):
            pass
        
        #Fake object that proxies the canvas object - if canvas is none, this returns a method that does nothing for calling
        class CanvasProxy(object):
            def __init__(self, canvas):
                self.canvas = canvas
            
            def __getattr__(self, key):
                if self.canvas:
                    return getattr(self.canvas, key)
                
                return noop
                
                    
        canvas = CanvasProxy(canvas)
                    
        canvas.saveState()
        canvas.setFont('HelveticaNeue-Bold', 13)
        canvas.setStrokeColor(accent_color)
        canvas.setFillColor(accent_color)
    
        canvas.line(.75 * inch, (11-.5)*inch, 7.75*inch, (11-.5)*inch)
        canvas.drawString(.75 * inch, (11-.75) * inch, self.invoice.vendor.name)

        canvas.setFont('HelveticaNeue-Light', 16)
        canvas.setFillColor(colors.black)        
        canvas.drawString(.75 * inch, 9.75 * inch, "INVOICE")
        
        line_space = .15*inch
        
        #Draw left side
        left_side_y = 9.45*inch
        
        canvas.setFont('HelveticaNeue-Light', 10)
        canvas.setFillColor(accent_color)
        
        if self.invoice.vendor.phone:
            canvas.drawString(.75 * inch, left_side_y, self.invoice.vendor.phone)
            left_side_y -= line_space
        
        if self.invoice.vendor.email:
            canvas.drawString(.75 * inch, left_side_y, self.invoice.vendor.email)
            left_side_y -= line_space
        
        canvas.setFont('HelveticaNeue-Light', 10)
        canvas.setFillColor(colors.black)
        if self.invoice.vendor.address:
            left_side_y -= line_space
            address_lines = self.invoice.vendor.address.splitlines()
            
            for address_line in address_lines:                    
                canvas.drawString(.75 * inch, left_side_y, address_line)
                left_side_y -= line_space
        
        #Draw right side
        canvas.setFont('HelveticaNeue-Bold', 10)
        canvas.setFillColor(colors.black)
        canvas.drawString(4.25 * inch, 9.75*inch, self.invoice.client.name)
    
        right_side_y = 9.45*inch
        
        canvas.setFont('HelveticaNeue-Light', 10)
        canvas.setFillColor(colors.black)
        
        if self.invoice.client.address:
            address_lines = self.invoice.client.address.splitlines()
            
            for address_line in address_lines:
                canvas.drawString(4.25 * inch, right_side_y, address_line)
                right_side_y -= line_space
            
            right_side_y -= line_space #Extra line break
            
    
        if self.invoice.date:
            canvas.drawString(4.25 * inch, right_side_y, "Invoice date: {:}".format(self.invoice.date.strftime("%B %d, %Y")))
            right_side_y -= line_space
            
        canvas.drawString(4.25 * inch, right_side_y, "Invoice number: {:}".format(self.invoice.id))
        right_side_y -= line_space*2 #Extra line break
        
        if self.invoice.vendor.checks_payable_to:
            canvas.drawString(4.25 * inch, right_side_y, "Please make checks payable to {}".format(self.invoice.vendor.checks_payable_to))
            right_side_y -= line_space
                    
        top_section_y = min(left_side_y, right_side_y)
        
        canvas.setStrokeColor(colors.grey)
        canvas.line(.75 * inch, top_section_y, 7.75*inch, top_section_y)
        
        canvas.setAuthor("Adam M Peacock")
        canvas.setSubject("Invoice")
        canvas.setTitle("Invoice {}".format(self.invoice.id))
        
        canvas.restoreState()
        
        return 11*inch - top_section_y
        
    def get_hourly_story_items(self):
        if not self.hourly_services:
            return []
        
        yield Paragraph("Hourly Services", table_name_style)
        
        uniform_rate = (len(set(self.hourly_services.values_list('rate'))) == 1)
        
        
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
            
            uniform_rate_value = self.hourly_services.values('rate')[0]['rate']
            
        total_hours = Decimal(0)
            
        for hourly_service in self.hourly_services:
            if not uniform_rate:
                table.append([
                    hourly_service.date and Paragraph(hourly_service.date.strftime(line_item_date_format), table_item_style) or None,
                    hourly_service.location and Paragraph(hourly_service.location, table_item_style) or None,
                    hourly_service.description and Paragraph(hourly_service.description, table_item_style) or None,
                    hourly_service.hours and Paragraph("{:0.3f}".format(hourly_service.hours), table_item_style_right) or None,
                    hourly_service.rate and Paragraph("{:0.2f}".format(hourly_service.rate), table_item_style_right) or None,
                    Paragraph(hourly_service.display_total, table_item_style_right)
                ])
                
            else:
                table.append([
                    hourly_service.date and Paragraph(hourly_service.date.strftime(line_item_date_format), table_item_style) or None,
                    hourly_service.location and Paragraph(hourly_service.location, table_item_style) or None,
                    hourly_service.description and Paragraph(hourly_service.description, table_item_style) or None,
                    hourly_service.hours and Paragraph("{:0.3f}".format(hourly_service.hours), table_item_style_right) or None,
                ])
                
                total_hours += hourly_service.hours
        
        table_style = []
        table_style.extend(default_table_style)
        
        if uniform_rate:
            table.append([
                Paragraph("Total Hours", table_total_style),
                None,
                None,
                Paragraph("{:.3f}".format(total_hours), table_total_style)
            ])
            
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
                Paragraph("${:.2f}".format(self.invoice.hourly_services_total), table_total_style)])
            
            table_style.remove(('LINEABOVE', (0, -1), (-1, -1), 1, colors.black))
            table_style.remove(('LINEABOVE', (0, 0), (-1, -2), .25, colors.grey))
            table_style.append(('LINEABOVE', (0, -3), (-1, -3), 1, colors.black))
            table_style.append(('LINEABOVE', (0, 0), (-1, -4), .25, colors.grey))
            table_style.append(('SPAN', (0, -2), (-2, -2)))
            table_style.append(('SPAN', (0, -3), (-2, -3)))
            
        else:
            table.append([
                Paragraph("Hourly Services Total", table_total_style), 
                None,
                None,
                None,
                None,
                Paragraph("${:.2f}".format(self.invoice.hourly_services_total), table_total_style)])
            
            col_widths = [1*inch, 1*inch, 2.5*inch, .75*inch, .75*inch, 1*inch]
            
        table_item = Table(table, colWidths = col_widths)
        table_item.setStyle(TableStyle(table_style))
        
        yield table_item
    
    def get_fixed_service_story_items(self):
        if not self.fixed_services:
            return []
        
        yield Paragraph("Fixed Services", table_name_style)
        
        table = [[
            Paragraph("Date", table_header_style), 
            Paragraph("Description", table_header_style), 
            Paragraph("Total", table_header_style_right)]]
        
        table_style = []
        table_style.extend(default_table_style)
        
        for fixed_service in self.fixed_services:
            table.append([
                fixed_service.date and Paragraph(fixed_service.date.strftime(line_item_date_format), table_item_style),
                fixed_service.description and Paragraph(fixed_service.description, table_item_style),
                Paragraph("${:0.2f}".format(fixed_service.total), table_item_style_right)
            ])
        
        table.append([
            Paragraph("Fixed Rate Services Total", table_total_style),
            None,
            Paragraph("${:0.2f}".format(self.invoice.fixed_services_total), table_total_style)
        ])
        
        
        table_item = Table(table, colWidths = [1*inch, 5*inch, 1*inch])
        table_item.setStyle(table_style)
        
        yield table_item
    
    def get_expense_story_items(self):
        if not self.expenses:
            return []
        
        yield Paragraph("Expenses", table_name_style)
        
        table = [[
            Paragraph("Date", table_header_style), 
            Paragraph("Description", table_header_style), 
            Paragraph("Total", table_header_style_right)]]
        
        table_style = []
        table_style.extend(default_table_style)
        
        for expense in self.expenses:
            table.append([
                expense.date and Paragraph(expense.date.strftime(line_item_date_format), table_item_style),
                expense.description and Paragraph(expense.description, table_item_style),
                Paragraph(expense.display_total, table_item_style_right)
            ])
        
        table.append([
            Paragraph("Total Expenses", table_total_style),
            None,
            Paragraph("${:0.2f}".format(self.invoice.expense_total), table_total_style)
        ])
        
        
        table_item = Table(table, colWidths = [1*inch, 5*inch, 1*inch])
        table_item.setStyle(table_style)
        
        yield table_item
    
    def get_payment_story_items(self):
        if not self.payments:
            return []
        
        yield Paragraph("Payments", table_name_style)
        
        table = [[
            Paragraph("Date", table_header_style), 
            Paragraph("Description", table_header_style), 
            Paragraph("Amount", table_header_style_right)
        ]]
        
        table_style = []
        table_style.extend(default_table_style)
        
        for payment in self.payments:
           table.append([
                payment.date and Paragraph(payment.date.strftime(line_item_date_format), table_item_style),
                payment.description and Paragraph(payment.description, table_item_style),
                Paragraph(payment.display_total, table_item_style_right)
           ])
        
        table.append([
            Paragraph("Total Payments", table_total_style),
            None,
            Paragraph("${:0.2f}".format(self.invoice.payment_total*-1), table_total_style)
        ])
        
        
        table_item = Table(table, colWidths = [1*inch, 5*inch, 1*inch])
        table_item.setStyle(table_style)
        
        yield table_item
     
    def get_credit_story_items(self):
        if not self.credits:
            return []
        
        yield Paragraph("Credits", table_name_style)
        
        table = [[
            Paragraph("Date", table_header_style), 
            Paragraph("Description", table_header_style), 
            Paragraph("Amount", table_header_style_right)
        ]]
        
        table_style = []
        table_style.extend(default_table_style)
        
        for credit in self.credits:
           table.append([
                credit.date and Paragraph(credit.date.strftime(line_item_date_format), table_item_style),
                credit.description and Paragraph(credit.description, table_item_style),
                Paragraph(credit.display_total, table_item_style_right)
           ])
        
        table.append([
            Paragraph("Total Credits", table_total_style),
            None,
            Paragraph("${:0.2f}".format(self.invoice.credit_total*-1), table_total_style)
        ])
        
        
        table_item = Table(table, colWidths = [1*inch, 5*inch, 1*inch])
        table_item.setStyle(table_style)
        
        yield table_item
     
            
    def build_pdf(self, output):
        def onFirstPage(canvas, doc):
            self.on_first_page(canvas)
        
        def onLaterPages(canvas, doc):
            canvas.saveState()
            canvas.setFont('HelveticaNeue-Bold', 13)
            canvas.setStrokeColor(accent_color)
            canvas.setFillColor(accent_color)
    
            canvas.line(.75 * inch, (11-.5)*inch, 7.75*inch, (11-.5)*inch)
            canvas.drawString(.75 * inch, (11-.75) * inch, self.invoice.vendor.name)

            canvas.setFont('HelveticaNeue-Light', 16)
            canvas.setFillColor(colors.black)        
            canvas.drawString(.75 * inch, 10 * inch, "INVOICE")
    
            #Client area
            canvas.setFont('HelveticaNeue-Bold', 10)
            canvas.drawString(4.25 * inch, 10.25 * inch, self.invoice.client.name)
            canvas.setFont('HelveticaNeue-Light', 10)
            canvas.drawString(4.25 * inch, 10.1 * inch, "Invoice number: {:} (continued)".format(self.invoice.id))
            
            canvas.setStrokeColor(colors.grey)
            canvas.line(.75 * inch, 9.9*inch, 7.75*inch, 9.9*inch)
            
            canvas.restoreState()
        
        if self.pdf_includes:
            #Holding object so I can merge it with the PDFs later
            reportlab_output = BytesIO()
        else:
            #Output to whatever we were given
            reportlab_output = output
            
        doc = SimpleDocTemplate(reportlab_output, leftMargin = .75 * inch, rightMargin = .75 * inch, pagesize=(8.5*inch, 11*inch), topMargin=1.25*inch)
        story = list(self.get_story())
        doc.build(story, onFirstPage=onFirstPage, onLaterPages=onLaterPages)
        
        if self.pdf_includes:
            reader = PdfFileReader(reportlab_output)
            merger = PdfFileMerger()
            merger.append(reader)
            
            for pdf_include in self.pdf_includes:
                merger.append(fileobj = pdf_include.pdf)
            
            merger.write(output)
        
    def get_total_items(self):
        table = []
        
        TOTAL_MAPPING = (
            ('Hourly Services', self.invoice.hourly_services_total, 1),
            ('Fixed Services', self.invoice.fixed_services_total, 1),
            ('Expenses', self.invoice.expense_total, 1),
            ('Payments', self.invoice.payment_total, -1),
            ('Credits', self.invoice.credit_total, -1),
        )
        
        for description, amount, multiplier in TOTAL_MAPPING:
            if amount:
                table.append([
                    Paragraph(description, table_total_style),
                    Paragraph("${:0.2f}".format(amount*multiplier), table_total_style)
                ])
        
        table.append([
            Paragraph("Invoice Total", table_total_style),
            Paragraph("${:0.2f}".format(self.invoice.total), table_total_style),
        ])
        
        table_item = Table(table, colWidths = [6*inch, 1*inch])
        table_style = [('LINEABOVE', (0, -1), (1, -1), 1, colors.black)]
        
        table_item.setStyle(table_style)
        
        yield table_item
        
    def get_story(self):
        first_page_buffer = self.on_first_page()

        yield Spacer(1, first_page_buffer - 1.15 * inch)
        
        item_lists = map(list, [self.get_hourly_story_items(), 
                      self.get_fixed_service_story_items(),
                      self.get_expense_story_items(),
                      self.get_credit_story_items(),
                      self.get_payment_story_items(),
                      self.get_total_items()])
        
        # Remove the empty lists
        item_lists = [l for l in item_lists if len(l) > 0]
        item_count = len(item_lists)
        
        for i, item_list in enumerate(map(list, item_lists)):
            
            if i == 0: # First item
                for item in item_list:
                    yield item
                
                yield Spacer(1, .5*inch)
            
            elif i == item_count - 1: # Last item
                yield KeepTogether(item_list)
            
            else: # Middle items
                yield KeepTogether(item_list + [Spacer(1, .5*inch)])
            