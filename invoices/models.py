import os
from decimal import Decimal

from django.db import models
from django.core.urlresolvers import reverse

from polymorphic.models import PolymorphicModel


def uuidUpload(instance, filename):
    name, ext = os.path.splitext(filename)
    
    newName = "{}{}".format(uuid.uuid4().hex, ext)
    
    return "by-uuid/{}".format(newName)
    
# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=50)
    address = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Invoice(models.Model):
    client = models.ForeignKey(Client)
    date = models.DateField(blank=True, null=True)
    finalized = models.BooleanField(default=False)
    
    hourly_services_total = models.DecimalField(max_digits=20, decimal_places=2)
    fixed_services_total = models.DecimalField(max_digits=20, decimal_places=2)
    expense_total = models.DecimalField(max_digits=20, decimal_places=2)
    payment_total = models.DecimalField(max_digits=20, decimal_places=2)
    credit_total = models.DecimalField(max_digits=20, decimal_places=2)
    
    total = models.DecimalField(max_digits=20, decimal_places=2)
    
    ordering = ['client__name', 'date']
    
    def update_totals(self):
        #Special case for hourly to make sure we are using the same computation methods throughout
        hourly_services = HourlyService.objects.filter(invoice=self)
        
        rates = set()
        total_hours = Decimal()
        total_dollars = Decimal()
        
        #Track both total hours and total dollars, along with the seen rates. We'll decide what to do at the end.
        for hourly_service in hourly_services:
            rates.add(hourly_service.rate)
            total_hours += hourly_service.hours
            total_dollars += hourly_service.total
        
        if len(rates) == 0:
            self.hourly_services_total = 0
        elif len(rates) == 1:
            #Aggregated hours
            rate = rates.pop()
            self.hourly_services_total = round(round(total_hours, 3) * rate, 2)
        else:
            self.hourly_services_total = total_dollars
        
        MAPPING = [
            ('fixed_services_total', FixedService),
            ('expense_total', Expense),
            ('payment_total', Payment),
            ('credit_total', Credit)
        ]
        
        for attr, C in MAPPING:
            type_total = C.objects.filter(invoice=self).aggregate(models.Sum('total'))['total__sum']
            if type_total == None:
                type_total = 0
                
            setattr(self, attr, type_total)
        
        ATTRS = ['hourly_services_total', 'fixed_services_total', 'expense_total', 'payment_total', 'credit_total']
        
        self.total = sum([getattr(self, attr) for attr in ATTRS])
    
    def get_absolute_url(self):
        return reverse('invoices.views.invoice', kwargs={'id': self.id})
    
    def __str__(self):
        return "{id} - {client}".format(id=self.id, client=self.client)

class DisplayTotalMixin(object):
    @property
    def display_total(self):
        if self.total:
            return "${:0.2f}".format(self.total)
        
        return "-"

class ReverseDisplayTotalMixin(object):
    @property
    def display_total(self):
        if self.total:
            return "${:0.2f}".format(self.total * -1)
        
        return "-"
    
class LineItem(PolymorphicModel):    
    invoice = models.ForeignKey(Invoice)
    date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    
    total = models.DecimalField(max_digits=20, decimal_places=2)
    
    def __str__(self):
        return self.description

class HourlyService(LineItem, DisplayTotalMixin):
    location = models.CharField(max_length=255, blank=True, null=True)
    hours = models.DecimalField(max_digits=11, decimal_places=3)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total = self.hours * self.rate
        super().save(*args, **kwargs)
    
class FixedService(LineItem, DisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.amount
        super().save(*args, **kwargs)
        
class Expense(LineItem, DisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total = self.amount
        super().save(*args, **kwargs)
    
class Payment(LineItem, ReverseDisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total = self.amount * -1
        super().save(*args, **kwargs)

class Credit(LineItem, ReverseDisplayTotalMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total = self.amount * -1
        super().save(*args, **kwargs)
        
class RelatedPDF(models.Model):
    invoice = models.ForeignKey(Invoice)
    pdf = models.FileField(upload_to=uuidUpload, verbose_name="PDF")
    
    #TODO: Validate that the document is a PDF