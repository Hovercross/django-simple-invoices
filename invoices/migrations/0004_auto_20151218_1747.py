# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_invoice_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='credit_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='expense_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='fixed_services_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='hourly_services_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='payment_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
            preserve_default=False,
        ),
    ]
