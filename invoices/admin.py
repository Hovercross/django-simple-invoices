from datetime import date
from collections import defaultdict
from io import StringIO
from decimal import Decimal

from django.contrib import admin
from django.http import HttpResponse

from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase

from invoices.models import (
    Client,
    Vendor,
    Invoice,
    HourlyService,
    FixedService,
    Expense,
    Payment,
    RelatedPDF,
    Credit,
)


class PaidListFilter(admin.SimpleListFilter):
    title = "paid"

    parameter_name = "paid"

    def lookups(self, request, model_admin):
        return (("paid", "Paid"), ("unpaid", "Unpaid"))

    def queryset(self, request, queryset):
        if self.value() == "paid":
            return queryset.filter(total=0)

        elif self.value() == "unpaid":
            return queryset.exclude(total=0)


class ClientAdmin(admin.ModelAdmin):
    pass


class InlineBase(SortableInlineAdminMixin, admin.StackedInline):
    extra = 0


class HourlyServiceInline(InlineBase):
    model = HourlyService

    fields = ["date", "description", "location", "duration", "rate", "display_total"]
    readonly_fields = ["display_total"]


class FixedServiceInline(InlineBase):
    model = FixedService

    fields = ["date", "description", "amount", "display_total"]
    readonly_fields = ["display_total"]


class ExpenseInline(InlineBase):
    model = Expense

    fields = ["date", "description", "amount", "display_total"]
    readonly_fields = ["display_total"]


class PaymentInline(InlineBase):
    model = Payment

    fields = ["date", "description", "amount", "display_total"]
    readonly_fields = ["display_total"]


class CreditInline(InlineBase):
    model = Credit

    fields = ["date", "description", "amount", "display_total"]
    readonly_fields = ["display_total"]


class RelatedPDFInline(InlineBase):
    model = RelatedPDF


class InvoiceAdmin(SortableAdminBase, admin.ModelAdmin):
    def invoice(self, o):
        return "Invoice {}".format(o.id)

    fields = ["client", "vendor", "date", "description", "total", "public"]
    readonly_fields = ["total"]

    actions = ["update_totals", "assume_payment", "tax_report"]

    inlines = [
        HourlyServiceInline,
        FixedServiceInline,
        ExpenseInline,
        PaymentInline,
        CreditInline,
        RelatedPDFInline,
    ]
    list_filter = ["vendor__name", "client__name", "date", PaidListFilter]
    list_display = ("__str__", "vendor", "client", "date", "description", "total")

    def update_totals(self, request, queryset):
        for invoice in queryset:
            invoice.update_totals()
            invoice.save()

    update_totals.short_description = "Update the totals for selected invoices"

    def assume_payment(self, request, queryset):
        for invoice in queryset.filter(total__gt=0):
            print(invoice, invoice.total)

            Credit.objects.create(
                invoice=invoice,
                date=date.today(),
                description="Credit to clear balance",
                amount=invoice.total,
            )
            invoice.update_totals()
            invoice.save()

    assume_payment.short_description = "Clear total via credit"

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        invoice = form.instance
        invoice.update_totals()
        invoice.save()

    change_form_template_extends = "admin/invoices/invoice/change_form.html"

    @admin.decorators.action(description="Tax report")
    def tax_report(self, request, qs):
        payment_by_year = defaultdict(list)

        payments = Payment.objects.filter(invoice__in=qs).order_by("date")
        for obj in payments:
            payment_by_year[obj.date.year].append(obj)

        out = StringIO()

        for year, payments in payment_by_year.items():
            by_client_totals = defaultdict(Decimal)
            out.write(f"{year} Payments:\n")

            for payment in payments:
                out.write(
                    f"\t{payment.date} - {payment.invoice.client} - {payment.amount}\n"
                )
                by_client_totals[payment.invoice.client] += payment.amount

            out.write(f"\n{year} Totals:\n")
            for client, total in sorted(by_client_totals.items(), key=lambda t: t[1]):
                out.write(f"\t{client.name}: {total}\n")

            out.write("\n")

        resp = HttpResponse(content=out.getvalue())
        resp["content-type"] = "text/plain"

        return resp


class VendorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Client, ClientAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Vendor, VendorAdmin)
