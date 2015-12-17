from django.shortcuts import render
from django.http import HttpResponse

from invoices.models import Invoice
from invoices import pdf_generator

# Create your views here.
def invoice(request, id):
    invoice = Invoice.objects.get(pk=id)
    
    response = HttpResponse(content_type='application/pdf')
    
    pdf_generator.build_invoice_pdf(invoice, response)
    
    return response