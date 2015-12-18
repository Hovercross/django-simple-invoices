# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='credit_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='expense_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='fixed_services_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='hourly_services_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='total',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=20),
        ),
    ]
