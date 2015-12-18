# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0002_auto_20151218_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='total_charges',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
        migrations.AddField(
            model_name='invoice',
            name='total_credits',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
    ]
