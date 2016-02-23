from django.conf.urls import include, url

import invoices.views

urlpatterns = [
    url(r'^invoice/(?P<uuid>[0-9a-z\-]+)/$', invoices.views.invoice, name='invoice-pdf')
]
