#!/usr/bin/python

from datetime import date
from decimal import Decimal

from django.db.models import Sum

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from invoices.models import HourlyService, FixedService, Expense, Payment, Credit
from invoices.lib.pdf_styles import accent_color, line_item_date_format, table_item_style, table_item_style_right, table_header_style, table_header_style_right, table_name_style, default_table_style, table_total_style

class InvoicePDFBuilder(object):
    def __init__(self, invoice):
        self.invoice = invoice
        
        self.hourly_services = HourlyService.objects.filter(invoice=invoice).order_by('date')
        self.fixed_services = FixedService.objects.filter(invoice=invoice).order_by('date')
        self.expenses = Expense.objects.filter(invoice=invoice).order_by('date')
        self.payments = Payment.objects.filter(invoice=invoice).order_by('date')
        self.credits = Credit.objects.filter(invoice=invoice).order_by('date')
        
        #Will be calculated by get_hourly_story_items so the math between uniform and non-uniform rates are consistent
        self.hourly_items_total = None
        
        self.fixed_services_total = self.fixed_services.aggregate(Sum('total'))['total__sum']
        self.expense_total = self.expenses.aggregate(Sum('total'))['total__sum']
        self.payment_total = self.payments.aggregate(Sum('total'))['total__sum']
        self.credit_total = self.credits.aggregate(Sum('total'))['total__sum']
        
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
            print(uniform_rate_value)
            
        if not uniform_rate:
            self.hourly_items_total = Decimal(0)
        else:
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
                
                self.hourly_items_total += hourly_item.total
                
            else:
                table.append([
                    hourly_service.date and Paragraph(hourly_service.date.strftime(line_item_date_format), table_item_style) or None,
                    hourly_service.location and Paragraph(hourly_service.location, table_item_style) or None,
                    hourly_service.description and Paragraph(hourly_service.description, table_item_style) or None,
                    hourly_service.hours and Paragraph("{:0.3f}".format(hourly_service.hours), table_item_style_right) or None,
                ])
                
                total_hours += hourly_service.hours
        
        if uniform_rate:
            self.hourly_items_total = Decimal(round(total_hours * uniform_rate_value, 2))
        
        table_style = []
        table_style.extend(default_table_style)
        
        if uniform_rate:
            table.append([
                Paragraph("Total Hours", table_total_style),
                None,
                None,
                Paragraph("${:.2f}".format(total_hours), table_total_style)
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
                Paragraph("${:.2f}".format(self.hourly_items_total), table_total_style)])
            
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
                Paragraph("${:.2f}".format(self.hourly_items_total), table_total_style)])
            
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
            Paragraph("${:0.2f}".format(self.fixed_services_total), table_total_style)
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
            Paragraph("${:0.2f}".format(self.expense_total), table_total_style)
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
            Paragraph("${:0.2f}".format(self.payment_total*-1), table_total_style)
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
            Paragraph("${:0.2f}".format(self.credit_total*-1), table_total_style)
        ])
        
        
        table_item = Table(table, colWidths = [1*inch, 5*inch, 1*inch])
        table_item.setStyle(table_style)
        
        yield table_item
     
            
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
            
            addresses_bottom = (9.05 - num_address_lines*.15) * inch
            other_bottom = 8.85 * inch
            
            top_section_bottom = min(addresses_bottom, other_bottom)
            
            canvas.setStrokeColor(colors.grey)
            canvas.line(.75 * inch, top_section_bottom - .15*inch, 7.75*inch, top_section_bottom - .15*inch)
            
            canvas.setAuthor("Adam M Peacock")
            canvas.setSubject("Invoice")
            canvas.setTitle("Invoice {}".format(self.invoice.id))
            
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
            canvas.drawString(4.25 * inch, 10.1 * inch, "Invoice number: {:} (continued)".format(self.invoice.id))
            
            canvas.setStrokeColor(colors.grey)
            canvas.line(.75 * inch, 9.9*inch, 7.75*inch, 9.9*inch)
            
            canvas.restoreState()
        
        doc = SimpleDocTemplate(output, leftMargin = .75 * inch, rightMargin = .75 * inch, pagesize=(8.5*inch, 11*inch), topMargin=1.25*inch)
        
        story = list(self.get_story())
        doc.build(story, onFirstPage=onFirstPage, onLaterPages=onLaterPages)
        
    def get_total_items(self):
        table = []
        
        TOTAL_MAPPING = (
            ('Hourly Services', self.hourly_items_total, 1),
            ('Fixed Services', self.fixed_services_total, 1),
            ('Expenses', self.expense_total, 1),
            ('Payments', self.payment_total, 1),
            ('Credits', self.credit_total, 1),
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
        yield Spacer(1, 1.5 * inch)
        
        hourly_story_items = list(self.get_hourly_story_items())
        if hourly_story_items:
            yield KeepTogether(hourly_story_items + [Spacer(1, .5*inch)])
            
        
        fixed_service_items = list(self.get_fixed_service_story_items())
        if fixed_service_items:
            yield KeepTogether(fixed_service_items + [Spacer(1, .5*inch)])
        
        expense_items = list(self.get_expense_story_items())
        if expense_items:
            yield KeepTogether(expense_items + [Spacer(1, .5*inch)])
    
        credit_items = list(self.get_credit_story_items())
        if credit_items:
            yield KeepTogether(credit_items + [Spacer(1, .5*inch)])
        
        payment_items = list(self.get_payment_story_items())
        if payment_items:
            yield KeepTogether(payment_items + [Spacer(1, .5*inch)])
        
        total_items = list(self.get_total_items())
        if total_items:
            yield KeepTogether(total_items)
        