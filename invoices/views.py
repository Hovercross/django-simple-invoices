from django.shortcuts import render
from django.http import HttpResponse

from invoices.models import Invoice
from invoices.lib.pdf_generator import InvoicePDFBuilder

# Create your views here.
def invoice(request, id):
    invoice = Invoice.objects.get(pk=id)
    builder = InvoicePDFBuilder(invoice)
    
    response = HttpResponse(content_type='application/pdf')
    
    builder.build_pdf(response)
    
    return response