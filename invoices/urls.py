from django.conf.urls import include, url

import invoices.views

urlpatterns = [
    url(r'^invoice/public/(?P<uuid>[0-9a-z\-]+)/$', invoices.views.invoice_public, name='invoice-pdf'),
    url(r'^invoice/private/(?P<id>[0-9]+)/$', invoices.views.invoice_private, name='invoice-pdf')
]
