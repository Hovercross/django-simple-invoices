from django.urls import path

import invoices.views

urlpatterns = [
    path(
        "invoice/public/<uuid:uuid>/",
        invoices.views.invoice_public,
        name="invoice-pdf",
    ),
    path(
        "invoice/private/<int:id>/",
        invoices.views.invoice_private,
        name="invoice-pdf",
    ),
    path(
        "client/private/hours/<int:client_id>/",
        invoices.views.client_weekly_hours,
        name="client-hours",
    ),
]
