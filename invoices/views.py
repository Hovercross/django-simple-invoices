from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from invoices.models import Invoice, Client, HourlyService
from invoices.lib.pdf_generator import InvoicePDFBuilder


def get_monday(date):
    return date - timedelta(days=date.weekday())


def get_previous_day_of_week(date, dow):
    # Naive implementation
    while date.weekday() != dow:
        date = date - timedelta(days=1)

    return date


@login_required
def client_weekly_hours(request, client_id):
    client = get_object_or_404(Client, pk=client_id)

    hourly_services = HourlyService.objects.filter(invoice__client=client)

    week_hours = {}

    for service in hourly_services:
        if not service.date:
            continue

        sunday = get_previous_day_of_week(service.date, 6)

        if sunday not in week_hours:
            week_hours[sunday] = timedelta()
        week_hours[sunday] += service.duration

    return HttpResponse(
        "\n".join(
            [
                "{week:}: {hours:}".format(
                    week=sunday.strftime("%Y-%m-%d"), hours=week_hours[sunday]
                )
                for sunday in sorted(week_hours.keys())
            ]
        ),
        content_type="text/plain",
    )


@login_required
def invoice_private(request, id):
    invoice = get_object_or_404(Invoice, pk=id)

    filename = "Invoice {id:} - {vendor:} - {client:}.pdf".format(
        id=invoice.id, client=invoice.client.name, vendor=invoice.vendor.name
    )

    builder = InvoicePDFBuilder(invoice)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="{}"'.format(filename)
    builder.build_pdf(response)

    return response


def invoice_public(request, uuid):
    invoice = get_object_or_404(Invoice, uuid=uuid)

    filename = "Invoice {id:} - {vendor:} - {client:}.pdf".format(
        id=invoice.id, client=invoice.client.name, vendor=invoice.vendor.name
    )

    if not invoice.public:
        return HttpResponseForbidden("Invoice is not public")

    builder = InvoicePDFBuilder(invoice)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="{}"'.format(filename)

    builder.build_pdf(response)

    return response
