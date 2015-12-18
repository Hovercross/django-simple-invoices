from django.contrib import admin

from invoices.models import LineItem, Client, Invoice, HourlyService, FixedService, Expense, Payment, RelatedPDF, Credit

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

# Register your models here.
class ClientAdmin(admin.ModelAdmin):
    pass
    
class HourlyServiceInline(InlineBase):
    model = HourlyService
    
    fields = ['date', 'description', 'location', 'hours', 'rate', 'display_total']
    readonly_fields = ['display_total']

class FixedServiceInline(InlineBase):
    model = FixedService
    
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class ExpenseInline(InlineBase):
    model = Expense
    
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class PaymentInline(InlineBase):
    model = Payment
    
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class CreditInline(InlineBase):
    model = Credit
        
    fields = ['date', 'description', 'amount', 'display_total']
    readonly_fields = ['display_total']

class RelatedPDFInline(InlineBase):
    model = RelatedPDF

class InvoiceAdmin(admin.ModelAdmin):
    def invoice(self, o):
        return "Invoice {}".format(o.id)
    
    fields = ['client', 'date', 'total']
    readonly_fields = ['total']
    
    actions = ['update_totals']
    
    inlines = [HourlyServiceInline, FixedServiceInline, ExpenseInline, PaymentInline, CreditInline, RelatedPDFInline]
    list_filter = ['client__name', PaidListFilter]
    list_display = ('__str__', 'client', 'date', 'total_charges', 'total_credits', 'total')
    
    
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


admin.site.register(Client, ClientAdmin)    
admin.site.register(Invoice, InvoiceAdmin)