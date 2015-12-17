import os

from decimal import Decimal

from django.db import models

from polymorphic.models import PolymorphicModel

from invoices.managers import InvoiceManager

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
    
    objects = InvoiceManager()
    
    ordering = ['client__name', 'date']
    
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