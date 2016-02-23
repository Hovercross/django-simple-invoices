from django.contrib import admin

from adminsortable.admin import SortableStackedInline, NonSortableParentAdmin, SortableTabularInline

from invoices.models import Client, Vendor, Invoice, HourlyService, FixedService, Expense, Payment, RelatedPDF, Credit

class PaidListFilter(admin.SimpleListFilter):
    title = "paid"
    
    parameter_name = "paid"
    
    def lookups(self, request, model_admin):
        return (('paid', 'Paid'), ('unpaid', 'Unpaid'))
    
    def queryset(self, request, queryset):
        if self.value() == 'paid':
            return queryset.filter(total = 0)
                    
        elif self.value() == 'unpaid':
            return queryset.exclude(total = 0)
        


class InlineBase(admin.TabularInline):
    extra = 0

class SortableInlineBase(SortableTabularInline):
    extra = 0

# Register your models here.
class ClientAdmin(admin.ModelAdmin):
    pass
    
class HourlyServiceInline(SortableInlineBase):
    model = HourlyService
    
    fields = ['date', 'description', 'location', 'hours', 'rate', 'display_total']
    readonly_fields = ['display_total']

class FixedServiceInline(SortableInlineBase):
    model = FixedService
    
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class ExpenseInline(SortableInlineBase):
    model = Expense
    
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class PaymentInline(SortableInlineBase):
    model = Payment
    
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class CreditInline(SortableInlineBase):
    model = Credit
        
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class RelatedPDFInline(SortableInlineBase):
    model = RelatedPDF

class InvoiceAdmin(NonSortableParentAdmin):
    def invoice(self, o):
        return "Invoice {}".format(o.id)
    
    fields = ['client', 'vendor', 'date', 'description', 'total', 'public']
    readonly_fields = ['total']
    
    actions = ['update_totals']
    
    inlines = [HourlyServiceInline, FixedServiceInline, ExpenseInline, PaymentInline, CreditInline, RelatedPDFInline]
    list_filter = ['vendor__name', 'client__name', PaidListFilter]
    list_display = ('__str__', 'vendor', 'client', 'date', 'description', 'total')
    
    def update_totals(self, request, queryset):
        for invoice in queryset:
            invoice.update_totals()
            invoice.save()
    
    update_totals.short_description = "Update the totals for selected invoices"
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        invoice = form.instance
        invoice.update_totals()
        invoice.save()
    
    change_form_template_extends = 'admin/invoices/invoice/change_form.html'
    
class VendorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Client, ClientAdmin)    
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Vendor, VendorAdmin)