# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def set_default_vendor(apps, schema_editor):
    Vendor = apps.get_model("invoices", "Vendor")
    Invoice = apps.get_model("invoices", "Invoice")
    
    default = Vendor.objects.get(name="Default")
    
    Invoice.objects.update(vendor=default)

class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0007_invoice_vendor'),
    ]

    operations = [
        migrations.RunPython(set_default_vendor, migrations.RunPython.noop),
        
        migrations.AlterField(
            model_name='invoice',
            name='vendor',
            field=models.ForeignKey(to='invoices.Vendor'),
        ),
    ]
