# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_default_vendor(apps, schema_editor):
    Vendor = apps.get_model("invoices", "Vendor")
    Vendor(name="Default").save()

def delete_default_vendor(apps, schema_editor):
    Vendor.objects.get(name="Default").delete()
    
class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0005_vendor'),
    ]

    operations = [
        migrations.RunPython(create_default_vendor, delete_default_vendor)
    ]
