from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from invoices.models import Invoice
from invoices.lib.pdf_generator import InvoicePDFBuilder

@login_required
def invoice_private(request, id):
    invoice = get_object_or_404(Invoice, pk=id)
    
    builder = InvoicePDFBuilder(invoice)
    response = HttpResponse(content_type='application/pdf')
    builder.build_pdf(response)
    
    return response

def invoice_public(request, uuid):
    invoice = get_object_or_404(Invoice, uuid=uuid)
    
    if not invoice.public:
        return HttpResponseForbidden("Invoice is not public")
    
    builder = InvoicePDFBuilder(invoice)
    
    response = HttpResponse(content_type='application/pdf')
    
    builder.build_pdf(response)
    
    return response