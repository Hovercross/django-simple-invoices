from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from invoices.models import Invoice
from invoices.lib.pdf_generator import InvoicePDFBuilder

@login_required
def invoice(request, id):
    invoice = Invoice.objects.get(pk=id)
    builder = InvoicePDFBuilder(invoice)
    
    response = HttpResponse(content_type='application/pdf')
    
    builder.build_pdf(response)
    
    return response